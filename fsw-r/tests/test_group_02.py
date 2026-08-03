from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_02_index_middle_fingers import (
    BaseSymbol01_02_001_IndexMiddle,
    BaseSymbol01_02_002_IndexMiddleOnCircle,
    BaseSymbol01_02_003_IndexMiddleBent,
    BaseSymbol01_02_004_IndexMiddleRaisedKnuckles,
    BaseSymbol01_02_005_IndexMiddleHinge,
    BaseSymbol01_02_006_IndexUpMiddleHinge,
    BaseSymbol01_02_007_IndexHingeMiddleUp,
    BaseSymbol01_02_008_IndexMiddleUnit,
    BaseSymbol01_02_009_IndexMiddleUnitIndexBent,
    BaseSymbol01_02_010_IndexMiddleUnitMiddleBent,
    BaseSymbol01_02_011_IndexMiddleUnitCup,
    BaseSymbol01_02_012_IndexMiddleUnitHinge,
    BaseSymbol01_02_013_IndexMiddleCross,
    BaseSymbol01_02_014_IndexMiddleCrossOnCircle,
    BaseSymbol01_02_015_MiddleBentOverIndex,
    BaseSymbol01_02_016_IndexBentOverMiddle,
)

GROUP_2_SYMBOLS = [
    (1, BaseSymbol01_02_001_IndexMiddle),
    (2, BaseSymbol01_02_002_IndexMiddleOnCircle),
    (3, BaseSymbol01_02_003_IndexMiddleBent),
    (4, BaseSymbol01_02_004_IndexMiddleRaisedKnuckles),
    (5, BaseSymbol01_02_005_IndexMiddleHinge),
    (6, BaseSymbol01_02_006_IndexUpMiddleHinge),
    (7, BaseSymbol01_02_007_IndexHingeMiddleUp),
    (8, BaseSymbol01_02_008_IndexMiddleUnit),
    (9, BaseSymbol01_02_009_IndexMiddleUnitIndexBent),
    (10, BaseSymbol01_02_010_IndexMiddleUnitMiddleBent),
    (11, BaseSymbol01_02_011_IndexMiddleUnitCup),
    (12, BaseSymbol01_02_012_IndexMiddleUnitHinge),
    (13, BaseSymbol01_02_013_IndexMiddleCross),
    (14, BaseSymbol01_02_014_IndexMiddleCrossOnCircle),
    (15, BaseSymbol01_02_015_MiddleBentOverIndex),
    (16, BaseSymbol01_02_016_IndexBentOverMiddle),
]
GROUP_2_BASE_HEX = 0x10E  # group 2 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_2_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-02-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_2_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_2_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_2_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_2_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_2_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-02-{base_symbol_number:03d}"

