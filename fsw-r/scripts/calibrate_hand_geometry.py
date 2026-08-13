"""Fits the two UN-CITED thumb geometry constants in
``export/forward_kinematics.py`` -- ``_THUMB_BASE_OFFSET_MM`` (where the thumb
attaches to the palm) and ``_THUMB_BASE_ROTATION`` (how the whole thumb chain
is oriented off the palm) -- to the ``3d-hands-benchmark`` ground truth, so
the thumb (this project's single largest FK error source: MPJPE ~80 vs 39-48
for the other fingers) stops dominating.

**Why this is a separate script, not part of eval_fk_accuracy.py, and why it
reuses that module wholesale:** the ground-truth construction
(``select_subset`` + ``ground_truth_median``) and the normalization
(``validation/normalization.normalize_landmarks``, which includes the z-sign
canonicalization fix for ``PoseNormalizer``'s plane-normal ambiguity) are
exactly the pieces the task brief says MUST be reused verbatim -- rewriting
the normalization risks silently reintroducing the mirror-flip bug that turns
every downstream number into noise. This script imports them; it does not
reimplement them.

**Mandatory train/test split (the methodological core of the brief):** the
thumb constants are fit on a TRAIN subset only, and the number that matters --
the one publishable -- is MPJPE on the held-out TEST subset. Fitting on all
261 symbols and reporting on those same 261 would be overfitting. The split is
stratified by ISWA group (so no handshape family is over-represented in test)
and seeded (``SPLIT_SEED``) for reproducibility; the base_hex membership of
each subset is written to ``reports/calibration_split.json`` and committed.

**One seed, one initialization, honest result.** This script does NOT sweep
seeds/inits looking for a flattering number. If the held-out improvement is
not meaningful, that is reported as-is (a negative result isolates the error
to the joint angles rather than the reconstruction geometry -- see the brief's
"accept negative result" clause). Adopting the fit into the source is a
deliberate human step gated on the printed test-set improvement, NOT done
automatically by this script.

Run: ``python scripts/calibrate_hand_geometry.py``
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation

import fsw_r.export.forward_kinematics as fk
from eval_fk_accuracy import (
    BASE_COUNT,
    FIRST_BASE_HEX,
    GROUND_TRUTH_PATH,
    average_pose,
    ground_truth_median,
    group_of_base_hex,
    per_landmark_error,
    predict_landmarks,
    select_subset,
)
from fsw_r.core.pose_table import HAND_POSE_TABLE
from fsw_r.core.types import HandJointPose
from fsw_r.export.bone_lengths import HAND_SCALE

# --- Reproducibility knobs, recorded in every report this script writes ---
SPLIT_SEED = 42
TRAIN_FRACTION = 0.70
# The current (pre-fit) values, kept here as the optimizer's start point so a
# zero-improvement fit reproduces exactly today's geometry. Offset is the raw
# [x, y, z] ratio BEFORE the * HAND_SCALE the source applies (see
# forward_kinematics.py) -- kept raw so the fit stays scale-coupled to the one
# stature everything else derives from.
INITIAL_OFFSET_RAW = np.array([26.0, 15.0, 0.0])
INITIAL_ROTATION_ZY_DEG = np.array([-65.0, -20.0])

# The brief's threshold: below this held-out relative improvement, keep the old
# constants and report a negative result rather than adopting noise.
MEANINGFUL_IMPROVEMENT = 0.05

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"

_Vec = NDArray[np.float64]


@contextmanager
def _patched_thumb(params: _Vec) -> Iterator[None]:
    """Temporarily install trial thumb constants into the live
    ``forward_kinematics`` module (which ``predict_landmarks`` reads at call
    time), restoring the originals on exit so the module is never left mutated.

    ``params``: ``[ox, oy, oz, rot_z_deg, rot_y_deg]`` -- the raw offset ratio
    and the two "zy" Euler angles, exactly the two constants' own parameters.
    """
    old_offset = fk._THUMB_BASE_OFFSET_MM
    old_rotation = fk._THUMB_BASE_ROTATION
    try:
        fk._THUMB_BASE_OFFSET_MM = np.asarray(params[:3], dtype=float) * HAND_SCALE
        fk._THUMB_BASE_ROTATION = Rotation.from_euler("zy", params[3:5], degrees=True)
        yield
    finally:
        fk._THUMB_BASE_OFFSET_MM = old_offset
        fk._THUMB_BASE_ROTATION = old_rotation


def _mpjpe(base_hexes: Sequence[int], ground_truth: _Vec) -> float:
    """Mean per-symbol MPJPE (mean over 21 landmarks, then over symbols) for a
    set of base symbols, using whatever thumb constants are currently live."""
    errors = [
        float(per_landmark_error(predict_landmarks(HAND_POSE_TABLE[b]), ground_truth[b - FIRST_BASE_HEX]).mean())
        for b in base_hexes
    ]
    return float(np.mean(errors))


def stratified_split(seed: int, train_fraction: float) -> tuple[list[int], list[int]]:
    """Split the 261 Category-1 base symbols into (train, test) base_hex lists,
    stratified by ISWA group so the 30% test set holds a representative slice
    of every handshape family, not a lump of one. Seeded and deterministic."""
    rng = np.random.default_rng(seed)
    train: list[int] = []
    test: list[int] = []
    for group in range(1, 11):
        members = [FIRST_BASE_HEX + i for i in range(BASE_COUNT) if group_of_base_hex(FIRST_BASE_HEX + i) == group]
        rng.shuffle(members)
        n_train = round(len(members) * train_fraction)
        train.extend(sorted(members[:n_train]))
        test.extend(sorted(members[n_train:]))
    return sorted(train), sorted(test)


def _baselines_on_test(train: Sequence[int], test: Sequence[int], ground_truth: _Vec) -> dict[str, float]:
    """The two naive predictors from eval_fk_accuracy, recomputed on the TEST
    set (built from TRAIN poses only, so no test leakage), using whatever thumb
    constants are currently live -- a floor the per-symbol model should beat."""
    # Baseline 1: one average pose (over train) predicts every test symbol.
    avg_prediction = predict_landmarks(average_pose([HAND_POSE_TABLE[b] for b in train]))
    base1 = float(np.mean([per_landmark_error(avg_prediction, ground_truth[b - FIRST_BASE_HEX]).mean() for b in test]))

    # Baseline 2: one average pose per ISWA group (over that group's train
    # members) predicts that group's test members.
    group_prediction: dict[int, _Vec] = {}
    for group in range(1, 11):
        members = [HAND_POSE_TABLE[b] for b in train if group_of_base_hex(b) == group]
        group_prediction[group] = predict_landmarks(average_pose(members))
    base2 = float(
        np.mean(
            [
                per_landmark_error(group_prediction[group_of_base_hex(b)], ground_truth[b - FIRST_BASE_HEX]).mean()
                for b in test
            ]
        )
    )
    return {"average_pose_baseline": base1, "one_pose_per_group_baseline": base2}


def _pose_count_by_group(base_hexes: Sequence[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for b in base_hexes:
        g = group_of_base_hex(b)
        counts[g] = counts.get(g, 0) + 1
    return counts


def main() -> None:
    if not GROUND_TRUTH_PATH.exists():
        raise SystemExit(f"Ground truth not found at {GROUND_TRUTH_PATH}. Run: python scripts/fetch_ground_truth.py")

    raw = np.load(GROUND_TRUTH_PATH)
    ground_truth = ground_truth_median(select_subset(raw))  # (261, 21, 3), normalized

    train, test = stratified_split(SPLIT_SEED, TRAIN_FRACTION)
    assert len(train) + len(test) == BASE_COUNT and not (set(train) & set(test))

    split_path = REPORT_DIR / "calibration_split.json"
    split_path.write_text(
        json.dumps(
            {
                "seed": SPLIT_SEED,
                "train_fraction": TRAIN_FRACTION,
                "stratified_by": "ISWA Category 1 group (1-10)",
                "n_train": len(train),
                "n_test": len(test),
                "train_by_group": _pose_count_by_group(train),
                "test_by_group": _pose_count_by_group(test),
                "train_base_hex": [f"0x{b:03x}" for b in train],
                "test_base_hex": [f"0x{b:03x}" for b in test],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    initial_params = np.concatenate([INITIAL_OFFSET_RAW, INITIAL_ROTATION_ZY_DEG])

    # Four numbers: before is the live source constants (== initial_params).
    train_before = _mpjpe(train, ground_truth)
    test_before = _mpjpe(test, ground_truth)

    # Fit on TRAIN only. Nelder-Mead: derivative-free, deterministic from x0,
    # appropriate for this low-dim, mildly non-smooth objective (the z-sign
    # canonicalization introduces rare discontinuities). One start, no restarts.
    def objective(params: _Vec) -> float:
        with _patched_thumb(params):
            return _mpjpe(train, ground_truth)

    result = minimize(objective, initial_params, method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-4})
    fitted_params: _Vec = np.asarray(result.x, dtype=float)

    with _patched_thumb(fitted_params):
        train_after = _mpjpe(train, ground_truth)
        test_after = _mpjpe(test, ground_truth)
        baselines_test = _baselines_on_test(train, test, ground_truth)

    test_improvement = (test_before - test_after) / test_before
    train_improvement = (train_before - train_after) / train_before
    adopt = test_improvement >= MEANINGFUL_IMPROVEMENT

    fitted_offset_raw = fitted_params[:3]
    fitted_rotation_zy = fitted_params[3:5]

    report = {
        "_meta": {
            "generated_by": "scripts/calibrate_hand_geometry.py",
            "objective": "MPJPE (mean per-symbol) after validation/normalization.normalize_landmarks (size=150)",
            "fitted_constants": "_THUMB_BASE_OFFSET_MM (raw, pre-HAND_SCALE) and _THUMB_BASE_ROTATION (zy Euler deg)",
            "optimizer": f"scipy Nelder-Mead, single start x0={initial_params.tolist()}, no restarts",
            "seed": SPLIT_SEED,
            "meaningful_improvement_threshold": MEANINGFUL_IMPROVEMENT,
        },
        "split": {"n_train": len(train), "n_test": len(test), "seed": SPLIT_SEED, "stratified_by": "ISWA group"},
        "mpjpe": {
            "train_before": train_before,
            "train_after": train_after,
            "test_before": test_before,
            "test_after": test_after,
        },
        "improvement": {
            "train_relative": train_improvement,
            "test_relative": test_improvement,
            "test_is_meaningful": adopt,
        },
        "baselines_on_test": baselines_test,
        "fitted": {
            "thumb_base_offset_mm_raw": fitted_offset_raw.tolist(),
            "thumb_base_offset_mm_scaled": (fitted_offset_raw * HAND_SCALE).tolist(),
            "thumb_base_rotation_zy_deg": fitted_rotation_zy.tolist(),
            "optimizer_success": bool(result.success),
            "optimizer_iterations": int(result.nit),
        },
        "initial": {
            "thumb_base_offset_mm_raw": INITIAL_OFFSET_RAW.tolist(),
            "thumb_base_rotation_zy_deg": INITIAL_ROTATION_ZY_DEG.tolist(),
        },
    }
    (REPORT_DIR / "fk_calibration.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (REPORT_DIR / "fk_calibration.md").write_text(_render_markdown(report), encoding="utf-8")

    print(_render_markdown(report))
    print(f"\nWrote {split_path}")
    print(f"Wrote {REPORT_DIR / 'fk_calibration.json'}")
    print(f"Wrote {REPORT_DIR / 'fk_calibration.md'}")
    verdict = "ADOPT (>= 5% held-out)" if adopt else "KEEP OLD (negative result, < 5% held-out)"
    print(f"\nDECISION: {verdict}")


def _render_markdown(report: dict[str, object]) -> str:
    def d(key: str) -> dict[str, object]:
        value = report[key]
        assert isinstance(value, dict)
        return value

    def num(dct: dict[str, object], key: str) -> float:
        value = dct[key]
        assert isinstance(value, (int, float))
        return float(value)

    def txt(dct: dict[str, object], key: str) -> str:
        return str(dct[key])

    mpjpe = d("mpjpe")
    imp = d("improvement")
    base = d("baselines_on_test")
    fitted = d("fitted")
    meta = d("_meta")
    split = d("split")
    lines = [
        "# Hand-geometry calibration (thumb constants, held-out)",
        "",
        f"Seed **{txt(meta, 'seed')}**, stratified by {txt(split, 'stratified_by')}, "
        f"train **{txt(split, 'n_train')}** / test **{txt(split, 'n_test')}**.",
        f"Objective: {txt(meta, 'objective')}.",
        f"Optimizer: {txt(meta, 'optimizer')}.",
        "",
        "## The four numbers (MPJPE, normalized size=150)",
        "",
        "| | train | test |",
        "|---|---|---|",
        f"| before | {num(mpjpe, 'train_before'):.2f} | {num(mpjpe, 'test_before'):.2f} |",
        f"| after | {num(mpjpe, 'train_after'):.2f} | {num(mpjpe, 'test_after'):.2f} |",
        "",
        f"Held-out (test) relative improvement: **{num(imp, 'test_relative') * 100:.1f}%** "
        f"(train {num(imp, 'train_relative') * 100:.1f}%). "
        f"Meaningful (>= {num(meta, 'meaningful_improvement_threshold') * 100:.0f}%): "
        f"**{txt(imp, 'test_is_meaningful')}**.",
        "",
        "## Baselines recomputed on the SAME test set",
        f"- average_pose_baseline: {num(base, 'average_pose_baseline'):.2f}",
        f"- one_pose_per_group_baseline: {num(base, 'one_pose_per_group_baseline'):.2f}",
        "",
        "## Fitted thumb constants (FITTED origin -- from data, not a citation)",
        f"- `_THUMB_BASE_OFFSET_MM` raw ratio: {[round(v, 3) for v in _as_floats(fitted['thumb_base_offset_mm_raw'])]}"
        f" (was {INITIAL_OFFSET_RAW.tolist()})",
        f"- `_THUMB_BASE_ROTATION` zy deg: {[round(v, 2) for v in _as_floats(fitted['thumb_base_rotation_zy_deg'])]}"
        f" (was {INITIAL_ROTATION_ZY_DEG.tolist()})",
        f"- optimizer success: {fitted['optimizer_success']}, iterations: {fitted['optimizer_iterations']}",
        "",
    ]
    return "\n".join(lines)


def _as_floats(value: object) -> list[float]:
    assert isinstance(value, list)
    return [float(v) for v in value]


if __name__ == "__main__":
    main()
