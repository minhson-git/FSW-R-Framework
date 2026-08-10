from __future__ import annotations

from pathlib import Path

import numpy as np
from pose_format.utils.holistic import HAND_POINTS
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.export.pose_export import (
    BODY_UNITS_TO_PIXELS,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    _component_offsets,
    frames_to_pose,
    save_pose,
)
from fsw_r.timeline.types import PoseFrame, TrackName, TrackPose

_FLAT_ANGLE = JointAngle(flexion=0.0, abduction=0.0)
_FLAT_FINGER = FingerPose(mcp=_FLAT_ANGLE, pip=_FLAT_ANGLE, dip=_FLAT_ANGLE)
_FLAT_POSE = HandJointPose(
    thumb=ThumbPose(cmc=_FLAT_ANGLE, mcp=_FLAT_ANGLE, ip=_FLAT_ANGLE),
    index=_FLAT_FINGER,
    middle=_FLAT_FINGER,
    ring=_FLAT_FINGER,
    pinky=_FLAT_FINGER,
)


def _right_hand_frame(y: float) -> PoseFrame:
    track_pose = TrackPose(joint_pose=_FLAT_POSE, wrist=Rotation.identity(), position=np.array([0.0, y, 0.0]))
    return PoseFrame(time_seconds=0.0, tracks={TrackName.RIGHT_HAND: track_pose})


def test_e2_higher_math_y_gives_smaller_image_y() -> None:
    # E2 -- QUAN TRỌNG NHẤT. A wrist at higher math-y (up) must land at a
    # SMALLER image-y (pose-format is y-down) after export.
    high = frames_to_pose((_right_hand_frame(y=1.0),))
    low = frames_to_pose((_right_hand_frame(y=-1.0),))

    offsets = _component_offsets(high.header)
    start, _count = offsets["RIGHT_HAND_LANDMARKS"]
    wrist_index = start + HAND_POINTS.index("WRIST")

    high_wrist_image_y = high.body.data[0, 0, wrist_index, 1]
    low_wrist_image_y = low.body.data[0, 0, wrist_index, 1]
    assert high_wrist_image_y < low_wrist_image_y


def test_pixel_normalization_uses_named_constants() -> None:
    frame = _right_hand_frame(y=0.0)
    pose = frames_to_pose((frame,))
    offsets = _component_offsets(pose.header)
    start, _count = offsets["RIGHT_HAND_LANDMARKS"]
    wrist_index = start + HAND_POINTS.index("WRIST")
    wrist_pixel = pose.body.data[0, 0, wrist_index]
    # Wrist at body (0, 0, 0) -> frame center.
    assert wrist_pixel[0] == FRAME_WIDTH / 2
    assert wrist_pixel[1] == FRAME_HEIGHT / 2
    assert BODY_UNITS_TO_PIXELS > 0  # named constant exists and is sane


def test_e6_frame_count_matches_sampled_frames() -> None:
    # E6 -- duration=0.8s, fps=25 -> 20 frames, same arithmetic as
    # timeline/sample.py's own test (this module must not re-derive it).
    frames = tuple(_right_hand_frame(y=0.0) for _ in range(20))
    pose = frames_to_pose(frames, fps=25)
    assert pose.body.data.shape[0] == 20
    assert pose.body.fps == 25


def test_e7_missing_track_gets_zero_confidence_not_garbage_coordinates() -> None:
    # E7 -- a sign with only a right hand: LEFT_HAND_LANDMARKS must be
    # confidence 0 for every point in every frame, not stray coordinates.
    frames = tuple(_right_hand_frame(y=float(i)) for i in range(3))
    pose = frames_to_pose(frames)
    offsets = _component_offsets(pose.header)
    start, count = offsets["LEFT_HAND_LANDMARKS"]
    left_hand_confidence = pose.body.confidence[:, 0, start : start + count]
    assert np.all(left_hand_confidence == 0.0)
    # pose-format masks 0-confidence points automatically (NumPyPoseBody
    # wraps data in a MaskedArray) -- confirms "missing," which is
    # stronger than merely checking the underlying numbers are 0.
    left_hand_data = pose.body.data[:, 0, start : start + count]
    assert np.ma.is_masked(left_hand_data)  # type: ignore[no-untyped-call]
    assert np.all(np.ma.getmaskarray(left_hand_data))  # type: ignore[no-untyped-call]
    assert np.all(np.ma.getdata(left_hand_data) == 0.0)  # type: ignore[no-untyped-call]

    right_start, right_count = offsets["RIGHT_HAND_LANDMARKS"]
    right_hand_confidence = pose.body.confidence[:, 0, right_start : right_start + right_count]
    assert np.all(right_hand_confidence == 1.0)


def test_non_hand_components_stay_present_at_zero_confidence() -> None:
    # C1 -- header keeps the full holistic topology; POSE/FACE/WORLD
    # components are present (not dropped) but always confidence 0 at this
    # task's scope (arm IK + torso are step 3, out of scope here).
    pose = frames_to_pose((_right_hand_frame(y=0.0),))
    component_names = {c.name for c in pose.header.components}
    assert component_names == {
        "POSE_LANDMARKS",
        "FACE_LANDMARKS",
        "LEFT_HAND_LANDMARKS",
        "RIGHT_HAND_LANDMARKS",
        "POSE_WORLD_LANDMARKS",
    }
    offsets = _component_offsets(pose.header)
    for name in ("POSE_LANDMARKS", "FACE_LANDMARKS", "POSE_WORLD_LANDMARKS"):
        start, count = offsets[name]
        assert np.all(pose.body.confidence[:, 0, start : start + count] == 0.0)


def test_e8_end_to_end_fsw_string_to_pose_file(tmp_path: Path) -> None:
    # E8 -- a real MVP-1 FSW string, all the way to a .pose file on disk.
    from fsw_r.core.fswr_converter import fsw_to_fswr
    from fsw_r.timeline.build import build_timeline
    from fsw_r.timeline.sample import sample

    fsw = "M508x515S10000493x485S22a04500x500"
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)

    out_path = tmp_path / "sign.pose"
    save_pose(pose, out_path)
    assert out_path.exists()
    assert out_path.stat().st_size > 0
