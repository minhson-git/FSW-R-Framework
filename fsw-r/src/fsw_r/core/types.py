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


@dataclass(frozen=True)
class FingerArticulation:
    """How the FINGER joints move over time, for a Group 12 (Finger
    Movement, ``PathType.FINGER``) symbol -- see this task's brief
    ("Chuyển động khớp ngón tay"), Part 0/B1. UNLIKE ``MotionPath``: the
    WRIST does not translate at all for Group 12 (see
    ``core/movement_paths.py``'s ``sample_trajectory()``, which now
    returns a fixed point for ``PathType.FINGER``, same treatment as
    ``PathType.CONTACT``) -- the movement is entirely in the JOINT ANGLES,
    applied by ``core/finger_articulation.py``'s ``articulate_joint_pose()``
    and wired into keyframe generation by ``timeline/build.py``.

    Every field is AUTHORED (a human reading of the base symbol's real
    ISWA name from signbank.org), not measured -- see
    ``data/finger_articulations.json``'s own ``_meta`` and PROGRESS.md's
    "giả định chưa kiểm chứng" list. No dataset maps ISWA finger-movement
    symbols to numeric joint-angle amplitudes.
    """

    fingers: frozenset[str]  # which fingers participate: 'thumb'/'index'/'middle'/'ring'/'pinky'
    joints: frozenset[str]  # which joints oscillate: 'mcp'/'pip'/'dip' (thumb has no pip/dip -- see finger_articulation.py)
    amplitude_deg: float  # peak deviation from the base flexion angle, in degrees (0 = no motion)
    cycles: float  # number of full oscillation cycles across the WHOLE sign duration
    phase_offset: float  # radians of phase shift PER FINGER, in canonical order -- 0 = every finger moves in sync
