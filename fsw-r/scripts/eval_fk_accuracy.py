"""Measures the accuracy of the joint-angle round trip:

    real landmarks (3d-hands-benchmark)  ->  flexion/abduction angles
                                              (data/hand_joint_poses.json)
                                          ->  forward kinematics
                                              (export/forward_kinematics.py)
                                          ->  reconstructed landmarks

against the SAME real landmarks the angles were originally measured from.
This answers this evaluation task's Câu 1 (Part 0): how much does the round
trip lose? A MEASURING script -- it does not clamp, retune, or change
``hand_joint_poses.json``/``forward_kinematics.py``/``bone_lengths.py``.

**Ground truth**: ``data/external/hands.npy`` (fetch via
``scripts/fetch_ground_truth.py`` first), shape ``(48, 261, 6, 21, 3)`` --
48 crops x 261 Category 1 base symbols x 6 fills x 21 MediaPipe landmarks
x xyz. Derived from ``3d-hands-benchmark`` v0.10.3 (the SAME source
``hand_joint_poses.json`` itself came from), packaged by
``sign-language-processing/synthetic-signwriting`` -- see
``fetch_ground_truth.py``'s docstring and PROGRESS.md's evaluation-layer
entry for the full citation/license.

**Subset selection and ground-truth construction exactly replicate
``synthetic_signwriting/hands/hands.py``'s real, verified source** (fetched
and read directly, not paraphrased from the brief): crops ``[16:32]`` ("good"
crops), fills ``[:3]`` (the 3 Wall Plane fills, 0-2 -- confirms this
project's own fill encoding: fill%3 selects Palm/Side/Back, fill//3 selects
Wall/Floor plane), then normalize (``validation/normalization.py``) and take
the MEDIAN across crop AND fill combined (48 samples per base, not per
(base, fill) -- matching how ``hand_joint_poses.json`` itself is keyed,
base_hex only, since normalization removes the whole-hand orientation
differences fill represents).

Run:  python scripts/eval_fk_accuracy.py
  (needs data/external/hands.npy -- run fetch_ground_truth.py first)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray
from pose_format.utils.holistic import HAND_POINTS
from scipy.spatial.transform import Rotation

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of, valid_combinations_for
from fsw_r.core.pose_table import HAND_NAME_TABLE, HAND_POSE_TABLE
from fsw_r.core.types import FingerPose, HandJointPose, HandSide, JointAngle, ThumbPose
from fsw_r.export.forward_kinematics import hand_to_landmarks
from fsw_r.validation.normalization import landmarks_dict_to_array, normalize_landmarks

GROUND_TRUTH_PATH = Path(__file__).resolve().parent.parent / "data" / "external" / "hands.npy"
REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"

FIRST_BASE_HEX = 0x100
BASE_COUNT = 261  # Category 1: 0x100-0x204
CROP_SLICE = slice(16, 32)  # "good" crops, per hands.py
FILL_SLICE = slice(0, 3)  # Wall Plane fills (0, 1, 2), per hands.py

_FINGER_NAMES = ("thumb", "index", "middle", "ring", "pinky")
_FINGER_LANDMARK_PREFIX = {
    "thumb": "THUMB",
    "index": "INDEX_FINGER",
    "middle": "MIDDLE_FINGER",
    "ring": "RING_FINGER",
    "pinky": "PINKY",
}
# All 20 non-WRIST landmark suffixes that actually appear in HAND_POINTS:
# MCP/PIP/DIP/TIP for the 4 fingers, CMC/MCP/IP/TIP for the thumb (a
# different joint chain -- see forward_kinematics.py). TIP is the endpoint,
# not a joint, but still a landmark, so still reported.
_JOINT_TYPE_SUFFIXES = ("CMC", "MCP", "PIP", "DIP", "IP", "TIP")


# ---------------------------------------------------------------------------
# D1/A2/A3: ground truth construction (pure function of the raw array, so
# this is testable with a small fake array -- no 38 MB file needed for CI).
# ---------------------------------------------------------------------------


def select_subset(raw: NDArray[np.float64]) -> NDArray[np.float64]:
    """``raw``: shape ``(F, B, V, 21, 3)`` -> ``(16, B, 3, 21, 3)``, exactly
    ``hands.py``'s ``hands[16:32]`` + ``hands[:, :, :3]``."""
    return raw[CROP_SLICE, :, FILL_SLICE]


