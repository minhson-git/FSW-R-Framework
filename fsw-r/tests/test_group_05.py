from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_05_five_fingers import (
    BaseSymbol01_05_001_FiveFingersSpread,
    BaseSymbol01_05_002_FiveFingersSpreadHeel,
    BaseSymbol01_05_003_FiveFingersSpread4Bent,
    BaseSymbol01_05_004_FiveFingersSpreadFourBentHeel,
    BaseSymbol01_05_005_FiveFingersSpreadAllBent,
    BaseSymbol01_05_006_FiveFingersSpreadAllBentHeel,
    BaseSymbol01_05_007_FiveFingersSpreadThumbForward,
    BaseSymbol01_05_008_FiveFingersSpreadCup,
    BaseSymbol01_05_009_FiveFingersSpreadCupOpen,
    BaseSymbol01_05_010_FiveFingersSpreadHingeOpen,
    BaseSymbol01_05_011_FiveFingersSpreadOval,
    BaseSymbol01_05_012_FiveFingersSpreadHinge,
    BaseSymbol01_05_013_FiveFingersSpreadHingeThumbSide,
    BaseSymbol01_05_014_FiveFingersSpreadHingeNoThumb,
    BaseSymbol01_05_015_FlatHand,
    BaseSymbol01_05_016_FlatHandInBetweenPalmFacings,
    BaseSymbol01_05_017_FlatHandHeel,
    BaseSymbol01_05_018_FlatThumbSide,
    BaseSymbol01_05_019_FlatThumbSideHeel,
    BaseSymbol01_05_020_FlatThumbBent,
    BaseSymbol01_05_021_FlatThumbForward,
    BaseSymbol01_05_022_FlatSplitIndexThumbSide,
    BaseSymbol01_05_023_FlatSplitCenter,
    BaseSymbol01_05_024_FlatSplitCenterThumbSide,
    BaseSymbol01_05_025_FlatSplitCenterThumbSideBent,
    BaseSymbol01_05_026_FlatSplitBaby,
    BaseSymbol01_05_027_Claw,
    BaseSymbol01_05_028_ClawThumbSide,
    BaseSymbol01_05_029_ClawNoThumb,
    BaseSymbol01_05_030_ClawThumbForward,
    BaseSymbol01_05_031_HookCurlicue,
    BaseSymbol01_05_032_Hook,
    BaseSymbol01_05_033_OpenCup,
    BaseSymbol01_05_034_Cup,
    BaseSymbol01_05_035_OpenCupThumbSide,
    BaseSymbol01_05_036_CupThumbSide,
    BaseSymbol01_05_037_OpenCupNoThumb,
    BaseSymbol01_05_038_CupNoThumb,
    BaseSymbol01_05_039_OpenCupThumbForward,
    BaseSymbol01_05_040_CupThumbForward,
    BaseSymbol01_05_041_OpenCurlicue,
    BaseSymbol01_05_042_Curlicue,
    BaseSymbol01_05_043_Circle,
    BaseSymbol01_05_044_Oval,
    BaseSymbol01_05_045_OvalThumbSide,
    BaseSymbol01_05_046_OvalNoThumb,
    BaseSymbol01_05_047_OvalThumbForward,
    BaseSymbol01_05_048_OpenHinge,
    BaseSymbol01_05_049_OpenHingeThumbForward,
    BaseSymbol01_05_050_Hinge,
    BaseSymbol01_05_051_SmallHinge,
    BaseSymbol01_05_052_OpenHingeThumbSide,
    BaseSymbol01_05_053_HingeThumbSide,
    BaseSymbol01_05_054_OpenHingeNoThumb,
    BaseSymbol01_05_055_HingeNoThumb,
    BaseSymbol01_05_056_HingeThumbSideTouchesIndex,
    BaseSymbol01_05_057_HingeThumbBetweenMiddleRing,
    BaseSymbol01_05_058_Angle,
)

