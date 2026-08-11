from __future__ import annotations

from eval_anatomical import (
    build_report,
    correlation_with_fk_error,
    evaluate_all,
    SymbolViolations,
)
from fsw_r.validation.anatomical_limits import FLEXION_CHECKS_PER_POSE, Violation


def test_evaluate_all_covers_all_261_symbols() -> None:
    results = evaluate_all()
    assert len(results) == 261


def test_evaluate_all_matches_validate_pose_directly() -> None:
    from fsw_r.core.pose_table import HAND_POSE_TABLE
    from fsw_r.validation.anatomical_limits import validate_pose

    results = {r.base_hex: r for r in evaluate_all()}
    for base_hex in (0x100, 0x1F5, 0x204):  # a few real Category 1 bases
        assert results[base_hex].violations == validate_pose(HAND_POSE_TABLE[base_hex])


def test_symbol_violations_worst_overshoot_is_zero_when_no_violations() -> None:
    entry = SymbolViolations(base_hex=0x100, symbol_id="01-01-001", name="Index", violations=[])
    assert entry.worst_flexion_overshoot == 0.0


def test_symbol_violations_worst_overshoot_reflects_largest_excess() -> None:
    entry = SymbolViolations(
        base_hex=0x100,
        symbol_id="01-01-001",
        name="Index",
        violations=[
            Violation(finger="index", joint="pip", angle_type="flexion", value=140.0, limit=(0.0, 120.0)),
            Violation(finger="index", joint="dip", angle_type="flexion", value=100.0, limit=(0.0, 90.0)),
        ],
    )
    assert entry.worst_flexion_overshoot == 20.0  # 140 - 120, larger than 100 - 90


def test_build_report_denominator_matches_brief() -> None:
    # 261 symbols x 15 flexion checks/symbol = 3,915, cited directly in
    # this task's brief.
    results = evaluate_all()
    report = build_report(results)
    flexion = report["flexion"]
    assert isinstance(flexion, dict)
    assert flexion["angle_checks_total"] == 261 * FLEXION_CHECKS_PER_POSE == 3915


def test_correlation_without_fk_report_says_so_honestly() -> None:
    results = evaluate_all()[:5]
    result = correlation_with_fk_error(results, None)
    assert isinstance(result, str)
    assert "eval_fk_accuracy" in result


def test_correlation_with_fake_mpjpe_data() -> None:
    results = evaluate_all()
    fake_mpjpe = {r.base_hex: float(i) for i, r in enumerate(results)}
    result = correlation_with_fk_error(results, fake_mpjpe)
    assert isinstance(result, dict)
    assert "pearson_r" in result
    assert result["n_symbols"] == len(results)