def ground_truth_median(subset: NDArray[np.float64]) -> NDArray[np.float64]:
    """``subset``: shape ``(16, B, 3, 21, 3)`` -> ``(B, 21, 3)``, one
    normalized median pose per base -- exactly ``hands.py``'s
    ``load_hands_3d()`` (crop x fill merged into one 48-sample median pool
    per base, see module docstring for why)."""
    crops, bases, fills, points, dims = subset.shape
    flat = subset.reshape(-1, points, dims)
    flat_normalized = normalize_landmarks(flat)
    normalized = flat_normalized.reshape(crops, bases, fills, points, dims)
    merged = normalized.transpose((0, 2, 1, 3, 4)).reshape(crops * fills, bases, points, dims)
    result: NDArray[np.float64] = np.median(merged, axis=0)
    return result


def verify_index_to_base_hex_mapping(base_count: int = BASE_COUNT) -> list[str]:
    """A3: ``base_hex = 0x100 + hand_index``. Cross-checks the 3 Wall Plane
    fills (0, 1, 2) actually used by ``ground_truth_median`` against
    ``iswa_valid_combinations.json`` for every base -- returns a list of
    human-readable warnings for any invalid (base, fill) pair found (empty
    list if all valid). Does NOT change how the ground truth is built
    (matching hands.py exactly is the point, see module docstring) -- this
    only reports."""
    warnings = []
    for hand_index in range(base_count):
        base_hex = FIRST_BASE_HEX + hand_index
        valid_fills = valid_combinations_for(base_hex).fills
        for fill in (0, 1, 2):
            if fill not in valid_fills:
                warnings.append(
                    f"base 0x{base_hex:03x} ({symbol_id_of(base_hex)}): fill={fill} used by "
                    f"hands.py's ground truth is NOT in ISWA's valid_fills={sorted(valid_fills)}"
                )
    return warnings


# ---------------------------------------------------------------------------
# D2: this project's FK prediction for one base symbol.
# ---------------------------------------------------------------------------


