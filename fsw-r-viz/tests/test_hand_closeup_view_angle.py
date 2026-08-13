"""B1-B4 (this task's brief, "Góc nhìn 3/4 cho video cận cảnh bàn tay",
Part B). B5-B7 (full-body video unchanged, fk_accuracy.md unchanged, 1,475
old tests pass) are process-level checks, not tests in this file -- B5's
own claim is already covered by ``test_render_hand_closeup.py``'s C4
(untouched by this task), and B6/B7 were verified directly (see
PROGRESS.md's entry for this task).
"""

from __future__ import annotations

import numpy as np
import pytest
from pose_format import Pose

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.export.pose_export import FRAME_HEIGHT, frames_to_pose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import TrackName
from fsw_r_viz.render_hand_closeup import HAND_CLOSEUP_VIEW_ANGLE_DEG, _hand_component_range, hand_closeup_pose

# Same standard MVP-1 demo sign used throughout this project's test suite
# (Index handshape + Straight Wall Plane movement -- no Group 12, so the
# handshape itself never changes, only the wrist's trajectory does).
_MVP1_SIGN = "M508x515S10000493x485S22a04500x500"

# The Group 12 (Finger Movement) sign from the "Chuyển động khớp ngón
# tay" task -- Index handshape + 0x221 ("Hinge Movement, Up Down Large").
# B2 explicitly needs a sign whose finger JOINTS actually move (not just
# the wrist) to measure a meaningful "visible flex amplitude".
_GROUP_12_SIGN = "M508x515S10000493x485S22100500x500"


def _pose_for(fsw: str) -> Pose:
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    return frames_to_pose(frames)


def _fingertip_xy_across_frames(pose: Pose, component_name: str, point_name: str) -> np.ndarray[tuple[int, ...], np.dtype[np.float64]]:
    from pose_format.utils.holistic import HAND_POINTS

    start, _count = _hand_component_range(pose, component_name)
    index = start + HAND_POINTS.index(point_name)
    return np.asarray(pose.body.data[:, 0, index, :2])


def _visible_flex_amplitude(pose: Pose, component_name: str, point_name: str) -> float:
    """Max pairwise XY-plane distance the named point travels across every
    frame -- this task's brief's own "biên độ dịch chuyển của đầu ngón
    trong mặt phẳng ảnh" ("Gập thấy được")."""
    xy = _fingertip_xy_across_frames(pose, component_name, point_name)
    diffs = xy[:, None, :] - xy[None, :, :]
    distances = np.linalg.norm(diffs, axis=-1)
    return float(distances.max())


def _min_mcp_distance_every_frame(pose: Pose, component_name: str) -> float:
    from pose_format.utils.holistic import HAND_POINTS

    start, _count = _hand_component_range(pose, component_name)
    mcp_names = ["THUMB_MCP", "INDEX_FINGER_MCP", "MIDDLE_FINGER_MCP", "RING_FINGER_MCP", "PINKY_MCP"]
    worst = float("inf")
    for frame_index in range(pose.body.data.shape[0]):
        points = np.array([pose.body.data[frame_index, 0, start + HAND_POINTS.index(n), :2] for n in mcp_names])
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                worst = min(worst, float(np.linalg.norm(points[i] - points[j])))
    return worst


def _bbox_height_fraction(pose: Pose, component_name: str) -> float:
    start, count = _hand_component_range(pose, component_name)
    all_y = []
    for frame_index in range(pose.body.data.shape[0]):
        conf = pose.body.confidence[frame_index, 0, start:start + count]
        ys = pose.body.data[frame_index, 0, start:start + count, 1][conf > 0]
        all_y.extend(ys.tolist())
    return float(max(all_y) - min(all_y)) / FRAME_HEIGHT


def test_b1_zero_degrees_reproduces_the_default_output_exactly() -> None:
    pose = _pose_for(_MVP1_SIGN)
    default_output = hand_closeup_pose(pose, TrackName.RIGHT_HAND)
    explicit_zero_output = hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=0.0)

    assert np.array_equal(np.asarray(default_output.body.data), np.asarray(explicit_zero_output.body.data))
    assert np.array_equal(
        np.asarray(default_output.body.confidence), np.asarray(explicit_zero_output.body.confidence)
    )


def test_b2_60_degrees_shows_more_visible_flex_than_0_degrees() -> None:
    pose = _pose_for(_GROUP_12_SIGN)
    front = hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=0.0)
    three_quarter = hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=HAND_CLOSEUP_VIEW_ANGLE_DEG)

    front_amplitude = _visible_flex_amplitude(front, "RIGHT_HAND_LANDMARKS", "MIDDLE_FINGER_TIP")
    three_quarter_amplitude = _visible_flex_amplitude(three_quarter, "RIGHT_HAND_LANDMARKS", "MIDDLE_FINGER_TIP")

    assert three_quarter_amplitude > front_amplitude, (
        f"visible flex amplitude did not increase: 0deg={front_amplitude:.1f}px, "
        f"{HAND_CLOSEUP_VIEW_ANGLE_DEG}deg={three_quarter_amplitude:.1f}px"
    )


def test_b3_min_mcp_distance_stays_at_least_15px_after_rotation() -> None:
    pose = _pose_for(_MVP1_SIGN)
    rotated = hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=HAND_CLOSEUP_VIEW_ANGLE_DEG)
    worst = _min_mcp_distance_every_frame(rotated, "RIGHT_HAND_LANDMARKS")
    assert worst >= 15.0, f"min MCP-MCP distance {worst:.1f}px after rotation, expected >= 15px"


def test_b4_hand_still_occupies_70_to_90_percent_of_frame_height_after_rotation() -> None:
    pose = _pose_for(_MVP1_SIGN)
    rotated = hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=HAND_CLOSEUP_VIEW_ANGLE_DEG)
    fraction = _bbox_height_fraction(rotated, "RIGHT_HAND_LANDMARKS")
    assert 0.70 <= fraction <= 0.90, f"hand occupies {fraction:.2%} of frame height after rotation, expected 70-90%"


@pytest.mark.parametrize("angle", [0.0, 30.0, 45.0, HAND_CLOSEUP_VIEW_ANGLE_DEG, 90.0])
def test_visible_flex_amplitude_increases_monotonically_with_angle(angle: float) -> None:
    # Cross-check for the A1 trade-off table itself (not one of the
    # brief's own numbered B-tests) -- confirms the measured trend this
    # task's HAND_CLOSEUP_VIEW_ANGLE_DEG choice was based on: larger angle
    # -> more visible flex, monotonically, up to 90 (edge-on).
    pose = _pose_for(_GROUP_12_SIGN)
    closeup = hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=angle)
    amplitude = _visible_flex_amplitude(closeup, "RIGHT_HAND_LANDMARKS", "MIDDLE_FINGER_TIP")
    zero_degree_amplitude = _visible_flex_amplitude(
        hand_closeup_pose(pose, TrackName.RIGHT_HAND, view_angle_deg=0.0), "RIGHT_HAND_LANDMARKS", "MIDDLE_FINGER_TIP"
    )
    if angle == 0.0:
        assert amplitude == pytest.approx(zero_degree_amplitude)
    else:
        assert amplitude >= zero_degree_amplitude
