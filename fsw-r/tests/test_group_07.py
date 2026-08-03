from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_07_ring_finger import (
    BaseSymbol01_07_001_IndexMiddleBaby,
    BaseSymbol01_07_002_IndexMiddleBabyOnCircle,
    BaseSymbol01_07_003_IndexMiddleBabyOnHinge,
    BaseSymbol01_07_004_RingHinge,
    BaseSymbol01_07_005_IndexMiddleBabyOnAngle,
    BaseSymbol01_07_006_IndexMiddleCrossWithBaby,
    BaseSymbol01_07_007_IndexMiddleCrossWithBabyOnCircle,
    BaseSymbol01_07_008_RingDown,
    BaseSymbol01_07_009_RingDownIndexThumbHookMiddleHinge,
    BaseSymbol01_07_010_RingDownMiddleThumbAngleIndexCross,
    BaseSymbol01_07_011_RingUp,
    BaseSymbol01_07_012_RingRaisedKnuckle,
    BaseSymbol01_07_013_RingBaby,
    BaseSymbol01_07_014_RingBabyOnCircle,
    BaseSymbol01_07_015_RingBabyOnOval,
    BaseSymbol01_07_016_RingBabyOnAngle,
    BaseSymbol01_07_017_RingMiddle,
    BaseSymbol01_07_018_RingMiddleUnit,
    BaseSymbol01_07_019_RingMiddleRaisedKnuckles,
    BaseSymbol01_07_020_RingIndex,
    BaseSymbol01_07_021_RingThumb,
    BaseSymbol01_07_022_RingThumbHook,
)

GROUP_7_SYMBOLS = [
    (1, BaseSymbol01_07_001_IndexMiddleBaby),
    (2, BaseSymbol01_07_002_IndexMiddleBabyOnCircle),
    (3, BaseSymbol01_07_003_IndexMiddleBabyOnHinge),
    (4, BaseSymbol01_07_004_RingHinge),
    (5, BaseSymbol01_07_005_IndexMiddleBabyOnAngle),
    (6, BaseSymbol01_07_006_IndexMiddleCrossWithBaby),
    (7, BaseSymbol01_07_007_IndexMiddleCrossWithBabyOnCircle),
    (8, BaseSymbol01_07_008_RingDown),
    (9, BaseSymbol01_07_009_RingDownIndexThumbHookMiddleHinge),
    (10, BaseSymbol01_07_010_RingDownMiddleThumbAngleIndexCross),
    (11, BaseSymbol01_07_011_RingUp),
    (12, BaseSymbol01_07_012_RingRaisedKnuckle),
    (13, BaseSymbol01_07_013_RingBaby),
    (14, BaseSymbol01_07_014_RingBabyOnCircle),
    (15, BaseSymbol01_07_015_RingBabyOnOval),
    (16, BaseSymbol01_07_016_RingBabyOnAngle),
    (17, BaseSymbol01_07_017_RingMiddle),
    (18, BaseSymbol01_07_018_RingMiddleUnit),
    (19, BaseSymbol01_07_019_RingMiddleRaisedKnuckles),
    (20, BaseSymbol01_07_020_RingIndex),
    (21, BaseSymbol01_07_021_RingThumb),
    (22, BaseSymbol01_07_022_RingThumbHook),
]
GROUP_7_BASE_HEX = 0x1A4  # group 7 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_7_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-07-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_7_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_7_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_7_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_7_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_7_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-07-{base_symbol_number:03d}"

