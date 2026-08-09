"""Category 4 Group 22 head-orientation symbols: the static "Face Direction
Position" symbols and the plain head outline. Unlike a facial *expression*
(a blend-shape, see ``FaceSymbol``), a head symbol is a rigid 3D orientation
of the head -- so this returns a ``Rotation`` (quaternion), the way
``HandSymbol`` returns a wrist orientation.

** Grounded in, but not numerically dictated by, the source. ** The
SEMANTICS come from *Lessons in SignWriting* (Sutton/Parkhurst), Lesson 10
("Head movements", pp. 150-152), read directly:
  - head tips up to look up / down to look down  -> PITCH (nod, "yes"),
  - head turns side to side ("no")               -> YAW,
  - head tilts to the side, "the nose follows a diagonal line instead of a
    vertical line"                                -> ROLL.
The head symbol's ``rotation`` points the nose in a direction (rot 0 = up,
counter-clockwise, the same compass Category 1 and eyegaze use, verified
against the glyph). This module maps that nose direction to pitch/yaw/roll
per the rules above. The EXACT per-rotation angles below are this project's
interpretation of that documented semantics -- the textbook gives the
directions, not the degrees -- exactly the same standing as Category 1's
wrist-orientation formula (chart-grounded, numerically ours). Movement head
symbols (nod/shake/tilt *arrows*, 0x301-0x306) are dynamic and are not here;
they stay ``AnnotationSymbol`` until an expression-over-time model exists.
"""

from __future__ import annotations

import math

from scipy.spatial.transform import Rotation

from fsw_r.core.renderable_symbol import FSWHeadRenderable
from fsw_r.core.types import HandSide

# Group 22 bases this models as a rigid head orientation.
_HEAD_STATIC = frozenset({0x2FF, 0x300})  # Head, Head Rims (neutral)
_NOSE_FORWARD_TILTING = 0x307  # 04-22-009
_NOSE_UP_DOWN = 0x308  # 04-22-010 (pitch + yaw)
_NOSE_UP_DOWN_TILTING = 0x309  # 04-22-011 (pitch + roll)
HEAD_ORIENTATION_BASES: frozenset[int] = _HEAD_STATIC | {
    _NOSE_FORWARD_TILTING,
    _NOSE_UP_DOWN,
    _NOSE_UP_DOWN_TILTING,
}

# Illustrative magnitudes (degrees) for the interpreted mapping.
_PITCH = 35.0
_YAW = 35.0
_ROLL = 30.0


def head_orientation(base_hex: int, rotation: int) -> Rotation:
    """Rigid head orientation for a Group 22 head base. Axis convention
    matches the rest of the project: x = left-right, y = up, z = toward the
    viewer. Pitch about x, yaw about y, roll about z."""
    if base_hex in _HEAD_STATIC:
        return Rotation.identity()

    theta = math.radians((rotation % 8) * 45.0)  # 0 = nose up, CCW
    vertical = math.cos(theta)  # +1 nose up, -1 nose down
    horizontal = math.sin(theta)  # +1 nose toward viewer-left

    # Sign chosen so the nose (face-forward, +z) actually points where the
    # glyph's nose does: up -> +y, viewer-left -> -x (verified by rendering).
    pitch = Rotation.from_euler("x", -_PITCH * vertical, degrees=True)

    if base_hex == _NOSE_FORWARD_TILTING:
        # "Forward tilting": head leaned forward (look down, nose -y);
        # rotation 1 adds a side tilt. Only two rotations exist for this base.
        forward = Rotation.from_euler("x", _PITCH, degrees=True)
        roll = Rotation.from_euler("z", _ROLL * (rotation % 8), degrees=True)
        return roll * forward
    if base_hex == _NOSE_UP_DOWN_TILTING:
        # Diagonal nose -> tilt (roll) for the horizontal component.
        roll = Rotation.from_euler("z", _ROLL * horizontal, degrees=True)
        return roll * pitch
    # _NOSE_UP_DOWN: sideways nose -> turn (yaw).
    yaw = Rotation.from_euler("y", -_YAW * horizontal, degrees=True)
    return yaw * pitch


class HeadSymbol(FSWHeadRenderable):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        """A head symbol encodes no performing hand."""
        return None

    def get_head_orientation(self) -> Rotation:
        return head_orientation(self.base_hex, self.rotation)
