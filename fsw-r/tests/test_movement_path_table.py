from __future__ import annotations

from fsw_r.core.iswa_data import GROUP_START
from fsw_r.core.pose_table import MOVEMENT_PATH_TABLE
from fsw_r.core.types import MotionPath

# Category 2 (Movement) spans groups 11-20 (GROUP_START indices 10-19).
_MOVEMENT_START = GROUP_START[10]
_MOVEMENT_END = GROUP_START[20] - 1  # last base of group 20, inclusive


def test_movement_path_table_has_exactly_242_entries() -> None:
    assert len(MOVEMENT_PATH_TABLE.base_hexes()) == 242


def test_every_base_hex_is_within_the_movement_range() -> None:
    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        assert _MOVEMENT_START <= base_hex <= _MOVEMENT_END


def test_every_entry_parses_to_a_motion_path() -> None:
    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        assert isinstance(MOVEMENT_PATH_TABLE[base_hex], MotionPath)


def test_contains_uses_base_hex() -> None:
    assert 0x205 in MOVEMENT_PATH_TABLE
    assert 0x100 not in MOVEMENT_PATH_TABLE  # a real Category 1 base, not Category 2
