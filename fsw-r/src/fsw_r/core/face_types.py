"""Immutable data type for a facial-expression pose (ISWA Category 4,
Groups 23-26: Brow/Eyes/Eyegaze, Cheeks/Nose/Breath, Mouth/Lips,
Tongue/Chin/Neck).

Unlike a hand (a rigid skeleton of joint angles, see ``types.py``), a face
is deformed by **blend-shapes** -- named morph targets each driven 0..1.
The target standard here is **ARKit 52** (Decision, see PHASE4_PLAN.md), the
de-facto industry set and also exactly what MediaPipe FaceLandmarker emits,
so a pose here maps straight onto a three.js / Blender face rig without a
translation table.

IMPORTANT -- these values are AUTHORED, not measured. There is no dataset
keying ISWA face symbols to blend-shape coefficients the way
``3d-hands-benchmark`` measured hand joints; each vector is a human reading
of the symbol's documented meaning (name + chart, signbank.org / SignWriting
Alphabet Manual 2010). Confidence is lower than the hand data and every
entry records its own ``source`` -- see ``data/face_expression_poses.json``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

# The 52 ARKit blend-shape names (ARKit `ARFaceAnchor.BlendShapeLocation`),
# grouped: brow(5) + cheek(3) + eye(14) + jaw(4) + mouth(23) + nose(2) +
# tongue(1) = 52. This same set is what MediaPipe FaceLandmarker outputs.
ARKIT_BLENDSHAPES: frozenset[str] = frozenset(
    {
        # brow
        "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
        # cheek
        "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
        # eye
        "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
        "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
        "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
        "eyeWideLeft", "eyeWideRight",
        # jaw
        "jawForward", "jawLeft", "jawOpen", "jawRight",
        # mouth
        "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft",
        "mouthFrownRight", "mouthFunnel", "mouthLeft", "mouthLowerDownLeft",
        "mouthLowerDownRight", "mouthPressLeft", "mouthPressRight", "mouthPucker",
        "mouthRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower",
        "mouthShrugUpper", "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft",
        "mouthStretchRight", "mouthUpperUpLeft", "mouthUpperUpRight",
        # nose
        "noseSneerLeft", "noseSneerRight",
        # tongue
        "tongueOut",
    }
)

assert len(ARKIT_BLENDSHAPES) == 52, "ARKit blend-shape set must have exactly 52 names"


@dataclass(frozen=True)
class FaceExpressionPose:
    """A facial expression as ARKit-52 blend-shape coefficients.

    Only non-zero targets need to be listed; any name absent from
    ``blendshapes`` is implicitly 0 (neutral). Validated on construction:
    every key must be a real ARKit-52 name and every value in [0, 1], so a
    typo or out-of-range weight fails fast at data-load time rather than
    silently rendering nothing.
    """

    blendshapes: Mapping[str, float] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        unknown = set(self.blendshapes) - ARKIT_BLENDSHAPES
        if unknown:
            raise ValueError(f"unknown ARKit blend-shape name(s): {sorted(unknown)}")
        for name, weight in self.blendshapes.items():
            if not (0.0 <= weight <= 1.0):
                raise ValueError(f"blend-shape {name}={weight} out of range [0, 1]")
        # Freeze the mapping so a "frozen" pose really is immutable.
        object.__setattr__(self, "blendshapes", MappingProxyType(dict(self.blendshapes)))
