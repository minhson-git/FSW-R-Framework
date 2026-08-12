"""C1-C6 (this task's brief, "Khung hình demo dễ đọc hơn", Part C).

Purely visual/readability fixes -- crop the closed shoulder-hip-hip
trapezoid ``PoseVisualizer`` draws (by no longer exporting the hip points),
and give the head actual shape (add the 6 eye points). No hand/body scale
parameter changes, no FK changes -- see ``test_pose_export.py``/
``test_body_and_arm.py`` for the pre-existing coverage this task must not
regress, and PROGRESS.md's export-layer entry for why
``reports/fk_accuracy.md`` is asserted unchanged elsewhere (this task
never touches anything MPJPE depends on).
"""

from __future__ import annotations

import numpy as np
import pytest
from pose_format.utils.holistic import holistic_components
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.export.pose_export import BODY_UNITS_TO_PIXELS, FRAME_HEIGHT, _component_offsets, frames_to_pose
from fsw_r.timeline.types import PoseFrame, TrackName, TrackPose

_POSE_POINT_NAMES = [c.points for c in holistic_components() if c.name == "POSE_LANDMARKS"][0]

_FLAT_ANGLE = JointAngle(flexion=0.0, abduction=0.0)
_FLAT_FINGER = FingerPose(mcp=_FLAT_ANGLE, pip=_FLAT_ANGLE, dip=_FLAT_ANGLE)
_FLAT_POSE = HandJointPose(
    thumb=ThumbPose(cmc=_FLAT_ANGLE, mcp=_FLAT_ANGLE, ip=_FLAT_ANGLE),
    index=_FLAT_FINGER,
    middle=_FLAT_FINGER,
    ring=_FLAT_FINGER,
    pinky=_FLAT_FINGER,
)

_EYE_NAMES = ("LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER", "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER")


def _right_hand_frame(position: np.ndarray[tuple[int, ...], np.dtype[np.float64]]) -> PoseFrame:
    track_pose = TrackPose(joint_pose=_FLAT_POSE, wrist=Rotation.identity(), position=position)
    return PoseFrame(time_seconds=0.0, tracks={TrackName.RIGHT_HAND: track_pose})


def test_c1_hips_stay_zero_confidence_every_frame() -> None:
    frames = tuple(_right_hand_frame(np.array([0.1 * i, 0.0, 0.0])) for i in range(5))
    pose = frames_to_pose(frames)
    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]
    for name in ("LEFT_HIP", "RIGHT_HIP"):
        index = start + _POSE_POINT_NAMES.index(name)
        assert np.all(pose.body.confidence[:, 0, index] == 0.0)


def test_c2_eyes_have_confidence_1_and_are_symmetric_about_the_midline() -> None:
    pose = frames_to_pose((_right_hand_frame(np.array([0.0, 0.0, 0.0])),))
    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]

    for name in _EYE_NAMES:
        index = start + _POSE_POINT_NAMES.index(name)
        assert pose.body.confidence[0, 0, index] == 1.0

    for left_name, right_name in (
        ("LEFT_EYE_INNER", "RIGHT_EYE_INNER"),
        ("LEFT_EYE", "RIGHT_EYE"),
        ("LEFT_EYE_OUTER", "RIGHT_EYE_OUTER"),
    ):
        left_x = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index(left_name), 0]
        right_x = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index(right_name), 0]
        # Pixel space: midline is FRAME_WIDTH/2; left/right offsets from it
        # must be equal and opposite (symmetric), small tolerance for
        # float rounding through the mm -> body-units -> pixel chain.
        midline = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("NOSE"), 0]
        assert (left_x - midline) == pytest.approx(-(right_x - midline), abs=1e-2)


def test_c3_eyes_are_above_nose_and_below_top_of_head() -> None:
    # Checked in BODY-SPACE (before pixel conversion, where +y is up), not
    # pixel space -- the y-flip in _body_to_pixel makes "above" mean
    # SMALLER pixel-y, and this test wants to avoid that sign entirely
    # (see this task's brief, C3's own warning: "tránh nhầm dấu").
    from fsw_r.export.body_geometry import NECK_TO_HEAD_CENTER_MM, SHOULDER_CENTER_BODY_SPACE, static_eye_landmarks, static_head_landmarks
    from fsw_r.export.anthropometry import HAND_MM_TO_BODY_UNITS

    nose_y = static_head_landmarks()["NOSE"][1]
    top_of_head_y = SHOULDER_CENTER_BODY_SPACE[1] + 2 * NECK_TO_HEAD_CENTER_MM * HAND_MM_TO_BODY_UNITS
    for name, point in static_eye_landmarks().items():
        assert point[1] > nose_y, f"{name} is not above the nose"
        assert point[1] < top_of_head_y, f"{name} is not below the top of the head"


def test_c4_nose_is_above_shoulder_and_hip_is_absent() -> None:
    # This task's own C4 (distinct from test_body_and_arm.py's
    # test_c4_nose_is_above_shoulder_in_image_space, which already covers
    # the y-flip regression risk with the SAME two points) -- included here
    # too so this task's own C1-C6 numbering is self-contained in one file.
    pose = frames_to_pose((_right_hand_frame(np.array([0.0, 0.0, 0.0])),))
    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]
    nose_y = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("NOSE"), 1]
    shoulder_y = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("RIGHT_SHOULDER"), 1]
    assert nose_y < shoulder_y  # smaller image-y = higher on screen
    assert pose.body.confidence[0, 0, start + _POSE_POINT_NAMES.index("RIGHT_HIP")] == 0.0


def test_c5_figure_occupies_70_to_90_percent_of_frame_height() -> None:
    from fsw_r.core.fswr_converter import fsw_to_fswr
    from fsw_r.timeline.build import build_timeline
    from fsw_r.timeline.sample import sample

    fsw = "M508x515S10000493x485S22a04500x500"
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)

    all_active_y = []
    for frame_index in range(len(frames)):
        conf = pose.body.confidence[frame_index, 0]
        ys = pose.body.data[frame_index, 0, :, 1][conf > 0]
        all_active_y.extend(ys.tolist())

    height_px = max(all_active_y) - min(all_active_y)
    fraction = height_px / FRAME_HEIGHT
    assert 0.70 <= fraction <= 0.90, f"figure occupies {fraction:.2%} of frame height, expected 70-90%"
    assert BODY_UNITS_TO_PIXELS > 0  # named constant, sanity

# C6 (this task's brief: "1.407 test cũ pass nguyên") is the whole existing
# suite, not a new test here -- in particular tests/test_hand_body_scale.py
# (the prior task's unified hand<->body ratio coverage), which this task
# never touches the inputs of (no bone_lengths.py/body_geometry.py 3D
# parameter changes, only pose_export.py's pixel-space output selection).