def predict_landmarks(pose: HandJointPose) -> NDArray[np.float64]:
    landmarks = hand_to_landmarks(pose, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    return normalize_landmarks(landmarks_dict_to_array(landmarks))


# ---------------------------------------------------------------------------
# C1: error measurement.
# ---------------------------------------------------------------------------


def per_landmark_error(predicted: NDArray[np.float64], ground_truth: NDArray[np.float64]) -> NDArray[np.float64]:
    """``predicted``/``ground_truth``: shape ``(..., 21, 3)`` -> per-landmark
    Euclidean distance, shape ``(..., 21)``."""
    result: NDArray[np.float64] = np.linalg.norm(predicted - ground_truth, axis=-1)
    return result


class _FingerJoint(NamedTuple):
    landmark_index: int
    finger: str
    joint_type: str  # MCP/PIP/DIP/TIP


def landmark_taxonomy() -> list[_FingerJoint]:
    """Every one of the 20 non-WRIST landmarks, tagged with which finger
    and joint type it is -- derived from HAND_POINTS names, not a
    hardcoded parallel list (same reasoning as forward_kinematics.py's
    own name parsing)."""
    taxonomy = []
    for i, name in enumerate(HAND_POINTS):
        if name == "WRIST":
            continue
        for finger, prefix in _FINGER_LANDMARK_PREFIX.items():
            if name.startswith(prefix + "_"):
                joint_type = name[len(prefix) + 1 :]
                taxonomy.append(_FingerJoint(i, finger, joint_type))
                break
    return taxonomy


# ---------------------------------------------------------------------------
# C2: baselines.
# ---------------------------------------------------------------------------


def _average_joint_angle(angles: list[JointAngle]) -> JointAngle:
    return JointAngle(
        flexion=float(np.mean([a.flexion for a in angles])),
        abduction=float(np.mean([a.abduction for a in angles])),
    )


def average_pose(poses: list[HandJointPose]) -> HandJointPose:
    """Element-wise mean of every one of the 15 joint angles across
    ``poses`` -- baseline 1 (C2): "one average pose for every symbol"."""

    def avg_finger(getter: object) -> FingerPose:
        return FingerPose(
            mcp=_average_joint_angle([getter(p).mcp for p in poses]),  # type: ignore[operator]
            pip=_average_joint_angle([getter(p).pip for p in poses]),  # type: ignore[operator]
            dip=_average_joint_angle([getter(p).dip for p in poses]),  # type: ignore[operator]
        )

    return HandJointPose(
        thumb=ThumbPose(
            cmc=_average_joint_angle([p.thumb.cmc for p in poses]),
            mcp=_average_joint_angle([p.thumb.mcp for p in poses]),
            ip=_average_joint_angle([p.thumb.ip for p in poses]),
        ),
        index=FingerPose(
            mcp=_average_joint_angle([p.index.mcp for p in poses]),
            pip=_average_joint_angle([p.index.pip for p in poses]),
            dip=_average_joint_angle([p.index.dip for p in poses]),
        ),
        middle=FingerPose(
            mcp=_average_joint_angle([p.middle.mcp for p in poses]),
            pip=_average_joint_angle([p.middle.pip for p in poses]),
            dip=_average_joint_angle([p.middle.dip for p in poses]),
        ),
        ring=FingerPose(
            mcp=_average_joint_angle([p.ring.mcp for p in poses]),
            pip=_average_joint_angle([p.ring.pip for p in poses]),
            dip=_average_joint_angle([p.ring.dip for p in poses]),
        ),
        pinky=FingerPose(
            mcp=_average_joint_angle([p.pinky.mcp for p in poses]),
            pip=_average_joint_angle([p.pinky.pip for p in poses]),
            dip=_average_joint_angle([p.pinky.dip for p in poses]),
        ),
    )


def group_of_base_hex(base_hex: int) -> int:
    """1-based Category 1 group number (1-10) -- local re-derivation
    avoiding a dependency on core/iswa_data.py's category-agnostic
    group_of() only to keep this a self-contained, easily-testable
    function; the boundary VALUES still come from GROUP_START itself, not
    hardcoded."""
    for group in range(1, 11):
        if GROUP_START[group - 1] <= base_hex < GROUP_START[group]:
            return group
    raise ValueError(f"0x{base_hex:03x} is not in Category 1 (0x100-0x204)")  # pragma: no cover


# ---------------------------------------------------------------------------
# Report assembly.
# ---------------------------------------------------------------------------


def _percentiles(values: NDArray[np.float64]) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p75": float(np.percentile(values, 75)),
        "p95": float(np.percentile(values, 95)),
        "max": float(np.max(values)),
    }


