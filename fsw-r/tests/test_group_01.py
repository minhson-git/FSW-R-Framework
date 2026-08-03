from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_01_index_finger import (
    BaseSymbol01_01_001_Index,
    BaseSymbol01_01_002_IndexOnCircle,
    BaseSymbol01_01_003_IndexOnCup,
    BaseSymbol01_01_004_IndexOnOval,
    BaseSymbol01_01_005_IndexOnHinge,
    BaseSymbol01_01_006_IndexOnAngle,
    BaseSymbol01_01_007_IndexBent,
    BaseSymbol01_01_008_IndexBentOnCircle,
    BaseSymbol01_01_009_IndexBentOnFistThumbUnder,
    BaseSymbol01_01_010_IndexCup,
    BaseSymbol01_01_011_IndexCup,
    BaseSymbol01_01_012_IndexHinge,
    BaseSymbol01_01_013_IndexHingeLow,
    BaseSymbol01_01_014_IndexHingeOnCircle,
)

GROUP_1_SYMBOLS = [
    (1, BaseSymbol01_01_001_Index),
    (2, BaseSymbol01_01_002_IndexOnCircle),
    (3, BaseSymbol01_01_003_IndexOnCup),
    (4, BaseSymbol01_01_004_IndexOnOval),
    (5, BaseSymbol01_01_005_IndexOnHinge),
    (6, BaseSymbol01_01_006_IndexOnAngle),
    (7, BaseSymbol01_01_007_IndexBent),
    (8, BaseSymbol01_01_008_IndexBentOnCircle),
    (9, BaseSymbol01_01_009_IndexBentOnFistThumbUnder),
    (10, BaseSymbol01_01_010_IndexCup),
    (11, BaseSymbol01_01_011_IndexCup),
    (12, BaseSymbol01_01_012_IndexHinge),
    (13, BaseSymbol01_01_013_IndexHingeLow),
    (14, BaseSymbol01_01_014_IndexHingeOnCircle),
]
GROUP_1_BASE_HEX = 0x100  # group 1 starts here, see core/fsw_symbol_key.py


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_1_SYMBOLS)
def test_symbol_id_and_hand_side(base_symbol_number: int, cls: type) -> None:
    right = cls(fill=1, rotation=0)
    left = cls(fill=1, rotation=10)

    assert right.symbol_id == f"01-01-{base_symbol_number:03d}"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_1_SYMBOLS)
def test_joint_pose_identical_across_rotations_and_hand_sides(base_symbol_number: int, cls: type) -> None:
    right_front = cls(fill=1, rotation=0)
    right_side = cls(fill=1, rotation=2)
    left_mirrored = cls(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_1_SYMBOLS)
def test_wrist_orientation_identity_at_rotation_zero(base_symbol_number: int, cls: type) -> None:
    # fill=0 (Palm of Hand, Wall Plane) is the neutral fill -- identity.
    symbol = cls(fill=0, rotation=0)
    assert symbol.get_wrist_orientation().as_quat() == pytest.approx([0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_1_SYMBOLS)
def test_wrist_orientation_differs_by_rotation(base_symbol_number: int, cls: type) -> None:
    front = cls(fill=1, rotation=0)
    side = cls(fill=1, rotation=2)
    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


@pytest.mark.parametrize("base_symbol_number,cls", GROUP_1_SYMBOLS)
def test_symbol_from_fsw_builds_correct_class(base_symbol_number: int, cls: type) -> None:
    base_hex = GROUP_1_BASE_HEX + (base_symbol_number - 1)
    symbol = symbol_from_fsw(f"S{base_hex:03x}12")
    assert isinstance(symbol, cls)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == f"01-01-{base_symbol_number:03d}"


def test_wrist_orientation_points_finger_down_at_180_degrees() -> None:
    """ISWA `rotation` changes which way the extended finger itself points,
    like a clock hand on the flat page: 0 degrees = up, 180 degrees = down.
    It is NOT a wrist twist that leaves the finger's direction fixed -- this
    pins that down after the axis was flip-flopped a few times."""
    extension_axis = [0.0, 1.0, 0.0]  # the resting direction of a straight finger

    at_rest = BaseSymbol01_01_001_Index(fill=0, rotation=0)
    at_180 = BaseSymbol01_01_001_Index(fill=0, rotation=4)  # (4 % 8) * 45 = 180

    assert at_rest.get_wrist_orientation().apply(extension_axis) == pytest.approx([0.0, 1.0, 0.0])
    assert at_180.get_wrist_orientation().apply(extension_axis) == pytest.approx([0.0, -1.0, 0.0])


def test_fill_facing_shows_palm_side_or_back_at_rest() -> None:
    """ISWA fill's lower component (fill % 3) is the "Six Palm Facings":
    which side of the hand faces the viewer. At rest (rotation=0), the palm
    normal starts pointing at the viewer (+z, per hand_geometry's
    convention) -- confirmed against the real chart at
    signwriting.org/lessons/iswa/group01/01-01-001-01.html."""
    palm_normal = [0.0, 0.0, 1.0]

    palm_facing = BaseSymbol01_01_001_Index(fill=0, rotation=0)  # Palm of Hand
    side_facing = BaseSymbol01_01_001_Index(fill=1, rotation=0)  # Side of Hand
    back_facing = BaseSymbol01_01_001_Index(fill=2, rotation=0)  # Back of Hand

    assert palm_facing.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, 0.0, 1.0])
    assert side_facing.get_wrist_orientation().apply(palm_normal) == pytest.approx([1.0, 0.0, 0.0])
    assert back_facing.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, 0.0, -1.0])


