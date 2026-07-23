"""Immutable data types describing a hand pose for 3D rendering.

These types are renderer-agnostic: they only describe joint angles, not how
any specific 3D engine (Blender, Open3D, three.js, ...) applies them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HandSide(str, Enum):
    RIGHT = "right"
    LEFT = "left"


@dataclass(frozen=True)
class JointAngle:
    """Rotation at a single joint, in degrees. 0 = fully extended (straight)."""

    flexion: float
    abduction: float = 0.0  # only meaningful at the MCP joint (finger spread)


@dataclass(frozen=True)
class FingerPose:
    mcp: JointAngle  # Metacarpophalangeal
    pip: JointAngle  # Proximal interphalangeal
    dip: JointAngle  # Distal interphalangeal


@dataclass(frozen=True)
class ThumbPose:
    cmc: JointAngle  # Carpometacarpal
    mcp: JointAngle
    ip: JointAngle  # Interphalangeal


@dataclass(frozen=True)
class HandJointPose:
    thumb: ThumbPose
    index: FingerPose
    middle: FingerPose
    ring: FingerPose
    pinky: FingerPose
