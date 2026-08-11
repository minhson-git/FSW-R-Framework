"""Packages a full ``timeline.sample()`` output (``tuple[PoseFrame, ...]``)
into a real ``pose_format.Pose`` (the ``.pose`` file format) -- see this
package's docstring and PROGRESS.md's export-layer entry for why this
project uses that library's format instead of inventing its own.

**Header**: built from ``pose_format.utils.holistic.holistic_components()``,
the library's own standard MediaPipe Holistic component list -- kept
COMPLETE (``POSE_LANDMARKS``, ``FACE_LANDMARKS``, both hands,
``POSE_WORLD_LANDMARKS``), not trimmed down to just the two hand
components this task actually fills in. Components this task has no data
for (body pose, face, world landmarks -- arm IK and a static torso are
explicitly step 3, out of this task's scope) get confidence 0 for every
point in every frame, which is how ``pose-format``/`PoseVisualizer``
represent "this point is missing," not silently dropped from the header --
dropping a component would make the file's topology non-standard and less
interoperable with other pose-format tooling, defeating the whole reason
this task chose this format (see PROGRESS.md's "vì sao chọn pose-format").
Confirmed, not just assumed: ``NumPyPoseBody`` itself wraps ``data`` in a
``numpy.ma.MaskedArray`` masked wherever ``confidence == 0`` -- the library
recognizes "confidence 0" as "missing" at the data-structure level, not
just by convention (see ``tests/test_pose_export.py``'s E7).

**Coordinate system, the highest-risk spot in this module** (per this
package's task brief): ``pose_format`` uses IMAGE coordinates (x right, y
DOWN), matching how MediaPipe/most CV tooling represents 2D video frames.
``fsw_r.timeline``'s body space uses MATH coordinates (y UP -- see
``timeline/anchor.py``'s own extensive comment on why, keyed to real
head-vs-hand corpus y medians). So exporting flips y a SECOND time here,
independently of anchor.py's own flip -- get this wrong and the output
video plays upside down while every other test in the suite stays green
(nothing else touches image-space y). See ``tests/test_pose_export.py``'s
E2, the test this exact risk is written for.
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
from fsw_r.export.forward_kinematics import hand_to_landmarks
from fsw_r.timeline.types import PoseFrame, TrackName

# Output frame size in pixels -- an arbitrary but named/documented choice,
# not a value pose-format or MediaPipe requires.
FRAME_WIDTH = 512
FRAME_HEIGHT = 512

# UNVERIFIED: how many pixels one fsw_r.timeline body-space unit occupies.
#
# CALIBRATED, not guessed: at the previous value (150.0), a real MVP-1
# static sign's hand bounding box measured 94x183 px in a 512x512 frame
# (~36% of frame height) -- too small for PoseVisualizer's line thickness
# (which scales with FRAME size only, not subject size --
# round(sqrt(w*h)/150) -- see pose_format.pose_visualizer.PoseVisualizer.
# _draw_frame) to read as anything but a toothpick-thin stick figure. This
# value is set so that SAME hand's bounding box height lands at ~75% of
# FRAME_HEIGHT instead: 150 * (0.75 * 512) / 183.22 =~ 314.4, rounded.
# Still just a hand-sized calibration, not a real body -- Part B (adding a
# torso/arms around the hand) changes what "fills the frame" means and
# will need this recalibrated again; see PROGRESS.md's export-layer
# entry and "giả định chưa kiểm chứng" list for both calibrations.
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


def frames_to_pose(frames: tuple[PoseFrame, ...], fps: int = 25) -> Pose:
    """Builds a ``Pose`` covering every frame in ``frames``. A track absent
    from a given ``PoseFrame.tracks`` (see ``timeline/sample.py`` -- MVP-1
    signs only ever populate one track) gets confidence 0 for that hand's
    21 points in that frame, not fabricated coordinates."""
    header = _build_header()
    offsets = _component_offsets(header)
    total_points = sum(len(c.points) for c in header.components)

    frame_count = len(frames)
    data = np.zeros((frame_count, 1, total_points, 3), dtype=np.float32)
    confidence = np.zeros((frame_count, 1, total_points), dtype=np.float32)

    for frame_index, frame in enumerate(frames):
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
            start, count = offsets[component_name]
            for point_index, name in enumerate(_ordered_point_names(header, component_name)):
                pixel = _body_to_pixel(landmarks[name])
                data[frame_index, 0, start + point_index] = pixel
                confidence[frame_index, 0, start + point_index] = 1.0

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
