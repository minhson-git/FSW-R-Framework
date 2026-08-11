"""Packages a full ``timeline.sample()`` output (``tuple[PoseFrame, ...]``)
into a real ``pose_format.Pose`` (the ``.pose`` file format) -- see this
package's docstring and PROGRESS.md's export-layer entry for why this
project uses that library's format instead of inventing its own.

**Header**: built from ``pose_format.utils.holistic.holistic_components()``,
the library's own standard MediaPipe Holistic component list -- kept
COMPLETE (``POSE_LANDMARKS``, ``FACE_LANDMARKS``, both hands,
``POSE_WORLD_LANDMARKS``), not trimmed down to just the components this
task fills in. ``FACE_LANDMARKS``/``POSE_WORLD_LANDMARKS`` still get
confidence 0 for every point (no face model, and world landmarks are a
separate MediaPipe coordinate space this project has no data for) -- that
is how ``pose-format``/``PoseVisualizer`` represent "this point is
missing," not silently dropped from the header, which would make the
file's topology non-standard and less interoperable with other
pose-format tooling, defeating the whole reason this project chose this
format (see PROGRESS.md's "vì sao chọn pose-format"). Confirmed, not just
assumed: ``NumPyPoseBody`` itself wraps ``data`` in a
``numpy.ma.MaskedArray`` masked wherever ``confidence == 0`` -- the library
recognizes "confidence 0" as "missing" at the data-structure level, not
just by convention (see ``tests/test_pose_export.py``'s E7).

**``POSE_LANDMARKS`` (the body)**: as of this task, filled for everything
EXCEPT the legs (indices 25-32, outside the signing space this project
models -- confidence 0) and the eyes (indices 1-6, not listed in this
task's own brief and left unset). A static neutral torso/head
(``export/body_geometry.py``) anchors two-bone IK (``export/arm_ik.py``)
that solves for each active hand track's elbow from its (fixed) shoulder
and its (per-frame) wrist position. The 6 duplicated hand-adjacent points
POSE_LANDMARKS itself defines (``LEFT/RIGHT_PINKY/INDEX/THUMB``, indices
17-22) are filled from that SAME frame's already-computed hand landmarks
(``PINKY_MCP``/``INDEX_FINGER_MCP``/``THUMB_TIP`` respectively -- MediaPipe's
own convention, confirmed by ``BODY_LIMBS``' wrist-to-these-points
connections) rather than recomputed independently, which is also what
guarantees ``POSE_LANDMARKS.WRIST`` and ``*_HAND_LANDMARKS.WRIST`` land at
the exact same pixel every frame (see ``tests/test_pose_export.py``'s C6).

**Coordinate system, the highest-risk spot in this module** (per this
package's task brief): ``pose_format`` uses IMAGE coordinates (x right, y
DOWN), matching how MediaPipe/most CV tooling represents 2D video frames.
``fsw_r.timeline``'s body space uses MATH coordinates (y UP -- see
``timeline/anchor.py``'s own extensive comment on why, keyed to real
head-vs-hand corpus y medians). So exporting flips y a SECOND time here,
independently of anchor.py's own flip -- get this wrong and the output
video plays upside down while every other test in the suite stays green
(nothing else touches image-space y). See ``tests/test_pose_export.py``'s
E2/C4, the tests this exact risk is written for.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from pose_format import Pose, PoseHeader
from pose_format.numpy import NumPyPoseBody
from pose_format.pose_header import PoseHeaderDimensions
from pose_format.utils.holistic import holistic_components

from fsw_r.core.types import HandSide
from fsw_r.export.arm_ik import POLE_DIRECTION_LEFT, POLE_DIRECTION_RIGHT, solve_two_bone_ik
from fsw_r.export.body_geometry import (
    FOREARM_LENGTH,
    UPPER_ARM_LENGTH,
    hip_position,
    shoulder_position,
    static_head_landmarks,
)
from fsw_r.export.forward_kinematics import hand_to_landmarks
from fsw_r.timeline.types import PoseFrame, TrackName

# Output frame size in pixels -- an arbitrary but named/documented choice,
# not a value pose-format or MediaPipe requires.
FRAME_WIDTH = 512
FRAME_HEIGHT = 512

# UNVERIFIED: how many pixels one fsw_r.timeline body-space unit occupies.
#
# CALIBRATED for a HAND-ONLY figure (Part A of this task): at the
# pre-Part-A value (150.0), a real MVP-1 static sign's hand bounding box
# measured 94x183 px in a 512x512 frame (~36% of frame height) -- too
# small for PoseVisualizer's line thickness (which scales with FRAME size
# only, not subject size -- round(sqrt(w*h)/150) -- see
# pose_format.pose_visualizer.PoseVisualizer._draw_frame) to read as
# anything but a toothpick-thin stick figure. 314.0 put that SAME hand's
# bounding box at ~75% of frame height.
#
# NOT recalibrated again for the full body added in Part B -- a full
# standing figure (shoulders + arms + torso) is taller/wider than a lone
# hand, so 314.0 no longer means "fills ~75% of frame" the same way. Kept
# as-is rather than re-tuned a second time in this task: still produces a
# complete, recognizable, correctly-proportioned figure (see
# demo/mvp1_sign_3_after_body.gif), and re-tuning frame occupancy again is
# a cosmetic follow-up, not a correctness issue -- noted in PROGRESS.md's
# "giả định chưa kiểm chứng" list rather than iterated on here.
BODY_UNITS_TO_PIXELS = 314.0

_HAND_COMPONENT_BY_TRACK: dict[TrackName, str] = {
    TrackName.RIGHT_HAND: "RIGHT_HAND_LANDMARKS",
    TrackName.LEFT_HAND: "LEFT_HAND_LANDMARKS",
}

# HandSide isn't stored on TrackName -- RIGHT_HAND/LEFT_HAND already say
# which hand, this just spells out the fsw_r.core.types.HandSide match
# forward_kinematics.hand_to_landmarks() needs.
_HAND_SIDE_BY_TRACK: dict[TrackName, HandSide] = {
    TrackName.RIGHT_HAND: HandSide.RIGHT,
    TrackName.LEFT_HAND: HandSide.LEFT,
}

# POSE_LANDMARKS point name -> which hand-component point it duplicates.
# MediaPipe's own convention (confirmed via BODY_LIMBS' wrist-to-these
# connections, see module docstring), not this project's invention.
_POSE_HAND_DUPLICATE_SOURCE = {
    "PINKY": "PINKY_MCP",
    "INDEX": "INDEX_FINGER_MCP",
    "THUMB": "THUMB_TIP",
}

# POSE_LANDMARKS indices 25-32 (see this task's brief, Part B1) -- outside
# the signing space this project models at all; always confidence 0.
_LEG_POINT_NAMES = (
    "LEFT_KNEE",
    "RIGHT_KNEE",
    "LEFT_ANKLE",
    "RIGHT_ANKLE",
    "LEFT_HEEL",
    "RIGHT_HEEL",
    "LEFT_FOOT_INDEX",
    "RIGHT_FOOT_INDEX",
)

_POLE_DIRECTION_BY_TRACK = {
    TrackName.RIGHT_HAND: POLE_DIRECTION_RIGHT,
    TrackName.LEFT_HAND: POLE_DIRECTION_LEFT,
}
_SIDE_PREFIX_BY_TRACK = {
    TrackName.RIGHT_HAND: "RIGHT",
    TrackName.LEFT_HAND: "LEFT",
}


def _body_to_pixel(point: NDArray[np.float64]) -> NDArray[np.float64]:
    """Body-space (math convention, y up) -> pose-format pixel space (image
    convention, y down). The y flip is the one thing this function must
    never get backwards -- see module docstring."""
    return np.array(
        [
            FRAME_WIDTH / 2 + point[0] * BODY_UNITS_TO_PIXELS,
            FRAME_HEIGHT / 2 - point[1] * BODY_UNITS_TO_PIXELS,  # the flip
            point[2] * BODY_UNITS_TO_PIXELS,
        ]
    )


def _build_header() -> PoseHeader:
    dimensions = PoseHeaderDimensions(width=FRAME_WIDTH, height=FRAME_HEIGHT)
    return PoseHeader(version=0.1, dimensions=dimensions, components=holistic_components())


def _component_offsets(header: PoseHeader) -> dict[str, tuple[int, int]]:
    """component name -> (start index, point count) within the flattened
    per-frame point array -- computed from the header actually built above,
    never assumed."""
    offsets: dict[str, tuple[int, int]] = {}
    cursor = 0
    for component in header.components:
        offsets[component.name] = (cursor, len(component.points))
        cursor += len(component.points)
    return offsets


def _pose_landmarks_for_frame(
    frame: PoseFrame, hand_landmarks_by_track: dict[TrackName, dict[str, NDArray[np.float64]]]
) -> dict[str, NDArray[np.float64]]:
    """The subset of POSE_LANDMARKS' 33 points this project has data for
    at this frame -- see module docstring for what's covered. Points not
    returned here (legs, eyes) get confidence 0, same as a track-less hand."""
    points: dict[str, NDArray[np.float64]] = {}
    points.update(static_head_landmarks())

    for is_right, track_name in ((True, TrackName.RIGHT_HAND), (False, TrackName.LEFT_HAND)):
        side = _SIDE_PREFIX_BY_TRACK[track_name]
        shoulder = shoulder_position(is_right)
        points[f"{side}_SHOULDER"] = shoulder
        points[f"{side}_HIP"] = hip_position(is_right)

        hand_landmarks = hand_landmarks_by_track.get(track_name)
        if hand_landmarks is None:
            continue  # no wrist for this frame/track -- elbow/wrist/duplicates stay unset (confidence 0)

        wrist = hand_landmarks["WRIST"]
        points[f"{side}_WRIST"] = wrist
        points[f"{side}_ELBOW"] = solve_two_bone_ik(
            shoulder, wrist, _POLE_DIRECTION_BY_TRACK[track_name], UPPER_ARM_LENGTH, FOREARM_LENGTH
        )
        for pose_suffix, hand_name in _POSE_HAND_DUPLICATE_SOURCE.items():
            points[f"{side}_{pose_suffix}"] = hand_landmarks[hand_name]

    return points


def frames_to_pose(frames: tuple[PoseFrame, ...], fps: int = 25) -> Pose:
    """Builds a ``Pose`` covering every frame in ``frames``. A track absent
    from a given ``PoseFrame.tracks`` (see ``timeline/sample.py`` -- MVP-1
    signs only ever populate one track) gets confidence 0 for that hand's
    21 points AND its arm/duplicated POSE_LANDMARKS points in that frame,
    not fabricated coordinates. The static torso/head points (shoulders,
    hips, face) are filled every frame regardless of which tracks are
    active."""
    header = _build_header()
    offsets = _component_offsets(header)
    total_points = sum(len(c.points) for c in header.components)
    pose_start, _pose_count = offsets["POSE_LANDMARKS"]
    pose_point_names = _ordered_point_names(header, "POSE_LANDMARKS")

    frame_count = len(frames)
    data = np.zeros((frame_count, 1, total_points, 3), dtype=np.float32)
    confidence = np.zeros((frame_count, 1, total_points), dtype=np.float32)

    for frame_index, frame in enumerate(frames):
        hand_landmarks_by_track: dict[TrackName, dict[str, NDArray[np.float64]]] = {}
        for track_name, component_name in _HAND_COMPONENT_BY_TRACK.items():
            track_pose = frame.tracks.get(track_name)
            if track_pose is None or track_pose.joint_pose is None or track_pose.wrist is None or track_pose.position is None:
                continue  # confidence stays 0 -- "missing," not guessed

            landmarks = hand_to_landmarks(
                pose=track_pose.joint_pose,
                wrist_orientation=track_pose.wrist,
                wrist_position=track_pose.position,
                hand_side=_HAND_SIDE_BY_TRACK[track_name],
            )
            hand_landmarks_by_track[track_name] = landmarks
            start, count = offsets[component_name]
            for point_index, name in enumerate(_ordered_point_names(header, component_name)):
                pixel = _body_to_pixel(landmarks[name])
                data[frame_index, 0, start + point_index] = pixel
                confidence[frame_index, 0, start + point_index] = 1.0

        pose_points = _pose_landmarks_for_frame(frame, hand_landmarks_by_track)
        for point_index, name in enumerate(pose_point_names):
            body_space = pose_points.get(name)
            if body_space is None:
                continue  # legs/eyes/inactive-side arm -- confidence stays 0
            pixel = _body_to_pixel(body_space)
            data[frame_index, 0, pose_start + point_index] = pixel
            confidence[frame_index, 0, pose_start + point_index] = 1.0

    body = NumPyPoseBody(fps=fps, data=data, confidence=confidence)
    return Pose(header=header, body=body)


def _ordered_point_names(header: PoseHeader, component_name: str) -> list[str]:
    for component in header.components:
        if component.name == component_name:
            names: list[str] = component.points
            return names
    raise ValueError(f"no such component: {component_name!r}")  # pragma: no cover -- holistic_components() is fixed


def save_pose(pose: Pose, path: Path) -> None:
    with open(path, "wb") as f:
        pose.write(f)