def build_report(ground_truth: NDArray[np.float64], index_warnings: list[str]) -> dict[str, object]:
    """``ground_truth``: shape ``(261, 21, 3)``, normalized, one per base
    (index 0 = base 0x100). Returns the full JSON-serializable report."""
    base_hexes = [FIRST_BASE_HEX + i for i in range(BASE_COUNT)]
    poses = [HAND_POSE_TABLE[b] for b in base_hexes]
    predictions = np.stack([predict_landmarks(p) for p in poses])  # (261, 21, 3)

    errors = per_landmark_error(predictions, ground_truth)  # (261, 21)
    per_symbol_mpjpe = errors.mean(axis=1)  # (261,) -- includes WRIST (always ~0)

    taxonomy = landmark_taxonomy()
    finger_errors: dict[str, list[float]] = {f: [] for f in _FINGER_NAMES}
    joint_errors: dict[str, list[float]] = {j: [] for j in _JOINT_TYPE_SUFFIXES}
    for t in taxonomy:
        finger_errors[t.finger].extend(errors[:, t.landmark_index].tolist())
        joint_errors[t.joint_type].extend(errors[:, t.landmark_index].tolist())

    # C2 baseline 1: one average pose for all 261.
    baseline1_pose = average_pose(poses)
    baseline1_pred = predict_landmarks(baseline1_pose)
    baseline1_errors = per_landmark_error(np.broadcast_to(baseline1_pred, ground_truth.shape), ground_truth)

    # C2 baseline 2: one average pose per ISWA group (10 groups).
    groups = [group_of_base_hex(b) for b in base_hexes]
    baseline2_errors_list = []
    for group in range(1, 11):
        members = [p for p, g in zip(poses, groups) if g == group]
        group_pose = average_pose(members)
        group_pred = predict_landmarks(group_pose)
        member_gt = ground_truth[[i for i, g in enumerate(groups) if g == group]]
        baseline2_errors_list.append(per_landmark_error(np.broadcast_to(group_pred, member_gt.shape), member_gt))
    baseline2_errors = np.concatenate(baseline2_errors_list, axis=0)

    ranked = sorted(
        range(BASE_COUNT),
        key=lambda i: per_symbol_mpjpe[i],
    )
    worst = ranked[-20:][::-1]
    best = ranked[:20]

    def symbol_entry(i: int) -> dict[str, object]:
        base_hex = base_hexes[i]
        return {
            "base_hex": f"0x{base_hex:03x}",
            "symbol_id": symbol_id_of(base_hex),
            "name": HAND_NAME_TABLE.get(base_hex, "?"),
            "mpjpe": float(per_symbol_mpjpe[i]),
        }

    # C4: occlusion hypothesis -- expected order ring > pinky > middle > index.
    finger_mpjpe = {f: float(np.mean(v)) for f, v in finger_errors.items() if f != "thumb"}
    expected_order = ["ring", "pinky", "middle", "index"]
    observed_order = sorted(finger_mpjpe, key=lambda f: -finger_mpjpe[f])

    return {
        "_meta": {
            "ground_truth_source": (
                "3d-hands-benchmark v0.10.3 (MIT), packaged as hands.npy by "
                "sign-language-processing/synthetic-signwriting (MIT) -- see "
                "fetch_ground_truth.py"
            ),
            "normalization": "pose_format.utils.normalization_3d.PoseNormalizer, size=150 (see validation/normalization.py)",
            "base_count": BASE_COUNT,
            "generated_by": "scripts/eval_fk_accuracy.py",
        },
        "index_to_base_hex_verification": {
            "checked": BASE_COUNT * 3,
            "invalid_pairs_found": len(index_warnings),
            "warnings": index_warnings,
        },
        "mpjpe_overall": _percentiles(per_symbol_mpjpe),
        # Full per-symbol MPJPE (all 261, not just worst/best 20) -- lets
        # eval_anatomical.py compute a real correlation (C3's last
        # requirement) instead of guessing from a biased 40-symbol subset.
        "per_symbol_mpjpe": {f"0x{b:03x}": float(per_symbol_mpjpe[i]) for i, b in enumerate(base_hexes)},
        "mpjpe_by_finger": {f: _percentiles(np.array(v)) for f, v in finger_errors.items()},
        "mpjpe_by_joint_type": {j: _percentiles(np.array(v)) for j, v in joint_errors.items()},
        "baselines": {
            "fsw_r_261_poses": _percentiles(per_symbol_mpjpe),
            "average_pose_baseline": _percentiles(baseline1_errors.mean(axis=1)),
            "one_pose_per_group_baseline": _percentiles(baseline2_errors.mean(axis=1)),
        },
        "occlusion_hypothesis": {
            "expected_order_worst_to_best": expected_order,
            "observed_order_worst_to_best": observed_order,
            "matches": observed_order == expected_order,
            "finger_mpjpe": finger_mpjpe,
        },
        "worst_20": [symbol_entry(i) for i in worst],
        "best_20": [symbol_entry(i) for i in best],
    }


