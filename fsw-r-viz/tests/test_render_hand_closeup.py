"""C1-C6 (this task's brief, "Video cận cảnh bàn tay", Part C).

Tests the PURE data transform (``hand_closeup_pose``), not the video/GIF
file itself -- this environment has neither vidgear nor a real ffmpeg
binary (see ``test_render_pose_video.py``'s own fallback tests), and the
close-up's actual video encoding is the exact same
``PoseVisualizer.save_video``/``save_gif`` fallback path
``render_pose_video.py`` already has dedicated tests for -- no need to
duplicate that here.
"""

from __future__ import annotations

import numpy as np
import pytest
from pose_format import Pose
from scipy.spatial.transform import Rotation

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.export.pose_export import FRAME_HEIGHT, FRAME_WIDTH, frames_to_pose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import PoseFrame, TrackName, TrackPose
from fsw_r_viz.render_hand_closeup import (
    HAND_CLOSEUP_TARGET_FRACTION,
    _hand_component_range,
    hand_closeup_pose,
)

# Same standard MVP-1 demo sign used throughout this project's demo/test
# suite (see e.g. tests/test_arm_configuration.py) -- Index handshape +
# Straight Wall Plane movement.
_MVP1_SIGN = "M508x515S10000493x485S22a04500x500"

_FLAT_ANGLE = JointAngle(flexion=0.0, abduction=0.0)
_FLAT_FINGER = FingerPose(mcp=_FLAT_ANGLE, pip=_FLAT_ANGLE, dip=_FLAT_ANGLE)
_FLAT_POSE = HandJointPose(
    thumb=ThumbPose(cmc=_FLAT_ANGLE, mcp=_FLAT_ANGLE, ip=_FLAT_ANGLE),
    index=_FLAT_FINGER,
    middle=_FLAT_FINGER,
    ring=_FLAT_FINGER,
    pinky=_FLAT_FINGER,
)


def _demo_pose() -> Pose:
    positioned = fsw_to_fswr(_MVP1_SIGN)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    return frames_to_pose(frames)


def _left_hand_pose() -> Pose:
    # C5 -- MVP-1's own SignTimeline only ever populates ONE track
    # (RIGHT_HAND, see timeline/sample.py), so there is no real FSW sign
    # to reach a LEFT_HAND-populated Pose through. Build one directly via
    # fsw_r.export.pose_export.frames_to_pose (public, unmodified by this
    # task) with a synthetic LEFT_HAND track -- the same pattern
    # tests/test_body_and_arm.py's own two-handed test uses.
    frame = PoseFrame(
        time_seconds=0.0,
        tracks={
            TrackName.LEFT_HAND: TrackPose(
                joint_pose=_FLAT_POSE, wrist=Rotation.identity(), position=np.array([0.3, 0.0, 0.0])
            ),
        },
    )
    return frames_to_pose((frame,))


def _bbox_height_and_min_mcp_distance(pose: Pose, component_name: str) -> tuple[float, float]:
    start, count = _hand_component_range(pose, component_name)
    all_y = []
    for frame_index in range(pose.body.data.shape[0]):
        conf = pose.body.confidence[frame_index, 0, start:start + count]
        ys = pose.body.data[frame_index, 0, start:start + count, 1][conf > 0]
        all_y.extend(ys.tolist())
    height = max(all_y) - min(all_y)

    component = [c for c in pose.header.components if c.name == component_name][0]
    mcp_names = [p for p in component.points if p.endswith("_MCP")]
    mcp_points = np.array(
        [pose.body.data[0, 0, start + component.points.index(n), :2] for n in mcp_names]
    )
    distances = [
        float(np.linalg.norm(mcp_points[i] - mcp_points[j]))
        for i in range(len(mcp_points))
        for j in range(i + 1, len(mcp_points))
    ]
    return height, min(distances)


def test_c1_hand_occupies_70_to_90_percent_of_frame_height() -> None:
    pose = _demo_pose()
    closeup = hand_closeup_pose(pose, TrackName.RIGHT_HAND)
    height, _min_mcp = _bbox_height_and_min_mcp_distance(closeup, "RIGHT_HAND_LANDMARKS")
    fraction = height / FRAME_HEIGHT
    assert 0.70 <= fraction <= 0.90, f"hand occupies {fraction:.2%} of frame height, expected 70-90%"


def test_c2_min_mcp_distance_is_at_least_20px_after_zoom() -> None:
    pose = _demo_pose()
    closeup = hand_closeup_pose(pose, TrackName.RIGHT_HAND)
    _height, min_mcp = _bbox_height_and_min_mcp_distance(closeup, "RIGHT_HAND_LANDMARKS")
    assert min_mcp >= 20.0, f"min MCP-MCP distance {min_mcp:.1f}px, expected >= 20px"


def test_c3_wrist_sits_near_the_horizontal_center() -> None:
    pose = _demo_pose()
    closeup = hand_closeup_pose(pose, TrackName.RIGHT_HAND)
    start, _count = _hand_component_range(closeup, "RIGHT_HAND_LANDMARKS")
    wrist_index = closeup.header.get_point_index("RIGHT_HAND_LANDMARKS", "WRIST")
    wrist_x = closeup.body.data[0, 0, wrist_index, 0]
    assert wrist_x == pytest.approx(FRAME_WIDTH / 2.0, abs=1.0)


def test_c4_full_body_video_data_is_unchanged() -> None:
    # This task touches ONLY fsw-r-viz's new render_hand_closeup.py -- the
    # full-body Pose fsw_r.export.pose_export.frames_to_pose produces
    # (what render_pose_video.py's body video draws) must be byte-for-byte
    # what it already was on the "sửa lại bất biến IK sai" baseline
    # (commit b54854d): shoulder.y=241, elbow.y=358, wrist.y=236, shoulder
    # width 60% of frame -- see this task's own PROGRESS.md entry for the
    # full before/after table this reproduces.
    pose = _demo_pose()

    def y_of(name: str) -> float:
        index = pose.header.get_point_index("POSE_LANDMARKS", name)
        return float(pose.body.data[0, 0, index, 1])

    def x_of(name: str) -> float:
        index = pose.header.get_point_index("POSE_LANDMARKS", name)
        return float(pose.body.data[0, 0, index, 0])

    assert y_of("RIGHT_SHOULDER") == pytest.approx(241, abs=1.0)
    assert y_of("RIGHT_ELBOW") == pytest.approx(358, abs=1.0)
    assert y_of("RIGHT_WRIST") == pytest.approx(236, abs=1.0)

    shoulder_width_fraction = abs(x_of("LEFT_SHOULDER") - x_of("RIGHT_SHOULDER")) / FRAME_WIDTH
    assert shoulder_width_fraction == pytest.approx(0.60, abs=0.01)


@pytest.mark.parametrize("hand", [TrackName.RIGHT_HAND, TrackName.LEFT_HAND])
def test_c5_works_for_both_hands(hand: TrackName) -> None:
    pose = _demo_pose() if hand == TrackName.RIGHT_HAND else _left_hand_pose()
    component_name = "RIGHT_HAND_LANDMARKS" if hand == TrackName.RIGHT_HAND else "LEFT_HAND_LANDMARKS"

    closeup = hand_closeup_pose(pose, hand)
    height, min_mcp = _bbox_height_and_min_mcp_distance(closeup, component_name)
    fraction = height / FRAME_HEIGHT

    assert 0.70 <= fraction <= 0.90
    assert min_mcp >= 20.0


# C6 (this task's brief: "1.441 test cũ pass nguyên") is the whole
# existing suite, not a new test here.
