from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_06_baby_finger import (
    BaseSymbol01_06_001_IndexMiddleRing,
    BaseSymbol01_06_002_IndexMiddleRingOnCircle,
    BaseSymbol01_06_003_IndexMiddleRingOnHinge,
    BaseSymbol01_06_004_IndexMiddleRingOnAngle,
    BaseSymbol01_06_005_BabyHinge,
    BaseSymbol01_06_006_IndexMiddleRingBent,
    BaseSymbol01_06_007_IndexMiddleRingUnit,
    BaseSymbol01_06_008_IndexMiddleRingUnitHinge,
    BaseSymbol01_06_009_BabyDown,
    BaseSymbol01_06_010_BabyDownRippleStraight,
    BaseSymbol01_06_011_BabyDownRippleCurved,
    BaseSymbol01_06_012_BabyDownOthersCircle,
    BaseSymbol01_06_013_BabyUp,
    BaseSymbol01_06_014_BabyUpOnFistThumbUnder,
    BaseSymbol01_06_015_BabyUpOnCircle,
    BaseSymbol01_06_016_BabyUpOnOval,
    BaseSymbol01_06_017_BabyUpOnAngle,
    BaseSymbol01_06_018_BabyRaisedKnuckle,
    BaseSymbol01_06_019_BabyBent,
    BaseSymbol01_06_020_BabyTouchesThumb,
    BaseSymbol01_06_021_BabyThumb,
    BaseSymbol01_06_022_BabyThumbOnHinge,
    BaseSymbol01_06_023_BabyIndexThumb,
    BaseSymbol01_06_024_BabyIndexThumbOnHinge,
    BaseSymbol01_06_025_BabyIndexThumbAngleOut,
    BaseSymbol01_06_026_BabyIndexThumbIndexThumbAngle,
    BaseSymbol01_06_027_BabyIndex,
    BaseSymbol01_06_028_BabyIndexOnCircle,
    BaseSymbol01_06_029_BabyIndexOnHinge,
    BaseSymbol01_06_030_BabyIndexOnAngle,
)

GROUP_6_SYMBOLS = [
    (1, BaseSymbol01_06_001_IndexMiddleRing),
    (2, BaseSymbol01_06_002_IndexMiddleRingOnCircle),
    (3, BaseSymbol01_06_003_IndexMiddleRingOnHinge),
    (4, BaseSymbol01_06_004_IndexMiddleRingOnAngle),
    (5, BaseSymbol01_06_005_BabyHinge),
    (6, BaseSymbol01_06_006_IndexMiddleRingBent),
    (7, BaseSymbol01_06_007_IndexMiddleRingUnit),
    (8, BaseSymbol01_06_008_IndexMiddleRingUnitHinge),
    (9, BaseSymbol01_06_009_BabyDown),
    (10, BaseSymbol01_06_010_BabyDownRippleStraight),
    (11, BaseSymbol01_06_011_BabyDownRippleCurved),
    (12, BaseSymbol01_06_012_BabyDownOthersCircle),
    (13, BaseSymbol01_06_013_BabyUp),
    (14, BaseSymbol01_06_014_BabyUpOnFistThumbUnder),
    (15, BaseSymbol01_06_015_BabyUpOnCircle),
    (16, BaseSymbol01_06_016_BabyUpOnOval),
    (17, BaseSymbol01_06_017_BabyUpOnAngle),
    (18, BaseSymbol01_06_018_BabyRaisedKnuckle),
    (19, BaseSymbol01_06_019_BabyBent),
    (20, BaseSymbol01_06_020_BabyTouchesThumb),
    (21, BaseSymbol01_06_021_BabyThumb),
    (22, BaseSymbol01_06_022_BabyThumbOnHinge),
    (23, BaseSymbol01_06_023_BabyIndexThumb),
    (24, BaseSymbol01_06_024_BabyIndexThumbOnHinge),
    (25, BaseSymbol01_06_025_BabyIndexThumbAngleOut),
    (26, BaseSymbol01_06_026_BabyIndexThumbIndexThumbAngle),
    (27, BaseSymbol01_06_027_BabyIndex),
    (28, BaseSymbol01_06_028_BabyIndexOnCircle),
    (29, BaseSymbol01_06_029_BabyIndexOnHinge),
    (30, BaseSymbol01_06_030_BabyIndexOnAngle),
]
GROUP_6_BASE_HEX = 0x186  # group 6 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_6_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-06-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_6_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_6_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_6_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_6_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_6_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-06-{base_symbol_number:03d}"

