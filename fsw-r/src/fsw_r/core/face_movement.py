"""Category 4 facial *movements* as an expression-over-time: a blink, a jaw
opening, a tongue lick... modelled as a time-varying ``FaceExpressionPose``
(ARKit-52 blend-shapes as a function of t in [0, 1]) -- the facial analogue
of Category 2's ``MotionPath``.

WHAT each movement is comes from its authoritative ISWA name (signbank.org):
"Eye Blink Single", "Eye Blinks Multiple", "Eyes Widening Movement", "Nose
Wiggles", "Jaw Movement Wall/Floor Plane", "Tongue Licks Lips", "Tongue
Moves Against Cheek". HOW it varies over time (the temporal profile below --
a single sine pulse for a one-shot motion, a faster oscillation for a
repeated one) is this project's interpretation, exactly as Category 2's
canonical path shapes are (see ``movement_paths.py``'s unverified-assumption
note). Only movements with a real ARKit-52 target are modelled here; teeth
movements and eyelash flutter (no ARKit target) stay ``AnnotationSymbol``.
"""

from __future__ import annotations

import math

from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.renderable_symbol import FSWFaceRenderable
from fsw_r.core.types import HandSide

# base_hex -> ISWA name, for the ARKit-representable facial movements.
_MOVEMENT_NAMES: dict[int, str] = {
    0x317: "Eye Blink Single",
    0x318: "Eye Blinks Multiple",
    0x31C: "Eyes Widening Movement",
    0x334: "Nose Wiggles",
    0x35A: "Tongue Licks Lips",
    0x35E: "Tongue Moves Against Cheek",
    0x368: "Jaw Movement Wall Plane",
    0x369: "Jaw Movement Floor Plane",
}
FACE_MOVEMENT_BASES: frozenset[int] = frozenset(_MOVEMENT_NAMES)


def _pulse(t: float) -> float:
    """One smooth there-and-back motion: 0 at the ends, 1 in the middle."""
    return math.sin(math.pi * t)


def _oscillation(t: float, cycles: float) -> float:
    """A repeated there-and-back motion (``cycles`` peaks over [0, 1])."""
    return abs(math.sin(math.pi * cycles * t))


def movement_expression_at(base_hex: int, t: float) -> FaceExpressionPose:
    """ARKit-52 blend-shapes for this facial movement at time ``t`` in
    [0, 1]. See module docstring for what's sourced vs interpreted."""
    if base_hex == 0x317:  # Eye Blink Single
        b = _pulse(t)
        return FaceExpressionPose({"eyeBlinkLeft": b, "eyeBlinkRight": b})
    if base_hex == 0x318:  # Eye Blinks Multiple
        b = _oscillation(t, 3)
        return FaceExpressionPose({"eyeBlinkLeft": b, "eyeBlinkRight": b})
    if base_hex == 0x31C:  # Eyes Widening Movement
        w = round(0.8 * t, 3)
        return FaceExpressionPose({"eyeWideLeft": w, "eyeWideRight": w})
    if base_hex == 0x334:  # Nose Wiggles
        s = round(0.6 * _oscillation(t, 3), 3)
        return FaceExpressionPose({"noseSneerLeft": s, "noseSneerRight": s})
    if base_hex == 0x35A:  # Tongue Licks Lips
        return FaceExpressionPose({"tongueOut": round(0.9 * _pulse(t), 3)})
    if base_hex == 0x35E:  # Tongue Moves Against Cheek
        return FaceExpressionPose({"tongueOut": 0.4, "cheekPuff": round(0.6 * _oscillation(t, 2), 3)})
    if base_hex == 0x368:  # Jaw Movement Wall Plane (open/close)
        return FaceExpressionPose({"jawOpen": round(0.6 * _pulse(t), 3)})
    if base_hex == 0x369:  # Jaw Movement Floor Plane (side to side)
        s = math.sin(2 * math.pi * t)
        return FaceExpressionPose({"jawRight": round(0.5 * max(s, 0.0), 3), "jawLeft": round(0.5 * max(-s, 0.0), 3)})
    raise ValueError(f"0x{base_hex:03x} is not a modelled facial movement")


class FaceMovementSymbol(FSWFaceRenderable):
    """A facial-expression movement. ``get_expression()`` returns the peak
    (mid-motion) frame, so a static viewer still shows something meaningful;
    ``expression_at(t)`` drives an animation."""

    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        return None

    @property
    def name(self) -> str:
        return _MOVEMENT_NAMES[self.base_hex]

    def expression_at(self, t: float) -> FaceExpressionPose:
        return movement_expression_at(self.base_hex, t)

    def get_expression(self) -> FaceExpressionPose:
        return movement_expression_at(self.base_hex, 0.5)
