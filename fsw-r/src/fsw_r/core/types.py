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


class PathType(Enum):
    """The 5 movement primitives Category 2 (Movement)'s 242 base symbols
    reduce to -- see core/movement_paths.py / PROGRESS.md's Phase 2 entry
    for the (path_type x plane) table this was derived from."""

    CONTACT = "contact"  # degenerate trajectory: a single point
    FINGER = "finger"  # local oscillation, no translation
    STRAIGHT = "straight"
    CURVED = "curved"
    CIRCLE = "circle"


class MovementPlane(Enum):
    WALL = "wall"  # parallel to the front wall: the XY plane
    FLOOR = "floor"  # parallel to the floor: the XZ plane
    DIAGONAL = "diagonal"


@dataclass(frozen=True)
class MotionPath:
    """A Category 2 (Movement) symbol's trajectory description -- NOT a
    static pose like HandJointPose. See core/movement_symbol.py and
    PROGRESS.md's Phase 2 entry for the derivation and, importantly, which
    parts of this are still unverified assumptions (``plane`` for groups
    11/12/20, ``is_hit``'s exact semantics, and the default
    curvature/amplitude/repeat values)."""

    path_type: PathType
    plane: MovementPlane | None  # None = derive from rotation (see sample_trajectory())
    curvature: float  # 0 for STRAIGHT
    amplitude: float
    repeat: int  # 1 / 2 / 3
    is_hit: bool
