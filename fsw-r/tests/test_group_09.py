from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_09_index_thumb import (
    BaseSymbol01_09_001_MiddleRingBaby,
    BaseSymbol01_09_002_MiddleRingBabyOnCircle,
    BaseSymbol01_09_003_MiddleRingBabyOnCurlicue,
    BaseSymbol01_09_004_MiddleRingBabyOnCup,
    BaseSymbol01_09_005_MiddleRingBabyOnHinge,
    BaseSymbol01_09_006_MiddleRingBabyOnAngleOut,
    BaseSymbol01_09_007_MiddleRingBabyOnAngleIn,
    BaseSymbol01_09_008_MiddleRingBabyOnAngle,
    BaseSymbol01_09_009_MiddleRingBabyBent,
    BaseSymbol01_09_010_MiddleRingBabyUnitOnClaw,
    BaseSymbol01_09_011_MiddleRingBabyUnitOnClawSide,
    BaseSymbol01_09_012_MiddleRingBabyUnitOnHookOut,
    BaseSymbol01_09_013_MiddleRingBabyUnitOnHookIn,
    BaseSymbol01_09_014_MiddleRingBabyUnitOnHook,
    BaseSymbol01_09_015_IndexHinge,
    BaseSymbol01_09_016_IndexThumbSide,
    BaseSymbol01_09_017_IndexThumbSideOnHinge,
    BaseSymbol01_09_018_IndexThumbSideThumbDiagonal,
    BaseSymbol01_09_019_IndexThumbSideThumbUnit,
    BaseSymbol01_09_020_IndexThumbSideThumbBent,
    BaseSymbol01_09_021_IndexThumbSideIndexBent,
    BaseSymbol01_09_022_IndexThumbSideBothBent,
    BaseSymbol01_09_023_IndexThumbSideIndexHinge,
    BaseSymbol01_09_024_IndexThumbForwardIndexStraight,
    BaseSymbol01_09_025_IndexThumbForwardIndexBent,
    BaseSymbol01_09_026_IndexThumbHook,
    BaseSymbol01_09_027_IndexThumbCurlicue,
    BaseSymbol01_09_028_IndexThumbCurveThumbSide,
    BaseSymbol01_09_029_IndexThumbCurveThumbInsideOnClaw,
    BaseSymbol01_09_030_IndexThumbCurveThumbUnder,
    BaseSymbol01_09_031_IndexThumbCircle,
    BaseSymbol01_09_032_IndexThumbCup,
    BaseSymbol01_09_033_IndexThumbCupOpen,
    BaseSymbol01_09_034_IndexThumbHingeOpen,
    BaseSymbol01_09_035_IndexThumbHingeLarge,
    BaseSymbol01_09_036_IndexThumbHinge,
    BaseSymbol01_09_037_IndexThumbHingeSmall,
    BaseSymbol01_09_038_IndexThumbAngleOut,
    BaseSymbol01_09_039_IndexThumbAngleIn,
    BaseSymbol01_09_040_IndexThumbAngle,
)

GROUP_9_SYMBOLS = [
    (1, BaseSymbol01_09_001_MiddleRingBaby),
    (2, BaseSymbol01_09_002_MiddleRingBabyOnCircle),
    (3, BaseSymbol01_09_003_MiddleRingBabyOnCurlicue),
    (4, BaseSymbol01_09_004_MiddleRingBabyOnCup),
    (5, BaseSymbol01_09_005_MiddleRingBabyOnHinge),
    (6, BaseSymbol01_09_006_MiddleRingBabyOnAngleOut),
    (7, BaseSymbol01_09_007_MiddleRingBabyOnAngleIn),
    (8, BaseSymbol01_09_008_MiddleRingBabyOnAngle),
    (9, BaseSymbol01_09_009_MiddleRingBabyBent),
    (10, BaseSymbol01_09_010_MiddleRingBabyUnitOnClaw),
    (11, BaseSymbol01_09_011_MiddleRingBabyUnitOnClawSide),
    (12, BaseSymbol01_09_012_MiddleRingBabyUnitOnHookOut),
    (13, BaseSymbol01_09_013_MiddleRingBabyUnitOnHookIn),
    (14, BaseSymbol01_09_014_MiddleRingBabyUnitOnHook),
    (15, BaseSymbol01_09_015_IndexHinge),
    (16, BaseSymbol01_09_016_IndexThumbSide),
    (17, BaseSymbol01_09_017_IndexThumbSideOnHinge),
    (18, BaseSymbol01_09_018_IndexThumbSideThumbDiagonal),
    (19, BaseSymbol01_09_019_IndexThumbSideThumbUnit),
    (20, BaseSymbol01_09_020_IndexThumbSideThumbBent),
    (21, BaseSymbol01_09_021_IndexThumbSideIndexBent),
    (22, BaseSymbol01_09_022_IndexThumbSideBothBent),
    (23, BaseSymbol01_09_023_IndexThumbSideIndexHinge),
    (24, BaseSymbol01_09_024_IndexThumbForwardIndexStraight),
    (25, BaseSymbol01_09_025_IndexThumbForwardIndexBent),
    (26, BaseSymbol01_09_026_IndexThumbHook),
    (27, BaseSymbol01_09_027_IndexThumbCurlicue),
    (28, BaseSymbol01_09_028_IndexThumbCurveThumbSide),
    (29, BaseSymbol01_09_029_IndexThumbCurveThumbInsideOnClaw),
    (30, BaseSymbol01_09_030_IndexThumbCurveThumbUnder),
    (31, BaseSymbol01_09_031_IndexThumbCircle),
    (32, BaseSymbol01_09_032_IndexThumbCup),
    (33, BaseSymbol01_09_033_IndexThumbCupOpen),
    (34, BaseSymbol01_09_034_IndexThumbHingeOpen),
    (35, BaseSymbol01_09_035_IndexThumbHingeLarge),
    (36, BaseSymbol01_09_036_IndexThumbHinge),
    (37, BaseSymbol01_09_037_IndexThumbHingeSmall),
    (38, BaseSymbol01_09_038_IndexThumbAngleOut),
    (39, BaseSymbol01_09_039_IndexThumbAngleIn),
    (40, BaseSymbol01_09_040_IndexThumbAngle),
]
GROUP_9_BASE_HEX = 0x1CD  # group 9 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_9_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-09-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_9_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_9_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_9_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_9_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_9_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-09-{base_symbol_number:03d}"

