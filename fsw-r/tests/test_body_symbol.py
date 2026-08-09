from __future__ import annotations

import pytest

from fsw_r.core.body_symbol import BodySymbol
from fsw_r.core.body_types import BodyPart
from fsw_r.core.iswa_data import category_of, group_of, valid_combinations_for
from fsw_r.core.pose_table import BODY_POSE_TABLE, EXPECTED_BODY_COUNT
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.renderable_symbol import FSWBodyRenderable

_BODY_BASES = sorted(BODY_POSE_TABLE.base_hexes())


def test_table_has_expected_count() -> None:
    assert len(_BODY_BASES) == EXPECTED_BODY_COUNT == 18


@pytest.mark.parametrize("base_hex", _BODY_BASES)
def test_every_base_is_category5(base_hex: int) -> None:
    # Trunk = group 27, Limb = group 28, both under category 5 ("trunk &
    # limb" is one category, see core/iswa_data.py's module docstring).
    assert category_of(base_hex) == 5
    assert group_of(base_hex) in {27, 28}


@pytest.mark.parametrize("base_hex", _BODY_BASES)
def test_symbol_builds_and_get_body_pose_does_not_raise(base_hex: int) -> None:
    # C2/C5: first valid (fill, rotation) for this base, real FSW key.
    combos = valid_combinations_for(base_hex)
    fill, rotation = min(combos.fills), min(combos.rotations)
    key = f"S{base_hex:03x}{fill:x}{rotation:x}"
    symbol = symbol_from_fsw(key)
    assert isinstance(symbol, BodySymbol)
    assert isinstance(symbol, FSWBodyRenderable)
    assert symbol.hand_side is None
    pose = symbol.get_body_pose()
    assert pose.part in (BodyPart.TRUNK, BodyPart.LIMB)


def test_trunk_group_has_trunk_pose_fields() -> None:
    symbol = symbol_from_fsw("S36d00")  # Shoulder Hip Spine, base_symbol_number 1 of group 27
    assert isinstance(symbol, BodySymbol)
    pose = symbol.get_body_pose()
    assert pose.part == BodyPart.TRUNK
    assert pose.motion_type == "REFERENCE"
    assert pose.trunk_rotation is not None
    assert pose.shoulder_offset is not None
    assert pose.limb_length_units is None


def test_limb_group_has_limb_length_units() -> None:
    symbol = symbol_from_fsw("S37700")  # Limb Length 1, base_symbol_number 2 of group 28
    assert isinstance(symbol, BodySymbol)
    pose = symbol.get_body_pose()
    assert pose.part == BodyPart.LIMB
    assert pose.limb_length_units == 1
    assert pose.trunk_rotation is None
    assert pose.shoulder_offset is None


def test_limb_combinations_and_fingers_have_zero_length_units() -> None:
    combinations = symbol_from_fsw("S37600")  # Limb Combinations, first of group 28
    fingers = symbol_from_fsw("S37e00")  # Fingers, last of group 28
    assert isinstance(combinations, BodySymbol) and isinstance(fingers, BodySymbol)
    assert combinations.get_body_pose().limb_length_units == 0
    assert fingers.get_body_pose().limb_length_units == 0


def test_c3_valid_combinations_reject_out_of_range_fill() -> None:
    # 0x36d ("Shoulder Hip Spine") only has fills [0, 1, 2] -- fill=4 (hex
    # digit '4') must be rejected by the real ISWA valid-combinations table.
    with pytest.raises(ValueError):
        symbol_from_fsw("S36d40")


def test_c3_valid_combinations_reject_out_of_range_fill_for_single_fill_base() -> None:
    # 0x376 ("Limb Combinations") only has fill [0] -- fill=1 must be rejected.
    with pytest.raises(ValueError):
        symbol_from_fsw("S37610")
