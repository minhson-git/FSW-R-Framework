"""Behavior-critical regression tests for the rotation/fill -> wrist
quaternion formulas in FSWBaseSymbol._default_wrist_orientation(). These are
generic to every Category 1 base symbol (the formula only depends on
fill/rotation, never on which symbol), so "Index" (01-01-001) is used
throughout as an arbitrary, always-valid (all 6 fills x 16 rotations)
example -- these tests moved here, unchanged in substance, from the old
per-group test_group_01.py when groups/ was replaced by HandSymbol (see
PROGRESS.md's "Refactor tang Group sang data-driven" entry).
"""

from __future__ import annotations

import pytest

from fsw_r.core.hand_symbol import HandSymbol


def _index(fill: int, rotation: int) -> HandSymbol:
    return HandSymbol(category=1, group=1, base_symbol_number=1, fill=fill, rotation=rotation)


def test_wrist_orientation_points_finger_down_at_180_degrees() -> None:
    """ISWA `rotation` changes which way the extended finger itself points,
    like a clock hand on the flat page: 0 degrees = up, 180 degrees = down.
    It is NOT a wrist twist that leaves the finger's direction fixed -- this
    pins that down after the axis was flip-flopped a few times."""
    extension_axis = [0.0, 1.0, 0.0]  # the resting direction of a straight finger

    at_rest = _index(fill=0, rotation=0)
    at_180 = _index(fill=0, rotation=4)  # (4 % 8) * 45 = 180

    assert at_rest.get_wrist_orientation().apply(extension_axis) == pytest.approx([0.0, 1.0, 0.0])
    assert at_180.get_wrist_orientation().apply(extension_axis) == pytest.approx([0.0, -1.0, 0.0])


def test_fill_facing_shows_palm_side_or_back_at_rest() -> None:
    """ISWA fill's lower component (fill % 3) is the "Six Palm Facings":
    which side of the hand faces the viewer. At rest (rotation=0), the palm
    normal starts pointing at the viewer (+z, per hand_geometry's
    convention). fill=1 (Side of Hand) must point to -x, not +x -- a
    concrete, deliberate correction (not derivable from the 2D chart photo
    alone, which has no depth cue to say which edge of the hand faces the
    camera)."""
    palm_normal = [0.0, 0.0, 1.0]

    palm_facing = _index(fill=0, rotation=0)  # Palm of Hand
    side_facing = _index(fill=1, rotation=0)  # Side of Hand
    back_facing = _index(fill=2, rotation=0)  # Back of Hand

    assert palm_facing.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, 0.0, 1.0])
    assert side_facing.get_wrist_orientation().apply(palm_normal) == pytest.approx([-1.0, 0.0, 0.0])
    assert back_facing.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, 0.0, -1.0])


def test_fill_plane_differs_between_wall_and_floor() -> None:
    """ISWA fill's upper component (fill // 3) is Wall Plane (0-2) vs Floor
    Plane (3-5) -- the same Palm/Side/Back facing, but with the whole
    arm/hand pitched 90 degrees. Same facing, different plane must not
    produce the same orientation."""
    wall_palm = _index(fill=0, rotation=0)
    floor_palm = _index(fill=3, rotation=0)

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
    floor_palm = _index(fill=3, rotation=0)

    assert floor_palm.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, 1.0, 0.0])


def test_fill_back_faces_down_in_floor_plane() -> None:
    """fill=5 (Back of Hand, Floor Plane): the top-view camera sees the
    back of the hand, so the palm normal must point straight down -- the
    opposite of fill=3, not the same orientation."""
    palm_normal = [0.0, 0.0, 1.0]
    floor_back = _index(fill=5, rotation=0)

    assert floor_back.get_wrist_orientation().apply(palm_normal) == pytest.approx([0.0, -1.0, 0.0])


def test_fill_side_in_floor_plane_differs_from_palm_and_back() -> None:
    """fill=4 (Side of Hand, Floor Plane) must be visually distinct from
    both fill=3 (Palm) and fill=5 (Back) -- not collapsed onto either.
    Sign matches fill=1's -x correction (same facing component, fill%3=1)."""
    palm_normal = [0.0, 0.0, 1.0]
    floor_side = _index(fill=4, rotation=0)

    result = floor_side.get_wrist_orientation().apply(palm_normal)
    assert result == pytest.approx([-1.0, 0.0, 0.0])
