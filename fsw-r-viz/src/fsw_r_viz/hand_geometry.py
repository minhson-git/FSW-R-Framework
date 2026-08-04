"""Approximate stick-figure hand geometry, for sanity-checking a HandJointPose
visually. Not anatomically precise -- just enough to see, at a glance,
whether a pose looks like what it's supposed to look like (e.g. "index
straight, other three curled into the fist").

All lengths are in arbitrary units (roughly centimeters for an adult hand).
Coordinates are in the wrist-local frame, before the symbol's wrist
orientation is applied:
  x: across the knuckle row, pinky (-) to thumb (+) side
  y: wrist -> fingertip direction when the hand is flat
  z: palm normal (points out of the palm, toward the viewer, at rotation=0)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, ThumbPose

_Vec3 = NDArray[np.float64]

# (mcp->pip, pip->dip, dip->tip) bone lengths per finger.
_FINGER_LENGTHS: dict[str, tuple[float, float, float]] = {
    "index": (4.6, 2.6, 1.8),
    "middle": (5.0, 3.0, 2.0),
    "ring": (4.7, 2.8, 1.8),
    "pinky": (3.7, 2.0, 1.7),
}

# MCP base position (x, y, z) per finger, along the knuckle row.
_FINGER_BASES: dict[str, _Vec3] = {
    "index": np.array([1.5, 9.0, 0.0]),
    "middle": np.array([0.5, 9.3, 0.0]),
    "ring": np.array([-0.5, 9.0, 0.0]),
    "pinky": np.array([-1.5, 8.4, 0.0]),
}

# (cmc->mcp, mcp->ip, ip->tip) bone lengths for the thumb.
_THUMB_LENGTHS: tuple[float, float, float] = (4.0, 3.0, 2.5)
_THUMB_BASE: _Vec3 = np.array([2.6, 1.5, 0.0])
# The thumb doesn't point along +y like the other fingers -- it comes off the
# palm at roughly a right angle, tilted out of the palm plane.
_THUMB_BASE_ROTATION = Rotation.from_euler("zy", [-65, -20], degrees=True)

_EXTENSION_AXIS: _Vec3 = np.array([0.0, 1.0, 0.0])


def _finger_chain(
    base: _Vec3,
    base_rotation: Rotation,
    pose: FingerPose,
    lengths: tuple[float, float, float],
) -> list[_Vec3]:
    points = [base]
    orientation = base_rotation * Rotation.from_euler(
        "xz", [pose.mcp.flexion, pose.mcp.abduction], degrees=True
    )
    current = points[-1] + orientation.apply(_EXTENSION_AXIS) * lengths[0]
    points.append(current)

    orientation = orientation * Rotation.from_euler("x", pose.pip.flexion, degrees=True)
    current = points[-1] + orientation.apply(_EXTENSION_AXIS) * lengths[1]
    points.append(current)

    orientation = orientation * Rotation.from_euler("x", pose.dip.flexion, degrees=True)
    current = points[-1] + orientation.apply(_EXTENSION_AXIS) * lengths[2]
    points.append(current)

    return points


def _thumb_chain(pose: ThumbPose) -> list[_Vec3]:
    points = [_THUMB_BASE]
    orientation = _THUMB_BASE_ROTATION * Rotation.from_euler(
        "xz", [pose.cmc.flexion, pose.cmc.abduction], degrees=True
    )
    current = points[-1] + orientation.apply(_EXTENSION_AXIS) * _THUMB_LENGTHS[0]
    points.append(current)

    orientation = orientation * Rotation.from_euler("x", pose.mcp.flexion, degrees=True)
    current = points[-1] + orientation.apply(_EXTENSION_AXIS) * _THUMB_LENGTHS[1]
    points.append(current)

    orientation = orientation * Rotation.from_euler("x", pose.ip.flexion, degrees=True)
    current = points[-1] + orientation.apply(_EXTENSION_AXIS) * _THUMB_LENGTHS[2]
    points.append(current)

    return points


def _flip_x(chains: dict[str, list[_Vec3]]) -> dict[str, list[_Vec3]]:
    return {
        finger: [np.array([-point[0], point[1], point[2]]) for point in points]
        for finger, points in chains.items()
    }


def hand_local_points(pose: HandJointPose) -> dict[str, list[_Vec3]]:
    """Wrist, MCP, PIP/IP, DIP, tip positions for each finger, in the
    wrist-local frame (before wrist orientation is applied)."""
    wrist = np.zeros(3)
    chains = {
        "thumb": [wrist, *_thumb_chain(pose.thumb)],
        "index": [wrist, *_finger_chain(_FINGER_BASES["index"], Rotation.identity(), pose.index, _FINGER_LENGTHS["index"])],
        "middle": [wrist, *_finger_chain(_FINGER_BASES["middle"], Rotation.identity(), pose.middle, _FINGER_LENGTHS["middle"])],
        "ring": [wrist, *_finger_chain(_FINGER_BASES["ring"], Rotation.identity(), pose.ring, _FINGER_LENGTHS["ring"])],
        "pinky": [wrist, *_finger_chain(_FINGER_BASES["pinky"], Rotation.identity(), pose.pinky, _FINGER_LENGTHS["pinky"])],
    }
    # The base positions/rotations above put the thumb on local +x -- which,
    # rendered unmirrored (RIGHT hand, palm facing the viewer, fingers up),
    # puts the thumb on the viewer's RIGHT. That's backwards: a real right
    # hand held up palm-out, fingers up (e.g. an oath-taking photo) shows
    # the thumb on the viewer's LEFT. Flipping once here fixes this
    # function's own output to be true RIGHT-hand chirality; mirroring
    # rotations analytically (instead of flipping the already-computed
    # points) would be much more error-prone, so the fix is applied to the
    # final Cartesian points, exactly like mirror_for_left_hand below.
    return _flip_x(chains)


def apply_wrist_orientation(
    chains: dict[str, list[_Vec3]], wrist_orientation: Rotation
) -> dict[str, list[_Vec3]]:
    return {
        finger: [wrist_orientation.apply(point) for point in points]
        for finger, points in chains.items()
    }


def mirror_for_left_hand(chains: dict[str, list[_Vec3]]) -> dict[str, list[_Vec3]]:
    """A LEFT hand is a mirror image of a RIGHT hand, not a rotation of one.
    ``hand_local_points`` above already returns true RIGHT-hand chirality;
    flipping the x axis (the pinky<->thumb spread axis) again turns it into
    the correct LEFT-hand chirality before the wrist orientation is
    applied. This stands in for what fsw-r's real HandRigProvider would do
    by picking a genuinely separate LEFT-hand rig/mesh instead."""
    return _flip_x(chains)
