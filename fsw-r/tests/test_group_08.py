from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_08_middle_finger import (
    BaseSymbol01_08_001_IndexRingBaby,
    BaseSymbol01_08_002_IndexRingBabyOnCircle,
    BaseSymbol01_08_003_IndexRingBabyOnCurlicue,
    BaseSymbol01_08_004_IndexRingBabyOnHookOut,
    BaseSymbol01_08_005_IndexRingBabyOnHookIn,
    BaseSymbol01_08_006_IndexRingBabyOnHookUnder,
    BaseSymbol01_08_007_IndexRingBabyOnCup,
    BaseSymbol01_08_008_IndexRingBabyOnHinge,
    BaseSymbol01_08_009_IndexRingBabyOnAngleOut,
    BaseSymbol01_08_010_IndexRingBabyOnAngle,
    BaseSymbol01_08_011_MiddleDown,
    BaseSymbol01_08_012_MiddleHinge,
    BaseSymbol01_08_013_MiddleUp,
    BaseSymbol01_08_014_MiddleUpOnCircle,
    BaseSymbol01_08_015_MiddleRaisedKnuckle,
    BaseSymbol01_08_016_MiddleUpThumbSide,
    BaseSymbol01_08_017_MiddleThumbHook,
    BaseSymbol01_08_018_MiddleThumbBaby,
    BaseSymbol01_08_019_MiddleBaby,
)

GROUP_8_SYMBOLS = [
    (1, BaseSymbol01_08_001_IndexRingBaby),
    (2, BaseSymbol01_08_002_IndexRingBabyOnCircle),
    (3, BaseSymbol01_08_003_IndexRingBabyOnCurlicue),
    (4, BaseSymbol01_08_004_IndexRingBabyOnHookOut),
    (5, BaseSymbol01_08_005_IndexRingBabyOnHookIn),
    (6, BaseSymbol01_08_006_IndexRingBabyOnHookUnder),
    (7, BaseSymbol01_08_007_IndexRingBabyOnCup),
    (8, BaseSymbol01_08_008_IndexRingBabyOnHinge),
    (9, BaseSymbol01_08_009_IndexRingBabyOnAngleOut),
    (10, BaseSymbol01_08_010_IndexRingBabyOnAngle),
    (11, BaseSymbol01_08_011_MiddleDown),
    (12, BaseSymbol01_08_012_MiddleHinge),
    (13, BaseSymbol01_08_013_MiddleUp),
    (14, BaseSymbol01_08_014_MiddleUpOnCircle),
    (15, BaseSymbol01_08_015_MiddleRaisedKnuckle),
    (16, BaseSymbol01_08_016_MiddleUpThumbSide),
    (17, BaseSymbol01_08_017_MiddleThumbHook),
    (18, BaseSymbol01_08_018_MiddleThumbBaby),
    (19, BaseSymbol01_08_019_MiddleBaby),
]
GROUP_8_BASE_HEX = 0x1BA  # group 8 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_8_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-08-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_8_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_8_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_8_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_8_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_8_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-08-{base_symbol_number:03d}"

