"""Data types for ``SignTimeline`` -- the time axis FSW itself doesn't
represent. Same style as ``core/``: ``frozen=True`` dataclasses, full type
hints, ``mypy --strict`` clean.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.types import HandJointPose


class TrackName(Enum):
    RIGHT_HAND = "right_hand"
    LEFT_HAND = "left_hand"
    # One FACE track, not one per facial feature: a face is deformed by the
    # ARKit-52 blend-shape set as a whole, and several Category 4 symbols in
    # a sign (brows + mouth + eyes) describe ONE face at ONE instant, so they
    # merge into a single expression rather than animating independently.
    FACE = "face"
    # HEAD, BODY: not used yet -- HeadSymbol (rigid orientation) and Category
    # 5 are the next two unlocks, and both are deliberately still rejected by
    # build.py rather than silently dropped.


class SymbolRole(Enum):
    """What a symbol's category means for the timeline -- see
    ``classify.py``'s ``role_of()``."""

    POSTURE = "posture"  # Category 1, 4 -- a state at one instant (a NODE)
    TRANSITION = "transition"  # Category 2 -- connects two states (an EDGE)
    TIMING = "timing"  # Category 3 -- adjusts rhythm (not used yet)
    ANCHOR = "anchor"  # Category 5, 6 -- reference frame (not used yet)
    BOUNDARY = "boundary"  # Category 7 -- sentence break, dropped when rendering one sign


@dataclass(frozen=True)
class Keyframe:
    time: float  # 0.0-1.0, normalized to the sign's own duration
    joint_pose: HandJointPose | None
    wrist: Rotation | None
    position: NDArray[np.float64] | None  # body-space 3D coordinate
    # ARKit-52 expression, for the FACE track. Defaulted so every existing
    # hand-track construction is unchanged: a hand keyframe carries no
    # expression and a face keyframe carries no joint pose.
    expression: FaceExpressionPose | None = None


@dataclass(frozen=True)
class Track:
    name: TrackName
    keyframes: tuple[Keyframe, ...]  # sorted by ascending time


@dataclass(frozen=True)
class SignTimeline:
    tracks: tuple[Track, ...]
    duration_seconds: float


@dataclass(frozen=True)
class TrackPose:
    """One track's interpolated state at a single sampled instant --
    ``sample.py``'s ``sample()`` output, per track, per frame."""

    joint_pose: HandJointPose | None
    wrist: Rotation | None
    position: NDArray[np.float64] | None
    expression: FaceExpressionPose | None = None


@dataclass(frozen=True)
class PoseFrame:
    """One sampled instant across every track -- ready for a renderer to
    consume, at a specific point in wall-clock time."""

    time_seconds: float
    tracks: dict[TrackName, TrackPose]
