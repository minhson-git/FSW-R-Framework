from __future__ import annotations

import pytest

from fsw_r.core.iswa_data import GROUP_START, group_of, valid_combinations_for
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import MotionPath

# Global group numbers 11-20 (GROUP_START indices 10-19) = Category 2 (Movement).
ALL_MOVEMENT_BASE_HEXES = [
    base_hex
    for group in range(11, 21)
    for base_hex in range(GROUP_START[group - 1], GROUP_START[group])
]


@pytest.mark.parametrize("base_hex", ALL_MOVEMENT_BASE_HEXES)
def test_symbol_constructs_and_gets_a_motion_path(base_hex: int) -> None:
    combos = valid_combinations_for(base_hex)
    fill = min(combos.fills)
    rotation = min(combos.rotations)
    symbol = MovementSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    assert symbol.hand_side is None
    assert isinstance(symbol.get_motion_path(), MotionPath)


def test_all_242_base_hexes_covered() -> None:
    assert len(ALL_MOVEMENT_BASE_HEXES) == 242
    assert len(set(ALL_MOVEMENT_BASE_HEXES)) == 242


# (base_hex, group, expected_fills or None for "all 6", expected rotation
# count) for the 20 base symbols covering 73.1% of real Category 2 token
# usage (sign-language-processing/signbank-plus) -- independently
# cross-checked against this project's own iswa_valid_combinations.json
# (generated from the real ISWA font, see scripts/gen_valid_combinations.py)
# and confirmed to match exactly.
TOP_20_MOST_FREQUENT_BASES = [
    (0x205, 11, [0], 1),  # 13.1% of all Cat 2 tokens -- only 1 valid combination total
    (0x265, 15, [0, 1, 2, 3], 8),
    (0x22A, 13, [0, 1, 2, 3], 8),
    (0x266, 15, [0, 1, 2, 3], 8),
    (0x22B, 13, [0, 1, 2, 3], 8),
    (0x221, 12, [0, 1, 2, 3, 4], 8),
    (0x20E, 11, [0], 1),
    (0x206, 11, [0, 1], 4),
    (0x26A, 15, [0, 1, 2], 8),
    (0x22F, 13, [0, 1, 2], 8),
    (0x2B7, 18, None, 8),
    (0x2D6, 19, [0, 1, 2, 3], 16),
    (0x211, 11, [0], 1),
    (0x288, 16, [0, 1, 2, 3], 16),
    (0x2A2, 16, None, 16),
    (0x2EA, 20, None, 16),
    (0x2DF, 19, None, 16),
    (0x2E7, 20, None, 16),
    (0x26C, 15, [0, 1, 2], 16),
    (0x289, 16, [0, 1, 2, 3], 16),
]


@pytest.mark.parametrize("base_hex,group,expected_fills,expected_rotation_count", TOP_20_MOST_FREQUENT_BASES)
def test_top_20_most_frequent_movement_bases(
    base_hex: int, group: int, expected_fills: list[int] | None, expected_rotation_count: int
) -> None:
    combos = valid_combinations_for(base_hex)
    if expected_fills is not None:
        assert sorted(combos.fills) == expected_fills
    else:
        assert len(combos.fills) == 6
    assert len(combos.rotations) == expected_rotation_count
    assert group_of(base_hex) == group

    symbol = MovementSymbol(base_hex=base_hex, fill=min(combos.fills), rotation=min(combos.rotations))
    assert symbol.get_motion_path() is not None


def test_movement_symbol_rejects_invalid_fill() -> None:
    # 0x205 (13.1% of all Cat 2 tokens) only has fill=0 in real ISWA --
    # hardcoding range(6) would silently accept hundreds of symbols that
    # don't exist, starting with this single highest-frequency base alone.
    with pytest.raises(ValueError):
        MovementSymbol(base_hex=0x205, fill=1, rotation=0)


def test_movement_symbol_accepts_its_one_valid_fill() -> None:
    symbol = MovementSymbol(base_hex=0x205, fill=0, rotation=0)
    assert symbol.fill == 0


def test_symbol_from_fsw_now_builds_a_movement_symbol() -> None:
    symbol = symbol_from_fsw("S22b03")
    assert isinstance(symbol, MovementSymbol)
    assert symbol.base_hex == 0x22B
    assert symbol.fill == 0
    assert symbol.rotation == 3
    assert symbol.hand_side is None
