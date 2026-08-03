from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_10_thumb import (
    BaseSymbol01_10_001_Thumb,
    BaseSymbol01_10_002_ThumbHeel,
    BaseSymbol01_10_003_ThumbSideDiagonal,
    BaseSymbol01_10_004_ThumbSideUnit,
    BaseSymbol01_10_005_ThumbSideBent,
    BaseSymbol01_10_006_ThumbForward,
    BaseSymbol01_10_007_ThumbBetweenIndexMiddle,
    BaseSymbol01_10_008_ThumbBetweenMiddleRing,
    BaseSymbol01_10_009_ThumbBetweenRingBaby,
    BaseSymbol01_10_010_ThumbUnderTwoFingers,
    BaseSymbol01_10_011_ThumbOverTwoFingers,
    BaseSymbol01_10_012_ThumbUnderThreeFingers,
    BaseSymbol01_10_013_ThumbUnderFourFingers,
    BaseSymbol01_10_014_ThumbOverFourRaisedKnuckles,
    BaseSymbol01_10_015_Fist,
    BaseSymbol01_10_016_FistHeel,
)

GROUP_10_SYMBOLS = [
    (1, BaseSymbol01_10_001_Thumb),
    (2, BaseSymbol01_10_002_ThumbHeel),
    (3, BaseSymbol01_10_003_ThumbSideDiagonal),
    (4, BaseSymbol01_10_004_ThumbSideUnit),
    (5, BaseSymbol01_10_005_ThumbSideBent),
    (6, BaseSymbol01_10_006_ThumbForward),
    (7, BaseSymbol01_10_007_ThumbBetweenIndexMiddle),
    (8, BaseSymbol01_10_008_ThumbBetweenMiddleRing),
    (9, BaseSymbol01_10_009_ThumbBetweenRingBaby),
    (10, BaseSymbol01_10_010_ThumbUnderTwoFingers),
    (11, BaseSymbol01_10_011_ThumbOverTwoFingers),
    (12, BaseSymbol01_10_012_ThumbUnderThreeFingers),
    (13, BaseSymbol01_10_013_ThumbUnderFourFingers),
    (14, BaseSymbol01_10_014_ThumbOverFourRaisedKnuckles),
    (15, BaseSymbol01_10_015_Fist),
    (16, BaseSymbol01_10_016_FistHeel),
]
GROUP_10_BASE_HEX = 0x1F5  # group 10 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_10_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-10-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_10_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_10_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_10_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_10_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_10_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-10-{base_symbol_number:03d}"

