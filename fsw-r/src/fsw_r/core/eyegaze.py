"""Eyegaze direction for Category 4 Group 23's eyegaze symbols
(04-23-024..029, base 0x321-0x326): unlike every other facial symbol, their
``rotation`` is not decoration -- it is the direction the eyes look.

The rotation->direction convention was VERIFIED against the real ISWA glyph
(rendered via the ``signwriting`` package's visualizer, not guessed): the
eyegaze glyph's gaze arrow points, in the viewer's frame,

    rot 0 = up,  2 = viewer-left,  4 = down,  6 = viewer-right

i.e. the same counter-clockwise compass Category 1 uses (0 up, +45 deg per
step CCW), cross-checked against the Index hand glyph at the same rotations.
Diagonals (1/3/5/7) are the in-between directions on that compass.

That viewer-frame direction is mapped to ARKit-52's own (person-frame)
``eyeLook*`` targets here. Horizontal needs the frame flip: gaze to the
VIEWER's left = the signer looking to THEIR right = left eye rotates in
(``eyeLookInLeft``) while the right eye rotates out (``eyeLookOutRight``).
Vertical needs no flip. This mapping is documented, not silently assumed.
"""

from __future__ import annotations

import math

# Base symbols whose expression is a rotation-driven gaze (the six "straight"
# eyegaze bases). The curved/circle eyegaze bases (0x327-0x329) are gaze
# *movements* and are handled as annotations, not a static direction.
EYEGAZE_BASES: frozenset[int] = frozenset(range(0x321, 0x327))


def gaze_blendshapes(rotation: int, amount: float = 0.9) -> dict[str, float]:
    """ARKit-52 ``eyeLook*`` weights for a gaze in the direction ``rotation``
    encodes (see module docstring). Returns only the non-zero targets."""
    angle = math.radians((rotation % 8) * 45.0)  # 0 = up, CCW
    vertical = math.cos(angle)  # +1 up, -1 down
    viewer_left = math.sin(angle)  # +1 viewer-left, -1 viewer-right

    weights: dict[str, float] = {}

    def add(name: str, value: float) -> None:
        if value > 1e-6:
            weights[name] = round(value * amount, 3)

    add("eyeLookUpLeft", vertical)
    add("eyeLookUpRight", vertical)
    add("eyeLookDownLeft", -vertical)
    add("eyeLookDownRight", -vertical)
    # viewer-left gaze = person looks to their right: left eye in, right eye out.
    add("eyeLookInLeft", viewer_left)
    add("eyeLookOutRight", viewer_left)
    # viewer-right gaze = person looks to their left: left eye out, right eye in.
    add("eyeLookOutLeft", -viewer_left)
    add("eyeLookInRight", -viewer_left)
    return weights