GROUP_5_SYMBOLS = [
    (1, BaseSymbol01_05_001_FiveFingersSpread),
    (2, BaseSymbol01_05_002_FiveFingersSpreadHeel),
    (3, BaseSymbol01_05_003_FiveFingersSpread4Bent),
    (4, BaseSymbol01_05_004_FiveFingersSpreadFourBentHeel),
    (5, BaseSymbol01_05_005_FiveFingersSpreadAllBent),
    (6, BaseSymbol01_05_006_FiveFingersSpreadAllBentHeel),
    (7, BaseSymbol01_05_007_FiveFingersSpreadThumbForward),
    (8, BaseSymbol01_05_008_FiveFingersSpreadCup),
    (9, BaseSymbol01_05_009_FiveFingersSpreadCupOpen),
    (10, BaseSymbol01_05_010_FiveFingersSpreadHingeOpen),
    (11, BaseSymbol01_05_011_FiveFingersSpreadOval),
    (12, BaseSymbol01_05_012_FiveFingersSpreadHinge),
    (13, BaseSymbol01_05_013_FiveFingersSpreadHingeThumbSide),
    (14, BaseSymbol01_05_014_FiveFingersSpreadHingeNoThumb),
    (15, BaseSymbol01_05_015_FlatHand),
    (16, BaseSymbol01_05_016_FlatHandInBetweenPalmFacings),
    (17, BaseSymbol01_05_017_FlatHandHeel),
    (18, BaseSymbol01_05_018_FlatThumbSide),
    (19, BaseSymbol01_05_019_FlatThumbSideHeel),
    (20, BaseSymbol01_05_020_FlatThumbBent),
    (21, BaseSymbol01_05_021_FlatThumbForward),
    (22, BaseSymbol01_05_022_FlatSplitIndexThumbSide),
    (23, BaseSymbol01_05_023_FlatSplitCenter),
    (24, BaseSymbol01_05_024_FlatSplitCenterThumbSide),
    (25, BaseSymbol01_05_025_FlatSplitCenterThumbSideBent),
    (26, BaseSymbol01_05_026_FlatSplitBaby),
    (27, BaseSymbol01_05_027_Claw),
    (28, BaseSymbol01_05_028_ClawThumbSide),
    (29, BaseSymbol01_05_029_ClawNoThumb),
    (30, BaseSymbol01_05_030_ClawThumbForward),
    (31, BaseSymbol01_05_031_HookCurlicue),
    (32, BaseSymbol01_05_032_Hook),
    (33, BaseSymbol01_05_033_OpenCup),
    (34, BaseSymbol01_05_034_Cup),
    (35, BaseSymbol01_05_035_OpenCupThumbSide),
    (36, BaseSymbol01_05_036_CupThumbSide),
    (37, BaseSymbol01_05_037_OpenCupNoThumb),
    (38, BaseSymbol01_05_038_CupNoThumb),
    (39, BaseSymbol01_05_039_OpenCupThumbForward),
    (40, BaseSymbol01_05_040_CupThumbForward),
    (41, BaseSymbol01_05_041_OpenCurlicue),
    (42, BaseSymbol01_05_042_Curlicue),
    (43, BaseSymbol01_05_043_Circle),
    (44, BaseSymbol01_05_044_Oval),
    (45, BaseSymbol01_05_045_OvalThumbSide),
    (46, BaseSymbol01_05_046_OvalNoThumb),
    (47, BaseSymbol01_05_047_OvalThumbForward),
    (48, BaseSymbol01_05_048_OpenHinge),
    (49, BaseSymbol01_05_049_OpenHingeThumbForward),
    (50, BaseSymbol01_05_050_Hinge),
    (51, BaseSymbol01_05_051_SmallHinge),
    (52, BaseSymbol01_05_052_OpenHingeThumbSide),
    (53, BaseSymbol01_05_053_HingeThumbSide),
    (54, BaseSymbol01_05_054_OpenHingeNoThumb),
    (55, BaseSymbol01_05_055_HingeNoThumb),
    (56, BaseSymbol01_05_056_HingeThumbSideTouchesIndex),
    (57, BaseSymbol01_05_057_HingeThumbBetweenMiddleRing),
    (58, BaseSymbol01_05_058_Angle),
]
GROUP_5_BASE_HEX = 0x14C  # group 5 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_5_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-05-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_5_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_5_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_5_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_5_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_5_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-05-{base_symbol_number:03d}"

