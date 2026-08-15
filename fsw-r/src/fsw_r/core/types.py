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
    """The movement primitives Category 2 (Movement)'s 242 base symbols
    reduce to. The first 5 (CONTACT..CIRCLE) were this project's original
    (group name x plane) reading -- see ``core/movement_paths.py``/
    PROGRESS.md's Phase 2 entry. The rest were added by the "`path_type` từ
    tên BASE SYMBOL" task after discovering that GROUP name only states the
    *plane*, not the *shape* -- e.g. group 02-03 ("Straight Wall Plane")
    alone contains 43 base symbols named Zigzag, Box, Check, Corner, Bend,
    Travel Rotation, ... that a group-name-only reading had all been
    silently calling "straight". Each value below is grounded in a real
    ISWA base-symbol NAME family from ``data/iswa_base_symbol_names.json``
    (signbank.org) -- see ``scripts/gen_movement_paths.py``'s name->PathType
    mapping table for the exact keyword each one comes from, and
    PROGRESS.md's entry for that task for the full before/after counts.
    Deliberately does NOT distinguish Small/Medium/Large/Largest or
    Single/Double/Triple/Alternating variants of the same name family --
    those are ``amplitude``/``repeat`` (a size or a rep count), not a
    different trajectory *shape* (see that task's brief's own principle:
    "hai tên chỉ khác nhau ở kích thước thì đó là amplitude, không phải
    path_type")."""

    CONTACT = "contact"  # degenerate trajectory: a single point
    FINGER = "finger"  # local oscillation, no translation
    STRAIGHT = "straight"  # "(Single/Double/Triple/Alternating) Straight Movement", "Diagonal Away/Towards/Between"
    CURVED = "curved"  # "Curve ... Quarter/Half/3 Quarter Circle/Combined", "Curve Hits ..."
    CIRCLE = "circle"  # "Rotation (Single/Double/Alternating)", "Arm/Wrist/Finger Circle(s)"
    FLEX = "flex"  # "(Single/Double/Triple/Alternating) Wrist Flex" -- mostly straight, hooks near the end
    CROSS = "cross"  # "Cross Movement" -- path crosses the central travel axis
    BEND = "bend"  # "Bend" -- one gentle direction change partway
    CORNER = "corner"  # "Corner (with Rotation)" -- one sharp (near-right-angle) direction change
    CHECK = "check"  # "Check" -- an asymmetric tick/checkmark (short stroke, then a longer one back)
    BOX = "box"  # "Box" -- a closed 4-sided path
    ZIGZAG = "zigzag"  # "Zigzag" -- several alternating diagonal segments while advancing
    PEAKS = "peaks"  # "Peaks" -- a triangle-wave of up/down peaks while advancing
    TRAVEL_ROTATION = "travel_rotation"  # "Travel Rotation" -- constant-radius loop while advancing (a helix)
    SHAKE = "shake"  # "(Travel) Shaking", "Shaking Parallel Floor" -- a tight, high-frequency wiggle
    SPIRAL = "spiral"  # "Travel Arm Spiral" -- an expanding-radius loop while advancing
    HUMP = "hump"  # "Hump" -- a single bump that returns to baseline (unlike CURVED's smooth arc)
    LOOP = "loop"  # "Loop" -- one small self-crossing loop with a little net travel
    WAVE = "wave"  # "Wave ... 2/3 Curves", "Wave Diagonal Path", "Wave Floor Plane Snake"
    CURVE_THEN_STRAIGHT = "curve_then_straight"  # "Curve Then Straight Movement" -- one compound path
    CURVED_CROSS = "curved_cross"  # "Curved Cross Movement" -- CROSS traced with curved, not straight, strokes
    ARROWHEAD = "arrowhead"  # "Arrowheads" -- a chevron/pointer shape (Circles group's one non-circular outlier)


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
    curvature/amplitude/repeat values).

    **``path_type`` comes from each base symbol's own real ISWA NAME**
    (``data/iswa_base_symbol_names.json``, ``scripts/gen_movement_paths.py``
    -- the "`path_type` từ tên BASE SYMBOL" task), NOT from its group name
    anymore -- ``plane``/``is_hit`` are still derived from the group (Part 0
    of that task's brief found only ``path_type`` wrong, not those two).
    See PROGRESS.md's entry for that task for the full name->PathType
    mapping and the before/after counts."""

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