def test_fill_plane_differs_between_wall_and_floor() -> None:
    """ISWA fill's upper component (fill // 3) is Wall Plane (0-2) vs Floor
    Plane (3-5) -- the same Palm/Side/Back facing, but with the whole
    arm/hand pitched 90 degrees. Same facing, different plane must not
    produce the same orientation."""
    wall_palm = BaseSymbol01_01_001_Index(fill=0, rotation=0)
    floor_palm = BaseSymbol01_01_001_Index(fill=3, rotation=0)

    wall_quat = wall_palm.get_wrist_orientation().as_quat()
    floor_quat = floor_palm.get_wrist_orientation().as_quat()

    assert wall_quat != pytest.approx(floor_quat)


def test_fill_palm_faces_up_in_floor_plane() -> None:
    """fill=3 (Palm of Hand, Floor Plane): the arm reaches down toward the
    floor and the top-view camera sees the palm -- so the palm normal must
    point straight up, not down. Regression test for a gimbal-lock-style
    bug where applying the plane pitch before the facing twist made fill=3
    and fill=5 produce the same orientation."""
    palm_normal = [0.0, 0.0, 1.0]
    floor_palm = BaseSymbol01_01_001_Index(fill=3, rotation=0)

    assert floor_palm.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, 1.0, 0.0])


def test_fill_back_faces_down_in_floor_plane() -> None:
    """fill=5 (Back of Hand, Floor Plane): the top-view camera sees the
    back of the hand, so the palm normal must point straight down -- the
    opposite of fill=3, not the same orientation."""
    palm_normal = [0.0, 0.0, 1.0]
    floor_back = BaseSymbol01_01_001_Index(fill=5, rotation=0)

    assert floor_back.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, -1.0, 0.0])


def test_fill_side_in_floor_plane_differs_from_palm_and_back() -> None:
    """fill=4 (Side of Hand, Floor Plane) must be visually distinct from
    both fill=3 (Palm) and fill=5 (Back) -- not collapsed onto either."""
    palm_normal = [0.0, 0.0, 1.0]
    floor_side = BaseSymbol01_01_001_Index(fill=4, rotation=0)

    result = floor_side.get_wrist_orientation().apply(palm_normal)
    assert result == pytest.approx([1.0, 0.0, 0.0])


def test_index_bent_overrides_only_index_finger() -> None:
    straight = BaseSymbol01_01_001_Index(fill=1, rotation=0)
    bent = BaseSymbol01_01_007_IndexBent(fill=1, rotation=0)

    straight_pose = straight.get_joint_pose()
    bent_pose = bent.get_joint_pose()

    assert bent_pose.index.pip.flexion == 46
    assert bent_pose.thumb == straight_pose.thumb
    assert bent_pose.middle == straight_pose.middle
    assert bent_pose.ring == straight_pose.ring
    assert bent_pose.pinky == straight_pose.pinky
