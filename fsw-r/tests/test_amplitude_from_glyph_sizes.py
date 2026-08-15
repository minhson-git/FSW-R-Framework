"""Dedicated B1-B5 tests for this task's brief ("`amplitude` từ variation +
kích thước glyph") -- ``data/iswa_movement_glyph_sizes.json``
(``scripts/gen_movement_glyph_sizes.py``) and the within-``(base_symbol_id,
path_type)`` amplitude ratio it feeds (``scripts/gen_movement_paths.py``'s
``amplitudes_for_group()``).

B6 ("regeneration script byte-identical") is NOT a pytest test here, same
reason Task 1's D6 and Task 2's C7 weren't: ``gen_movement_glyph_sizes.py``
needs live ``npm pack`` network access, which would make the suite
non-offline-runnable. Verified by hand this session (two runs, diffed
byte-for-byte identical) and recorded in PROGRESS.md.

B7 ("test cũ pass, test nào assert amplitude==10.0 sẽ fail"): verified (not
assumed) that BEFORE this task, no existing test asserted a specific
base_hex's real ``amplitude`` against ``MOVEMENT_PATH_TABLE`` --
``test_movement_paths.py`` only constructs ``MotionPath`` directly via its
own fixture helper (with its own explicit ``amplitude=10.0``/``5.0``/
``20.0`` default arguments, never reading the loaded table). So 0 existing
tests needed updating -- the full suite was green (1,525/1,525) immediately
after regenerating ``movement_paths.json``.

B8 (``reports/fk_accuracy.md`` unchanged) is a ``git diff`` check on the
final commit, not a pytest test -- this task never touches Category 1 data
in the first place (only ``movement_paths.json`` and its own new glyph/name
resource files), so the report is untouched by construction.
"""

from __future__ import annotations

import gen_movement_paths
import numpy as np
import pytest

from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.pose_table import MOVEMENT_PATH_TABLE

# (large, small) pairs, same base_symbol_id, same path_type -- spanning
# several path_types and BOTH variation-number orders (0x216/0x217 has
# "Large" as variation 1 and "Small" as variation 2, the REVERSE of the
# others -- see PROGRESS.md's A1 finding: variation number order is not
# reliably size order, so these tests read amplitude directly, never assume
# ascending variation number means ascending size).
LARGE_SMALL_PAIRS = [
    (0x22C, 0x22A, "Single Straight Movement, Wall Plane"),
    (0x216, 0x217, "Squeeze ... Single (reversed variation order)"),
    (0x23A, 0x238, "Bend, Wall Plane"),
    (0x247, 0x245, "Zigzag, Wall Plane"),
    (0x267, 0x265, "Single Straight Movement, Floor Plane"),
]

# B5 needs a real (non-degenerate) trajectory -- excludes 0x216/0x217
# (FINGER: the wrist does not translate at all for Group 12, by design, so
# "trajectory length" is always 0 regardless of amplitude -- see
# core/movement_paths.py's _canonical_shape() docstring). B2's amplitude
# comparison above is still meaningful for FINGER (amplitude still sets the
# point's own position), just not a "longer path" claim.
TRAJECTORY_LARGE_SMALL_PAIRS = [pair for pair in LARGE_SMALL_PAIRS if pair[:2] != (0x216, 0x217)]


def _path_length(base_hex: int) -> float:
    points = sample_trajectory(MOVEMENT_PATH_TABLE[base_hex], rotation=0)
    diffs = np.diff(points, axis=0)
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def test_b1_amplitude_is_not_uniform_and_correlates_with_size_names() -> None:
    amplitudes = {MOVEMENT_PATH_TABLE[b].amplitude for b in MOVEMENT_PATH_TABLE.base_hexes()}
    assert len(amplitudes) > 1, "every base still has the same amplitude -- the fix did nothing"

    # The 4-step Small/Medium/Large/Largest family (0x22a-0x22d) must be
    # monotonically increasing, matching their names exactly.
    small, medium, large, largest = (MOVEMENT_PATH_TABLE[b].amplitude for b in (0x22A, 0x22B, 0x22C, 0x22D))
    assert small < medium < large < largest


@pytest.mark.parametrize("large_base,small_base,label", LARGE_SMALL_PAIRS)
def test_b2_large_variation_has_bigger_amplitude_than_small(large_base: int, small_base: int, label: str) -> None:
    large_amplitude = MOVEMENT_PATH_TABLE[large_base].amplitude
    small_amplitude = MOVEMENT_PATH_TABLE[small_base].amplitude
    assert large_amplitude > small_amplitude, f"{label}: large={large_amplitude}, small={small_amplitude}"


def test_b3_single_variation_bases_have_a_valid_nonzero_amplitude() -> None:
    # 0x205 "Touch Single" (Contact) has no sibling variation at all --
    # answers this task's brief's own A1 question ("base chỉ có một
    # variation dùng giá trị mặc định nào"): the group-mean default, 10.0.
    amplitude = MOVEMENT_PATH_TABLE[0x205].amplitude
    assert amplitude is not None
    assert amplitude != 0.0
    assert amplitude == pytest.approx(10.0)

    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        amplitude = MOVEMENT_PATH_TABLE[base_hex].amplitude
        assert amplitude is not None and amplitude > 0.0, f"0x{base_hex:x}: amplitude={amplitude}"


def test_b4_overall_mean_amplitude_within_20_percent_of_10() -> None:
    amplitudes = [MOVEMENT_PATH_TABLE[b].amplitude for b in MOVEMENT_PATH_TABLE.base_hexes()]
    mean = sum(amplitudes) / len(amplitudes)
    assert 8.0 <= mean <= 12.0, f"overall mean amplitude = {mean} (target 10.0 +/- 20%)"


@pytest.mark.parametrize("large_base,small_base,label", TRAJECTORY_LARGE_SMALL_PAIRS)
def test_b5_large_variation_trajectory_is_longer_than_small(large_base: int, small_base: int, label: str) -> None:
    large_length = _path_length(large_base)
    small_length = _path_length(small_base)
    assert large_length > small_length, f"{label}: large={large_length:.3f}, small={small_length:.3f}"


def test_amplitudes_for_group_singleton_normalizes_to_the_group_mean() -> None:
    result = gen_movement_paths.amplitudes_for_group([0x205], {0x205: 123})
    assert result[0x205] == pytest.approx(10.0)


def test_amplitudes_for_group_preserves_the_group_mean() -> None:
    sizes = {0x22A: 100, 0x22B: 200, 0x22C: 300}
    result = gen_movement_paths.amplitudes_for_group([0x22A, 0x22B, 0x22C], sizes)
    assert sum(result.values()) / len(result) == pytest.approx(10.0)
    assert result[0x22A] < result[0x22B] < result[0x22C]
