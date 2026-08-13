"""Forward kinematics: a hand's 15 joint angles (``HandJointPose``) + wrist
orientation/position -> the 21 MediaPipe Holistic hand landmarks that
``pose_export.py`` needs.

**Landmark names come from the library, not typed by hand:**
``pose_format.utils.holistic.HAND_POINTS`` (itself
``mediapipe.solutions.holistic.HandLandmark._member_names_``) is imported
and used to both validate this module's own output (every call asserts the
21 keys match exactly) and to assemble the returned dict order-independently
-- each name is parsed for its finger/joint identity (e.g.
``"INDEX_FINGER_PIP"`` -> finger ``"index"``, joint index 1) rather than
assuming a fixed position in the list, so a future pose-format version
reordering ``HAND_POINTS`` would still produce a correctly-labelled dict
(only a version bump of the exact pin in pyproject.toml could silently
change semantics, and that pin is exact for this reason -- see
pyproject.toml's comment). This is the single highest-risk spot named in
this module's task brief ("sai thứ tự một điểm là hỏng cả bàn tay") -- see
``tests/test_forward_kinematics.py``'s E1.

**Coordinate convention** (matches ``fsw-r-viz/hand_geometry.py``'s
already-established one, reused for consistency rather than inventing a
third): in the hand's own local frame, before the wrist orientation is
applied, +y is the wrist -> fingertip direction when the hand is flat, +x
is the pinky(-) -> thumb(+) spread axis, +z is the palm normal. World
(body-space) output = ``wrist_position + wrist_orientation.apply(local_point)``.

**Forward kinematics accumulates rotation, it does not apply each joint's
angle independently in the world frame** -- each joint's ``Rotation`` is
composed onto its parent's, exactly the way ``hand_geometry.py``'s
``_finger_chain``/``_thumb_chain`` already do (see their comments); this
module reimplements that same proven structure (not a shared import --
``fsw-r-viz`` depends on ``fsw-r``, not the reverse) driven by
``bone_lengths.py``'s cited constants instead of that module's un-cited
debug numbers.

**Left-hand mirroring**: this module always builds RIGHT-hand chirality
first (thumb on local +x, same as ``hand_geometry.hand_local_points``), then
flips the local x axis for ``HandSide.LEFT`` before the wrist orientation is
applied -- the same fix (and the same reasoning for why it's a flip of the
computed points, not a re-derivation of mirrored Euler angles) already
locked in by ``fsw-r-viz``'s ``test_right_hand_thumb_is_on_the_viewers_left``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from pose_format.utils.holistic import HAND_POINTS
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, HandSide, ThumbPose
from fsw_r.export.bone_lengths import (
    FINGER_METACARPAL_LENGTH_MM,
    FINGER_PHALANX_LENGTHS_MM,
    HAND_MM_TO_BODY_UNITS,
    HAND_SCALE,
    KNUCKLE_LATERAL_SPACING_MM,
    THUMB_METACARPAL_LENGTH_MM,
    THUMB_PHALANX_LENGTHS_MM,
)

_Vec3 = NDArray[np.float64]

_EXTENSION_AXIS: _Vec3 = np.array([0.0, 1.0, 0.0])

# Lateral (x) knuckle position per finger, in KNUCKLE_LATERAL_SPACING_MM
# units -- same relative ordering as fsw-r-viz/hand_geometry.py's
# _FINGER_BASES (index closest to thumb at +x, pinky farthest at -x), scaled
# by the cited spacing constant instead of that module's un-cited numbers.
_FINGER_LATERAL_SLOTS: dict[str, float] = {
    "index": 1.5,
    "middle": 0.5,
    "ring": -0.5,
    "pinky": -1.5,
}

# The thumb doesn't extend along +y like the other fingers -- it comes off
# the palm at roughly a right angle, tilted out of the palm plane. These two
# constants (attachment OFFSET + base ROTATION) have origin **FITTED**: they
# were optimized against the 3d-hands-benchmark ground truth on a held-out,
# ISWA-group-stratified 70/30 split (scripts/calibrate_hand_geometry.py,
# seed 42) -- NOT an anthropometric citation, and no longer the earlier
# "visually verified" authored guess (was offset [26, 15, 0], rotation
# zy [-65, -20]). FITTED is a distinct origin from the AUTHORED / measured /
# derived / cited values elsewhere in this layer: the numbers are simply
# whatever minimizes normalized MPJPE on the fit set. The thumb was this
# project's single largest FK error source (per-finger MPJPE ~80 vs 39-48);
# this fit cut held-out (test-set) MPJPE 6.4% (48.14 -> 45.07). The z Euler
# angle was the dominant error (-65 -> -29.70). See reports/fk_calibration.md,
# reports/calibration_split.json, and PROGRESS.md's calibration entry.
#
# The offset is still multiplied by HAND_SCALE (the fit was on the raw ratio),
# so it stays coupled to the single stature every other hand/body dimension
# derives from -- otherwise the thumb attachment would not scale with the rest
# of the hand (see bone_lengths.HAND_SCALE's comment).
_THUMB_BASE_OFFSET_MM: _Vec3 = np.array([27.2162, 15.6248, 0.0009]) * HAND_SCALE  # FITTED, see above
_THUMB_BASE_ROTATION = Rotation.from_euler("zy", [-29.7002, -24.5550], degrees=True)  # FITTED, see above

_FINGER_JOINT_NAMES = ("MCP", "PIP", "DIP", "TIP")
_THUMB_JOINT_NAMES = ("CMC", "MCP", "IP", "TIP")

# HAND_POINTS name prefix -> this module's internal finger key. Read off
# HAND_POINTS itself (see module docstring), not an independently-guessed
# spelling.
_PREFIX_TO_FINGER: dict[str, str] = {
    "THUMB": "thumb",
    "INDEX_FINGER": "index",
    "MIDDLE_FINGER": "middle",
    "RING_FINGER": "ring",
    "PINKY": "pinky",
}


def _finger_chain_local(pose: FingerPose, finger: str) -> list[_Vec3]:
    """MCP, PIP, DIP, TIP for one of the 4 non-thumb fingers, in the local
    (pre-wrist-rotation) RIGHT-hand frame."""
    palm_offset = np.array(
        [
            _FINGER_LATERAL_SLOTS[finger] * KNUCKLE_LATERAL_SPACING_MM,
            FINGER_METACARPAL_LENGTH_MM[finger],
            0.0,
        ]
    ) * HAND_MM_TO_BODY_UNITS
    lengths_mm = FINGER_PHALANX_LENGTHS_MM[finger]

    points = [palm_offset]
    orientation = Rotation.from_euler("xz", [pose.mcp.flexion, pose.mcp.abduction], degrees=True)
    points.append(points[-1] + orientation.apply(_EXTENSION_AXIS) * lengths_mm[0] * HAND_MM_TO_BODY_UNITS)

    orientation = orientation * Rotation.from_euler("x", pose.pip.flexion, degrees=True)
    points.append(points[-1] + orientation.apply(_EXTENSION_AXIS) * lengths_mm[1] * HAND_MM_TO_BODY_UNITS)

    orientation = orientation * Rotation.from_euler("x", pose.dip.flexion, degrees=True)
    points.append(points[-1] + orientation.apply(_EXTENSION_AXIS) * lengths_mm[2] * HAND_MM_TO_BODY_UNITS)

    return points  # [MCP, PIP, DIP, TIP]


def _thumb_chain_local(pose: ThumbPose) -> list[_Vec3]:
    """CMC, MCP, IP, TIP, in the local (pre-wrist-rotation) RIGHT-hand
    frame."""
    cmc = _THUMB_BASE_OFFSET_MM * HAND_MM_TO_BODY_UNITS
    points = [cmc]

    orientation = _THUMB_BASE_ROTATION * Rotation.from_euler("xz", [pose.cmc.flexion, pose.cmc.abduction], degrees=True)
    points.append(
        points[-1] + orientation.apply(_EXTENSION_AXIS) * THUMB_METACARPAL_LENGTH_MM * HAND_MM_TO_BODY_UNITS
    )

    orientation = orientation * Rotation.from_euler("x", pose.mcp.flexion, degrees=True)
    points.append(
        points[-1] + orientation.apply(_EXTENSION_AXIS) * THUMB_PHALANX_LENGTHS_MM[0] * HAND_MM_TO_BODY_UNITS
    )

    orientation = orientation * Rotation.from_euler("x", pose.ip.flexion, degrees=True)
    points.append(
        points[-1] + orientation.apply(_EXTENSION_AXIS) * THUMB_PHALANX_LENGTHS_MM[1] * HAND_MM_TO_BODY_UNITS
    )

    return points  # [CMC, MCP, IP, TIP]


def _flip_x(point: _Vec3) -> _Vec3:
    return np.array([-point[0], point[1], point[2]])


def _finger_and_joint(name: str) -> tuple[str, int]:
    """Parses a HAND_POINTS name (e.g. "INDEX_FINGER_PIP") into this
    module's internal finger key and joint index (0=first joint after
    wrist, 3=TIP) -- see module docstring for why this is name-parsing, not
    a positional assumption."""
    for prefix, finger in _PREFIX_TO_FINGER.items():
        if name.startswith(prefix + "_"):
            suffix = name[len(prefix) + 1 :]
            joint_names = _THUMB_JOINT_NAMES if finger == "thumb" else _FINGER_JOINT_NAMES
            return finger, joint_names.index(suffix)
    raise ValueError(f"unrecognized HAND_POINTS name: {name!r}")


def hand_to_landmarks(
    pose: HandJointPose,
    wrist_orientation: Rotation,
    wrist_position: _Vec3,
    hand_side: HandSide,
) -> dict[str, _Vec3]:
    """The 21 MediaPipe Holistic hand landmarks, in body-space world
    coordinates, keyed by the exact names in
    ``pose_format.utils.holistic.HAND_POINTS``."""
    chains: dict[str, list[_Vec3]] = {
        "thumb": _thumb_chain_local(pose.thumb),
        "index": _finger_chain_local(pose.index, "index"),
        "middle": _finger_chain_local(pose.middle, "middle"),
        "ring": _finger_chain_local(pose.ring, "ring"),
        "pinky": _finger_chain_local(pose.pinky, "pinky"),
    }
    if hand_side == HandSide.LEFT:
        chains = {finger: [_flip_x(p) for p in points] for finger, points in chains.items()}

    world_chains = {
        finger: [wrist_position + wrist_orientation.apply(p) for p in points] for finger, points in chains.items()
    }

    landmarks: dict[str, _Vec3] = {}
    for name in HAND_POINTS:
        if name == "WRIST":
            landmarks[name] = wrist_position
        else:
            finger, joint_index = _finger_and_joint(name)
            landmarks[name] = world_chains[finger][joint_index]

    assert set(landmarks) == set(HAND_POINTS), "internal error: landmark set does not match HAND_POINTS"
    return landmarks
