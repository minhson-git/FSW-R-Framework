"""Category 4 Group 22 head *movements* (04-22-003..008): the head
orientation over time -- a nod, a shake, a tilt, a circling head -- the head
analogue of ``face_movement.py``. ``orientation_at(t)`` returns a
``Rotation`` for t in [0, 1]; ``get_head_orientation()`` returns the peak
frame so a static viewer still shows the motion's extreme.

Semantics from *Lessons in SignWriting* Lesson 10 (pp. 150-152, read
directly): nod up/down ("yes") = PITCH, shake side-to-side ("no") = YAW,
tilt (nose on a diagonal) = ROLL; wall vs floor plane and straight/curve/
circle mirror the path vocabulary. The base names give WHAT (Straight/Tilts/
Curves/Circles x Wall/Floor); the exact per-frame angles are this project's
interpretation, same standing as Category 2's path shapes.
"""

from __future__ import annotations

import math

from scipy.spatial.transform import Rotation

from fsw_r.core.head_symbol import _PITCH, _ROLL, _YAW
from fsw_r.core.renderable_symbol import FSWHeadRenderable
from fsw_r.core.types import HandSide

_HEAD_MOVEMENT_NAMES: dict[int, str] = {
    0x301: "Head Movement Straight Wall Plane",
    0x302: "Head Movement Tilts Wall Plane",
    0x303: "Head Movement Straight Floor Plane",
    0x304: "Head Movement Curves Wall Plane",
    0x305: "Head Movement Curves Floor Plane",
    0x306: "Head Movement Circles",
}
HEAD_MOVEMENT_BASES: frozenset[int] = frozenset(_HEAD_MOVEMENT_NAMES)


def head_movement_orientation_at(base_hex: int, t: float) -> Rotation:
    """Head orientation at time ``t`` in [0, 1] for a head-movement base.
    One there-and-back cycle over the interval."""
    phase = math.sin(2 * math.pi * t)
    if base_hex == 0x301:  # Straight Wall: nod up/down (pitch)
        return Rotation.from_euler("x", _PITCH * phase, degrees=True)
    if base_hex == 0x302:  # Tilts Wall: side tilt (roll)
        return Rotation.from_euler("z", _ROLL * phase, degrees=True)
    if base_hex == 0x303:  # Straight Floor: turn/shake (yaw)
        return Rotation.from_euler("y", _YAW * phase, degrees=True)
    if base_hex == 0x304:  # Curves Wall: pitch + roll
        return Rotation.from_euler("x", _PITCH * phase, degrees=True) * Rotation.from_euler(
            "z", _ROLL * math.cos(2 * math.pi * t), degrees=True
        )
    if base_hex == 0x305:  # Curves Floor: yaw + pitch
        return Rotation.from_euler("y", _YAW * phase, degrees=True) * Rotation.from_euler(
            "x", _PITCH * math.cos(2 * math.pi * t), degrees=True
        )
    if base_hex == 0x306:  # Circles: nose traces a circle (pitch x yaw)
        return Rotation.from_euler("y", _YAW * math.sin(2 * math.pi * t), degrees=True) * Rotation.from_euler(
            "x", _PITCH * math.cos(2 * math.pi * t), degrees=True
        )
    raise ValueError(f"0x{base_hex:03x} is not a head-movement base")


class HeadMovementSymbol(FSWHeadRenderable):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        return None

    @property
    def name(self) -> str:
        return _HEAD_MOVEMENT_NAMES[self.base_hex]

    def orientation_at(self, t: float) -> Rotation:
        return head_movement_orientation_at(self.base_hex, t)

    def get_head_orientation(self) -> Rotation:
        return head_movement_orientation_at(self.base_hex, 0.25)  # first extreme
