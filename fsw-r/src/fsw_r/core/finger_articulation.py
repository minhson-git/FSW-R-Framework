"""Applies a ``FingerArticulation``'s per-frame joint-angle oscillation to
a static ``HandJointPose`` -- the Group 12 (Finger Movement) analogue of
``core/movement_paths.py``'s ``sample_trajectory()`` for ``MotionPath``.
Unlike ``MotionPath`` (3D translation), ``FingerArticulation`` describes
JOINT ANGLE oscillation over time with the wrist held still -- see this
task's brief ("Chuyển động khớp ngón tay"), Part 0/C1.

Clamps every oscillated angle to ``validation/anatomical_limits.py``'s
``JOINT_LIMITS`` -- data only, imported and used directly, NOT
``validate_pose()`` -- this task's own constraint ("clamp ở tầng sinh
chuyển động, không sửa validation/"): the clamp happens at the SOURCE
(here, before a frame is ever built), so a rendered pose never violates
the same limits ``validate_pose()`` would flag, without touching
``validation/`` itself or ``hand_joint_poses.json``'s own static data.
"""

from __future__ import annotations

import math

from fsw_r.core.types import FingerArticulation, FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.validation.anatomical_limits import JOINT_LIMITS

# Canonical order used ONLY to distribute FingerArticulation.phase_offset
# across participating fingers (e.g. "Hinge Movement, Up Down Alternating"
# -- 0x225, see data/finger_articulations.json) -- an arbitrary but fixed,
# documented ordering, not derived from any ISWA source.
_FINGER_ORDER = ("thumb", "index", "middle", "ring", "pinky")

_NON_THUMB_JOINTS = ("mcp", "pip", "dip")
_THUMB_JOINTS = ("cmc", "mcp", "ip")


def _joint_key(finger: str, joint: str) -> str:
    """Same (finger, joint) -> JOINT_LIMITS key convention as
    ``validation/anatomical_limits.py``'s own private ``_joint_key`` --
    duplicated here (2 lines) rather than importing that module's private
    name across the ``validation/`` package boundary, per this task's own
    constraint (only USE ``validation/``, never modify it -- importing a
    private helper would create a de facto second public contract on that
    module without it being declared as one)."""
    return "thumb_" + joint if finger == "thumb" else "finger_" + joint


def _clamp_flexion(finger: str, joint: str, value: float) -> float:
    limit = JOINT_LIMITS.get((_joint_key(finger, joint), "flexion"))
    if limit is None:
        return value
    low, high = limit
    return min(max(value, low), high)


def _oscillation_delta(articulation: FingerArticulation, finger: str, t: float) -> float:
    """``amplitude_deg * sin(2*pi*cycles*t + phase)`` -- exactly this
    task's brief formula (Part C1), with ``phase`` distributed across
    fingers by their position in ``_FINGER_ORDER`` (0 for a single-finger
    or in-sync articulation, since ``phase_offset`` itself is 0 unless the
    symbol's real name says "Alternating" -- see the data table)."""
    phase = articulation.phase_offset * _FINGER_ORDER.index(finger)
    return articulation.amplitude_deg * math.sin(2 * math.pi * articulation.cycles * t + phase)


def _articulate_finger(base: FingerPose, finger: str, articulation: FingerArticulation, t: float) -> FingerPose:
    if finger not in articulation.fingers:
        return base
    delta = _oscillation_delta(articulation, finger, t)
    angles = {}
    for joint in _NON_THUMB_JOINTS:
        base_angle: JointAngle = getattr(base, joint)
        if joint in articulation.joints:
            angles[joint] = JointAngle(
                flexion=_clamp_flexion(finger, joint, base_angle.flexion + delta),
                abduction=base_angle.abduction,
            )
        else:
            angles[joint] = base_angle
    return FingerPose(**angles)


def _articulate_thumb(base: ThumbPose, articulation: FingerArticulation, t: float) -> ThumbPose:
    if "thumb" not in articulation.fingers:
        return base
    delta = _oscillation_delta(articulation, "thumb", t)
    # FingerArticulation.joints uses the 4-finger vocabulary (mcp/pip/dip)
    # -- the thumb has no pip/dip (its own joints are cmc/mcp/ip). Only
    # 'mcp' overlaps by name; when it's requested, the WHOLE thumb
    # oscillates together (cmc+mcp+ip), since a thumb "squeeze"/"hinge"
    # curls as one unit, not joint-by-joint independently -- an AUTHORED
    # simplification (none of this task's own 5 leading base symbols
    # apply to the thumb, so this path is exercised only by
    # tests/D5's full 20-base sweep, not by the demo GIF).
    if "mcp" not in articulation.joints:
        return base
    angles = {}
    for joint in _THUMB_JOINTS:
        base_angle: JointAngle = getattr(base, joint)
        angles[joint] = JointAngle(
            flexion=_clamp_flexion("thumb", joint, base_angle.flexion + delta),
            abduction=base_angle.abduction,
        )
    return ThumbPose(**angles)


def articulate_joint_pose(base_pose: HandJointPose, articulation: FingerArticulation, t: float) -> HandJointPose:
    """``base_pose`` (a Category 1 symbol's static joint angles, unchanged
    -- this never mutates ``hand_joint_poses.json``'s data) oscillated
    per ``articulation.fingers``/``joints`` at normalized time ``t``
    (0.0-1.0 across the whole sign), clamped to anatomical limits.
    Fingers/joints NOT named in ``articulation`` are returned exactly as
    given in ``base_pose`` (D2's "no regression for non-participating
    fingers" -- this task's brief only names D2 for whole non-Group-12
    signs, but the same "leave everything else untouched" principle
    applies within one Group 12 sign too)."""
    return HandJointPose(
        thumb=_articulate_thumb(base_pose.thumb, articulation, t),
        index=_articulate_finger(base_pose.index, "index", articulation, t),
        middle=_articulate_finger(base_pose.middle, "middle", articulation, t),
        ring=_articulate_finger(base_pose.ring, "ring", articulation, t),
        pinky=_articulate_finger(base_pose.pinky, "pinky", articulation, t),
    )
