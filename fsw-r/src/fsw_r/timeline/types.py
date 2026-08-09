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

from fsw_r.core.types import HandJointPose


class TrackName(Enum):
    RIGHT_HAND = "right_hand"
    LEFT_HAND = "left_hand"
    # HEAD, BODY: not used at MVP-1 -- add once Category 4/5 support lands.


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


@dataclass(frozen=True)
class PoseFrame:
    """One sampled instant across every track -- ready for a renderer to
    consume, at a specific point in wall-clock time."""

    time_seconds: float
    tracks: dict[TrackName, TrackPose]
