"""Measures how much of Category 1's 261 hand poses (``data/
hand_joint_poses.json``) violate real anatomical joint limits
(``validation/anatomical_limits.py``) -- this evaluation task's Câu 2
(Part 0), quantified precisely instead of estimated. A MEASURING script --
it does not clamp or edit ``hand_joint_poses.json``.

Needs no external ground truth file (unlike ``eval_fk_accuracy.py``) --
``hand_joint_poses.json`` is already bundled with ``fsw_r`` -- so this runs
anywhere the package is installed, no fetch step first.

If ``reports/fk_accuracy.json`` already exists (from
``eval_fk_accuracy.py``), this also reports the correlation between a
symbol's anatomical-violation severity and its FK reconstruction error
(C3's last requirement) -- skipped, not faked, if that file isn't there.

Run:  python scripts/eval_anatomical.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from fsw_r.core.iswa_data import symbol_id_of
from fsw_r.core.pose_table import HAND_NAME_TABLE, HAND_POSE_TABLE
from fsw_r.validation.anatomical_limits import (
    ESTIMATED_LIMITS,
    FLEXION_CHECKS_PER_POSE,
    Violation,
    validate_pose,
)

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
FK_ACCURACY_REPORT = REPORT_DIR / "fk_accuracy.json"


@dataclass(frozen=True)
class SymbolViolations:
    base_hex: int
    symbol_id: str
    name: str
    violations: list[Violation]

    @property
    def flexion_violations(self) -> list[Violation]:
        return [v for v in self.violations if v.angle_type == "flexion"]

    @property
    def abduction_violations(self) -> list[Violation]:
        return [v for v in self.violations if v.angle_type == "abduction"]

    @property
    def worst_flexion_overshoot(self) -> float:
        overshoots = [max(v.value - v.limit[1], v.limit[0] - v.value, 0.0) for v in self.flexion_violations]
        return max(overshoots) if overshoots else 0.0


def evaluate_all() -> list[SymbolViolations]:
    results = []
    for base_hex in sorted(HAND_POSE_TABLE.base_hexes()):
        pose = HAND_POSE_TABLE[base_hex]
        violations = validate_pose(pose)
        results.append(
            SymbolViolations(
                base_hex=base_hex,
                symbol_id=symbol_id_of(base_hex),
                name=HAND_NAME_TABLE.get(base_hex, "?"),
                violations=violations,
            )
        )
    return results


def _finger_flexion_distribution(results: list[SymbolViolations]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in results:
        seen_fingers = {v.finger for v in r.flexion_violations}
        for finger in seen_fingers:
            counts[finger] = counts.get(finger, 0) + 1
    return counts


def _joint_flexion_distribution(results: list[SymbolViolations]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in results:
        for v in r.flexion_violations:
            counts[v.joint] = counts.get(v.joint, 0) + 1
    return counts


def _load_mpjpe_by_base_hex() -> dict[int, float] | None:
    if not FK_ACCURACY_REPORT.exists():
        return None
    data = json.loads(FK_ACCURACY_REPORT.read_text(encoding="utf-8"))
    per_symbol = data.get("per_symbol_mpjpe")
    if not per_symbol:
        return None  # older report without the full per-symbol field
    return {int(k, 16): v for k, v in per_symbol.items()}


def correlation_with_fk_error(
    results: list[SymbolViolations], mpjpe_by_base_hex: dict[int, float] | None
) -> dict[str, object] | str:
    """Pearson correlation between a symbol's worst flexion overshoot
    (degrees beyond the limit; 0 for no violation) and its FK
    reconstruction MPJPE, across all 261 symbols -- C3's last requirement:
    if violation severity and FK error move together, the two issues share
    a root cause (systematic MediaPipe estimation error on occluded
    fingers) rather than being independent problems."""
    if mpjpe_by_base_hex is None:
        return "not computed -- run eval_fk_accuracy.py first (needs data/external/hands.npy)"
    overshoots = []
    mpjpes = []
    for r in results:
        if r.base_hex in mpjpe_by_base_hex:
            overshoots.append(r.worst_flexion_overshoot)
            mpjpes.append(mpjpe_by_base_hex[r.base_hex])
    if len(overshoots) < 2:
        return "not enough overlapping symbols to compute a correlation"
    correlation = float(np.corrcoef(overshoots, mpjpes)[0, 1])
    return {
        "pearson_r": correlation,
        "n_symbols": len(overshoots),
        "interpretation": (
            "positive r: symbols with worse anatomical violations tend to also have worse FK "
            "reconstruction error (consistent with a shared root cause); near-zero or negative r: "
            "the two are not obviously related"
        ),
    }


def build_report(results: list[SymbolViolations]) -> dict[str, object]:
    total = len(results)
    with_any_flexion_violation = [r for r in results if r.flexion_violations]
    total_flexion_checks = total * FLEXION_CHECKS_PER_POSE
    total_flexion_violations = sum(len(r.flexion_violations) for r in results)

    finger_dist = _finger_flexion_distribution(results)
    joint_dist = _joint_flexion_distribution(results)

    worst = sorted(results, key=lambda r: -r.worst_flexion_overshoot)[:20]
    worst = [r for r in worst if r.worst_flexion_overshoot > 0]

    with_abduction_violation = [r for r in results if r.abduction_violations]

    return {
        "_meta": {
            "source": "data/hand_joint_poses.json (261 Category 1 symbols)",
            "limits_source": "validation/anatomical_limits.py -- see its module docstring for citations per joint",
            "estimated_limits": [f"{k[0]}.{k[1]}" for k in sorted(ESTIMATED_LIMITS)],
            "generated_by": "scripts/eval_anatomical.py",
        },
        "flexion": {
            "symbols_with_violation": len(with_any_flexion_violation),
            "symbols_total": total,
            "angle_checks_with_violation": total_flexion_violations,
            "angle_checks_total": total_flexion_checks,
            "by_finger": finger_dist,
            "by_joint": joint_dist,
            "worst_overshoot": [
                {
                    "base_hex": f"0x{r.base_hex:03x}",
                    "symbol_id": r.symbol_id,
                    "name": r.name,
                    "worst_overshoot_degrees": r.worst_flexion_overshoot,
                    "violations": [
                        {"finger": v.finger, "joint": v.joint, "value": v.value, "limit": v.limit}
                        for v in r.flexion_violations
                    ],
                }
                for r in worst
            ],
        },
        "abduction": {
            "symbols_with_violation": len(with_abduction_violation),
            "symbols_total": total,
            "note": (
                "hand_joint_poses.json's own abduction values are already documented "
                "as un-measured estimates (see PROGRESS.md) -- these violation counts "
                "are a weaker signal than the flexion ones above, reported separately "
                "rather than merged into one number."
            ),
        },
        "correlation_with_fk_error": correlation_with_fk_error(results, _load_mpjpe_by_base_hex()),
    }


def render_markdown(report: dict[str, object], results: list[SymbolViolations]) -> str:
    flexion = report["flexion"]
    assert isinstance(flexion, dict)
    abduction = report["abduction"]
    assert isinstance(abduction, dict)

    lines = ["# Anatomical Limit Evaluation", ""]
    lines.append("## Flexion violations")
    lines.append(
        f"- Symbols with >=1 violation: {flexion['symbols_with_violation']}/{flexion['symbols_total']} "
        f"({100 * flexion['symbols_with_violation'] / flexion['symbols_total']:.1f}%)"
    )
    lines.append(
        f"- Angle checks with violation: {flexion['angle_checks_with_violation']}/{flexion['angle_checks_total']}"
    )
    lines.append("")
    lines.append("### By finger")
    for finger, count in sorted(flexion["by_finger"].items(), key=lambda kv: -kv[1]):
        lines.append(f"- {finger}: {count}")
    lines.append("")
    lines.append("### By joint")
    for joint, count in sorted(flexion["by_joint"].items(), key=lambda kv: -kv[1]):
        lines.append(f"- {joint}: {count}")
    lines.append("")
    lines.append("### Worst overshoot (top 20)")
    for entry in flexion["worst_overshoot"]:
        lines.append(
            f"- {entry['symbol_id']} {entry['name']!r} ({entry['base_hex']}): "
            f"overshoot={entry['worst_overshoot_degrees']:.1f} deg"
        )
    lines.append("")
    lines.append("## Abduction violations")
    lines.append(
        f"- Symbols with >=1 violation: {abduction['symbols_with_violation']}/{abduction['symbols_total']}"
    )
    lines.append(f"- Note: {abduction['note']}")
    lines.append("")
    lines.append("## Correlation with FK reconstruction error (C3)")
    correlation = report["correlation_with_fk_error"]
    if isinstance(correlation, dict):
        lines.append(f"- Pearson r = {correlation['pearson_r']:.3f} (n={correlation['n_symbols']})")
        lines.append(f"- {correlation['interpretation']}")
    else:
        lines.append(f"- {correlation}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    results = evaluate_all()
    report = build_report(results)

    REPORT_DIR.mkdir(exist_ok=True)
    json_path = REPORT_DIR / "anatomical.json"
    md_path = REPORT_DIR / "anatomical.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report, results), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
