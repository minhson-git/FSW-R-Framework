from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_03_index_middle_thumb import (
    BaseSymbol01_03_001_IndexMiddleThumb,
    BaseSymbol01_03_002_IndexMiddleThumbOnCircle,
    BaseSymbol01_03_003_IndexMiddleStraightThumbBent,
    BaseSymbol01_03_004_IndexMiddleBentThumbStraight,
    BaseSymbol01_03_005_IndexMiddleThumbBent,
    BaseSymbol01_03_006_IndexMiddleHingeSpreadThumbSide,
    BaseSymbol01_03_007_IndexUpMiddleHingeThumbSide,
    BaseSymbol01_03_008_IndexUpMiddleHingeThumbTight,
    BaseSymbol01_03_009_IndexHingeMiddleUpThumbSide,
    BaseSymbol01_03_010_IndexMiddleUpSpreadThumbForward,
    BaseSymbol01_03_011_IndexMiddleThumbCup,
    BaseSymbol01_03_012_IndexMiddleThumbCircle,
    BaseSymbol01_03_013_IndexMiddleThumbHook,
    BaseSymbol01_03_014_IndexMiddleThumbHinge,
    BaseSymbol01_03_015_ThumbBetweenIndexMiddle,
    BaseSymbol01_03_016_IndexMiddleUnitThumbSide,
    BaseSymbol01_03_017_IndexMiddleUnitThumbTight,
    BaseSymbol01_03_018_IndexMiddleUnitThumbBent,
    BaseSymbol01_03_019_MiddleThumbHookIndexUp,
    BaseSymbol01_03_020_IndexThumbHookMiddleUp,
    BaseSymbol01_03_021_IndexMiddleUnitHingeThumbSide,
    BaseSymbol01_03_022_IndexMiddleCrossThumbSide,
    BaseSymbol01_03_023_IndexMiddleUnitThumbForward,
    BaseSymbol01_03_024_IndexMiddleUnitCupThumbForward,
    BaseSymbol01_03_025_MiddleThumbCupIndexUp,
    BaseSymbol01_03_026_IndexThumbCupMiddleUp,
    BaseSymbol01_03_027_MiddleThumbCircleIndexUp,
    BaseSymbol01_03_028_MiddleThumbCircleIndexHinge,
    BaseSymbol01_03_029_IndexThumbAngleOutMiddleUp,
    BaseSymbol01_03_030_IndexThumbAngleInMiddleUp,
    BaseSymbol01_03_031_IndexThumbCircleMiddleUp,
    BaseSymbol01_03_032_IndexMiddleThumbUnitHinge,
    BaseSymbol01_03_033_IndexMiddleThumbAngleOut,
    BaseSymbol01_03_034_IndexMiddleThumbAngle,
    BaseSymbol01_03_035_MiddleThumbAngleOutIndexUp,
    BaseSymbol01_03_036_MiddleThumbAngleOutIndexCrossed,
    BaseSymbol01_03_037_MiddleThumbAngleIndexUp,
    BaseSymbol01_03_038_IndexThumbHookMiddleAngle,
)

GROUP_3_SYMBOLS = [
    (1, BaseSymbol01_03_001_IndexMiddleThumb),
    (2, BaseSymbol01_03_002_IndexMiddleThumbOnCircle),
    (3, BaseSymbol01_03_003_IndexMiddleStraightThumbBent),
    (4, BaseSymbol01_03_004_IndexMiddleBentThumbStraight),
    (5, BaseSymbol01_03_005_IndexMiddleThumbBent),
    (6, BaseSymbol01_03_006_IndexMiddleHingeSpreadThumbSide),
    (7, BaseSymbol01_03_007_IndexUpMiddleHingeThumbSide),
    (8, BaseSymbol01_03_008_IndexUpMiddleHingeThumbTight),
    (9, BaseSymbol01_03_009_IndexHingeMiddleUpThumbSide),
    (10, BaseSymbol01_03_010_IndexMiddleUpSpreadThumbForward),
    (11, BaseSymbol01_03_011_IndexMiddleThumbCup),
    (12, BaseSymbol01_03_012_IndexMiddleThumbCircle),
    (13, BaseSymbol01_03_013_IndexMiddleThumbHook),
    (14, BaseSymbol01_03_014_IndexMiddleThumbHinge),
    (15, BaseSymbol01_03_015_ThumbBetweenIndexMiddle),
    (16, BaseSymbol01_03_016_IndexMiddleUnitThumbSide),
    (17, BaseSymbol01_03_017_IndexMiddleUnitThumbTight),
    (18, BaseSymbol01_03_018_IndexMiddleUnitThumbBent),
    (19, BaseSymbol01_03_019_MiddleThumbHookIndexUp),
    (20, BaseSymbol01_03_020_IndexThumbHookMiddleUp),
    (21, BaseSymbol01_03_021_IndexMiddleUnitHingeThumbSide),
    (22, BaseSymbol01_03_022_IndexMiddleCrossThumbSide),
    (23, BaseSymbol01_03_023_IndexMiddleUnitThumbForward),
    (24, BaseSymbol01_03_024_IndexMiddleUnitCupThumbForward),
    (25, BaseSymbol01_03_025_MiddleThumbCupIndexUp),
    (26, BaseSymbol01_03_026_IndexThumbCupMiddleUp),
    (27, BaseSymbol01_03_027_MiddleThumbCircleIndexUp),
    (28, BaseSymbol01_03_028_MiddleThumbCircleIndexHinge),
    (29, BaseSymbol01_03_029_IndexThumbAngleOutMiddleUp),
    (30, BaseSymbol01_03_030_IndexThumbAngleInMiddleUp),
    (31, BaseSymbol01_03_031_IndexThumbCircleMiddleUp),
    (32, BaseSymbol01_03_032_IndexMiddleThumbUnitHinge),
    (33, BaseSymbol01_03_033_IndexMiddleThumbAngleOut),
    (34, BaseSymbol01_03_034_IndexMiddleThumbAngle),
    (35, BaseSymbol01_03_035_MiddleThumbAngleOutIndexUp),
    (36, BaseSymbol01_03_036_MiddleThumbAngleOutIndexCrossed),
    (37, BaseSymbol01_03_037_MiddleThumbAngleIndexUp),
    (38, BaseSymbol01_03_038_IndexThumbHookMiddleAngle),
]
GROUP_3_BASE_HEX = 0x11E  # group 3 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_3_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-03-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_3_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_3_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_3_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_3_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_3_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-03-{base_symbol_number:03d}"