def render_markdown(report: dict[str, object]) -> str:
    def fmt(d: dict[str, float]) -> str:
        return f"mean={d['mean']:.2f} median={d['median']:.2f} p75={d['p75']:.2f} p95={d['p95']:.2f} max={d['max']:.2f}"

    def as_dict(value: object) -> dict[str, object]:
        assert isinstance(value, dict)
        return value

    def as_list(value: object) -> list[object]:
        assert isinstance(value, list)
        return value

    lines = ["# FK Accuracy Evaluation", ""]
    lines.append("## Overall MPJPE (normalized, size=150)")
    lines.append(fmt(as_dict(report["mpjpe_overall"])))  # type: ignore[arg-type]
    lines.append("")
    lines.append("## Baselines")
    for name, values in as_dict(report["baselines"]).items():
        lines.append(f"- **{name}**: {fmt(as_dict(values))}")  # type: ignore[arg-type]
    lines.append("")
    lines.append("## MPJPE by finger")
    for finger, values in as_dict(report["mpjpe_by_finger"]).items():
        lines.append(f"- **{finger}**: {fmt(as_dict(values))}")  # type: ignore[arg-type]
    lines.append("")
    lines.append("## MPJPE by joint type")
    for joint, values in as_dict(report["mpjpe_by_joint_type"]).items():
        lines.append(f"- **{joint}**: {fmt(as_dict(values))}")  # type: ignore[arg-type]
    lines.append("")
    occlusion = as_dict(report["occlusion_hypothesis"])
    lines.append("## Occlusion hypothesis (C4)")
    lines.append(f"- Expected order (worst->best): {occlusion['expected_order_worst_to_best']}")
    lines.append(f"- Observed order (worst->best): {occlusion['observed_order_worst_to_best']}")
    lines.append(f"- Matches: {occlusion['matches']}")
    lines.append("")
    lines.append("## Index -> base_hex verification (A3)")
    verification = as_dict(report["index_to_base_hex_verification"])
    lines.append(f"- Checked {verification['checked']} (base, fill) pairs")
    lines.append(f"- Invalid pairs found: {verification['invalid_pairs_found']}")
    for w in as_list(verification["warnings"]):
        lines.append(f"  - {w}")
    lines.append("")
    lines.append("## Worst 20 symbols")
    for entry_obj in as_list(report["worst_20"]):
        entry = as_dict(entry_obj)
        lines.append(f"- {entry['symbol_id']} {entry['name']!r} ({entry['base_hex']}): MPJPE={entry['mpjpe']:.2f}")
    lines.append("")
    lines.append("## Best 20 symbols")
    for entry_obj in as_list(report["best_20"]):
        entry = as_dict(entry_obj)
        lines.append(f"- {entry['symbol_id']} {entry['name']!r} ({entry['base_hex']}): MPJPE={entry['mpjpe']:.2f}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not GROUND_TRUTH_PATH.exists():
        raise SystemExit(
            f"Ground truth not found at {GROUND_TRUTH_PATH}. "
            f"Run: python scripts/fetch_ground_truth.py"
        )
    raw = np.load(GROUND_TRUTH_PATH)
    subset = select_subset(raw)
    ground_truth = ground_truth_median(subset)
    index_warnings = verify_index_to_base_hex_mapping()

    report = build_report(ground_truth, index_warnings)

    REPORT_DIR.mkdir(exist_ok=True)
    json_path = REPORT_DIR / "fk_accuracy.json"
    md_path = REPORT_DIR / "fk_accuracy.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print()
    print(f"Overall MPJPE: {report['mpjpe_overall']}")


if __name__ == "__main__":
    main()
