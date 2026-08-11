"""C4-C6 (this task's brief, Part C) -- integration tests for the
body/arm points ``pose_export.frames_to_pose`` now fills in, on top of
``test_pose_export.py``'s existing hand-only coverage."""

from __future__ import annotations

import numpy as np
from pose_format.utils.holistic import HAND_POINTS, holistic_components
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.export.pose_export import _component_offsets, frames_to_pose
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

_POSE_POINT_NAMES = [c.points for c in holistic_components() if c.name == "POSE_LANDMARKS"][0]
_LEG_INDICES = [_POSE_POINT_NAMES.index(n) for n in ("LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE",
                                                       "LEFT_HEEL", "RIGHT_HEEL", "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX")]


def _right_hand_frame(position: np.ndarray[tuple[int, ...], np.dtype[np.float64]]) -> PoseFrame:
    track_pose = TrackPose(joint_pose=_FLAT_POSE, wrist=Rotation.identity(), position=position)
    return PoseFrame(time_seconds=0.0, tracks={TrackName.RIGHT_HAND: track_pose})


def test_c4_shoulder_is_above_hip_in_image_space() -> None:
    # C4 -- shoulder must have a SMALLER image-y than hip (shoulder is
    # visually above hip). Protects the y-flip in _body_to_pixel against a
    # regression introduced by this task's new points, same reasoning as
    # test_pose_export.py's E2 for the hand.
    pose = frames_to_pose((_right_hand_frame(np.array([0.0, 0.0, 0.0])),))
    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]
    shoulder_y = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("RIGHT_SHOULDER"), 1]
    hip_y = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("RIGHT_HIP"), 1]
    assert shoulder_y < hip_y


def test_c5_point_count_increases_clearly_and_legs_stay_zero() -> None:
    # C5 -- was 21 (hand only) before this task; must be clearly higher now.
    pose = frames_to_pose((_right_hand_frame(np.array([0.3, 0.0, 0.2])),))
    total_active = int((pose.body.confidence[0, 0] > 0).sum())
    assert total_active > 21

    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]
    leg_confidence = pose.body.confidence[0, 0, [start + i for i in _LEG_INDICES]]
    assert np.all(leg_confidence == 0.0)


def test_c5_two_handed_sign_reaches_around_60_points() -> None:
    # Supplementary to C5 -- confirms this task brief's own "khoảng 60+"
    # estimate is reached for a two-handed frame (MVP-1 itself is
    # single-hand only, see timeline/build.py, so a one-handed sign tops
    # out lower -- see PROGRESS.md's export-layer entry for the exact
    # count and why the brief's estimate assumed two hands).
    frame = PoseFrame(
        time_seconds=0.0,
        tracks={
            TrackName.RIGHT_HAND: TrackPose(joint_pose=_FLAT_POSE, wrist=Rotation.identity(), position=np.array([0.3, 0.0, 0.0])),
            TrackName.LEFT_HAND: TrackPose(joint_pose=_FLAT_POSE, wrist=Rotation.identity(), position=np.array([-0.3, 0.0, 0.0])),
        },
    )
    pose = frames_to_pose((frame,))
    assert int((pose.body.confidence[0, 0] > 0).sum()) >= 60


def test_c6_pose_wrist_matches_hand_wrist_exactly() -> None:
    # C6 -- POSE_LANDMARKS.RIGHT_WRIST and RIGHT_HAND_LANDMARKS.WRIST must
    # be pixel-identical every frame, or the arm visually disconnects from
    # the hand.
    frames = tuple(_right_hand_frame(np.array([0.1 * i, 0.2, -0.1])) for i in range(5))
    pose = frames_to_pose(frames)
    offsets = _component_offsets(pose.header)
    pose_start, _ = offsets["POSE_LANDMARKS"]
    hand_start, _ = offsets["RIGHT_HAND_LANDMARKS"]
    pose_wrist_index = pose_start + _POSE_POINT_NAMES.index("RIGHT_WRIST")
    hand_wrist_index = hand_start + HAND_POINTS.index("WRIST")

    for frame_index in range(len(frames)):
        pose_wrist = pose.body.data[frame_index, 0, pose_wrist_index]
        hand_wrist = pose.body.data[frame_index, 0, hand_wrist_index]
        np.testing.assert_array_equal(pose_wrist, hand_wrist)


def test_inactive_side_arm_points_stay_zero_confidence() -> None:
    # A right-hand-only sign: every LEFT arm/hand-duplicate point in
    # POSE_LANDMARKS must stay confidence 0 -- shoulders/hips are static
    # (both sides always drawn), but the arm itself needs a wrist to solve
    # IK against.
    pose = frames_to_pose((_right_hand_frame(np.array([0.0, 0.0, 0.0])),))
    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]
    for name in ("LEFT_ELBOW", "LEFT_WRIST", "LEFT_PINKY", "LEFT_INDEX", "LEFT_THUMB"):
        index = start + _POSE_POINT_NAMES.index(name)
        assert pose.body.confidence[0, 0, index] == 0.0

    for name in ("LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP"):
        index = start + _POSE_POINT_NAMES.index(name)
        assert pose.body.confidence[0, 0, index] == 1.0
