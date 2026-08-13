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
    two_hand_closeup_pose,
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
    # The close-up module (this file's subject) must NOT alter the full-body
    # Pose fsw_r.export.pose_export.frames_to_pose produces -- it only crops a
    # COPY. The baseline values were recalibrated in Pha 17 (signbox->body
    # position scale reconciliation, PROGRESS.md): that changed where the HAND
    # is anchored, hence the wrist (236->231) and the IK-derived elbow
    # (358->353); the SHOULDER (241) and shoulder width (60% of frame) come
    # from body_geometry and are untouched by Pha 17. This test still guards
    # its real invariant -- the close-up transform leaves the body pose alone.
    pose = _demo_pose()

    def y_of(name: str) -> float:
        index = pose.header.get_point_index("POSE_LANDMARKS", name)
        return float(pose.body.data[0, 0, index, 1])

    def x_of(name: str) -> float:
        index = pose.header.get_point_index("POSE_LANDMARKS", name)
        return float(pose.body.data[0, 0, index, 0])

    assert y_of("RIGHT_SHOULDER") == pytest.approx(241, abs=1.0)
    assert y_of("RIGHT_ELBOW") == pytest.approx(353, abs=1.0)
    assert y_of("RIGHT_WRIST") == pytest.approx(231, abs=1.0)

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


# --- Two-hand side-by-side close-up (Pha 18) ---

# A real MVP-2 two-handed sign: RIGHT Index + LEFT Middle-Ring-Baby, two
# clearly different handshapes so "both are readable" is a meaningful check.
_TWO_HAND_SIGN = "M500x500S10010480x480S1cd1a520x520"


def _two_hand_pose() -> Pose:
    return frames_to_pose(sample(build_timeline(fsw_to_fswr(_TWO_HAND_SIGN))))


def _hand_x_range(pose: Pose, component_name: str) -> tuple[float, float]:
    start, count = _hand_component_range(pose, component_name)
    conf = pose.body.confidence[0, 0, start : start + count]
    xs = pose.body.data[0, 0, start : start + count, 0][conf > 0]
    return float(xs.min()), float(xs.max())


def test_two_hand_closeup_draws_both_hands() -> None:
    closeup = two_hand_closeup_pose(_two_hand_pose())
    for component_name in ("RIGHT_HAND_LANDMARKS", "LEFT_HAND_LANDMARKS"):
        start, count = _hand_component_range(closeup, component_name)
        assert closeup.body.confidence[:, 0, start : start + count].sum() > 0, f"{component_name} not drawn"


def test_two_hand_closeup_hands_do_not_overlap() -> None:
    # The whole point: the full-body view collapsed the two hands into one
    # blob; here they must sit in separate halves with a real gap between them.
    closeup = two_hand_closeup_pose(_two_hand_pose())
    _right_min, right_max = _hand_x_range(closeup, "RIGHT_HAND_LANDMARKS")
    left_min, _left_max = _hand_x_range(closeup, "LEFT_HAND_LANDMARKS")
    assert right_max < left_min, f"hands overlap: right reaches {right_max:.0f}, left starts {left_min:.0f}"


def test_two_hand_closeup_puts_right_hand_on_viewers_left() -> None:
    # Subject's RIGHT hand -> viewer's left half, matching pose_export's
    # selfie-mirror convention.
    closeup = two_hand_closeup_pose(_two_hand_pose())
    right_min, right_max = _hand_x_range(closeup, "RIGHT_HAND_LANDMARKS")
    left_min, left_max = _hand_x_range(closeup, "LEFT_HAND_LANDMARKS")
    assert (right_min + right_max) / 2 < FRAME_WIDTH / 2 < (left_min + left_max) / 2


def test_two_hand_closeup_works_with_a_single_active_hand() -> None:
    # A one-handed pose must still render (the one hand, in its half), not
    # crash -- two_hand_closeup_pose only draws hands that are active.
    closeup = two_hand_closeup_pose(_left_hand_pose())
    start, count = _hand_component_range(closeup, "LEFT_HAND_LANDMARKS")
    assert closeup.body.confidence[:, 0, start : start + count].sum() > 0


def test_two_hand_closeup_raises_when_no_hand_is_active() -> None:
    pose = _demo_pose()
    blanked = Pose(
        header=pose.header,
        body=type(pose.body)(
            fps=pose.body.fps,
            data=np.array(pose.body.data),
            confidence=np.zeros_like(np.array(pose.body.confidence)),
        ),
    )
    with pytest.raises(ValueError, match="neither hand is active"):
        two_hand_closeup_pose(blanked)
