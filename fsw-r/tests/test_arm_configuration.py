"""C1-C7 (this task's brief, "Sửa bug hướng xoay IK + chỉnh khung hình
demo", Part C). The class of test the previous "khung hình dễ đọc hơn"
task was missing: geometry INVARIANTS on the arm configuration itself, not
just bone lengths (``tests/test_arm_ik.py``'s own pre-existing C1/C2) or
symmetry alone. All 1,407+5 tests before this task passed with a
hyperextended-looking elbow -- these tests are written so that specific
failure mode (elbow well outside the shoulder-wrist vertical span) cannot
silently pass again.

Uses the SAME closed-form ``solve_two_bone_ik`` (see ``arm_ik.py`` -- no
new solver here), and the SAME real bone lengths from
``body_geometry.py``/``anthropometry.py`` this project already derives
from ``ASSUMED_STATURE_MM`` -- no new hardcoded numbers besides the
wrist-offset FRACTIONS OF MAX REACH used to build the 4 configs below
(0.55/0.45/0.45/0.85 of ``upper_arm_length + forearm_length``), which are
deliberately expressed as fractions of the real reach rather than raw body
units so they scale automatically if those lengths ever change.
"""

from __future__ import annotations

import numpy as np
import pytest
from numpy.typing import NDArray

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.export.arm_ik import POLE_DIRECTION_LEFT, POLE_DIRECTION_RIGHT, solve_two_bone_ik
from fsw_r.export.body_geometry import FOREARM_LENGTH, UPPER_ARM_LENGTH, shoulder_position
from fsw_r.export.pose_export import FRAME_WIDTH, _component_offsets, frames_to_pose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from pose_format.utils.holistic import holistic_components

_L1 = UPPER_ARM_LENGTH
_L2 = FOREARM_LENGTH
_REACH = _L1 + _L2
_EPS = 0.15  # this task brief's own example tolerance for C1 ("ví dụ 0.15")

_POSE_POINT_NAMES = [c.points for c in holistic_components() if c.name == "POSE_LANDMARKS"][0]


def _configs(is_right: bool) -> dict[str, NDArray[np.float64]]:
    """The 4 configurations this task's brief names for C1
    ("cổ tay ngang vai, cao hơn vai, thấp hơn vai, và dang xa sang ngang"),
    built as OFFSETS FROM THE SHOULDER expressed as fractions of the arm's
    own max reach (so they stay "moderate, in-reach" configurations
    regardless of the exact bone lengths) -- signed by ``is_right`` so a
    right-arm config and a left-arm config are true mirror images (needed
    by C4)."""
    shoulder = shoulder_position(is_right)
    sign = 1.0 if is_right else -1.0  # right shoulder sits at -x, so "away from midline" is +x for the right side
    return {
        "level": shoulder + np.array([sign * 0.55 * _REACH, 0.0, 0.0]),
        "high": shoulder + np.array([sign * 0.45 * _REACH, 0.35 * _REACH, 0.1 * _REACH]),
        "low": shoulder + np.array([sign * 0.45 * _REACH, -0.35 * _REACH, 0.1 * _REACH]),
        "splayed": shoulder + np.array([sign * 0.85 * _REACH, 0.05 * _REACH, 0.0]),
    }


@pytest.mark.parametrize("is_right", [True, False])
@pytest.mark.parametrize("config_name", ["level", "high", "low", "splayed"])
def test_c1_elbow_stays_within_the_shoulder_wrist_vertical_span(config_name: str, is_right: bool) -> None:
    shoulder = shoulder_position(is_right)
    pole = POLE_DIRECTION_RIGHT if is_right else POLE_DIRECTION_LEFT
    wrist = _configs(is_right)[config_name]

    elbow = solve_two_bone_ik(shoulder, wrist, pole, _L1, _L2)

    lo = min(shoulder[1], wrist[1]) - _EPS
    hi = max(shoulder[1], wrist[1]) + _EPS
    assert lo <= elbow[1] <= hi, f"{config_name} (is_right={is_right}): elbow.y={elbow[1]:.3f} outside [{lo:.3f}, {hi:.3f}]"


@pytest.mark.parametrize("is_right", [True, False])
@pytest.mark.parametrize("config_name", ["level", "high", "low", "splayed"])
def test_c2_elbow_leans_toward_the_pole_direction(config_name: str, is_right: bool) -> None:
    shoulder = shoulder_position(is_right)
    pole = POLE_DIRECTION_RIGHT if is_right else POLE_DIRECTION_LEFT
    wrist = _configs(is_right)[config_name]

    elbow = solve_two_bone_ik(shoulder, wrist, pole, _L1, _L2)
    midpoint = (shoulder + wrist) / 2

    assert np.dot(elbow - midpoint, pole) > 0


@pytest.mark.parametrize("is_right", [True, False])
@pytest.mark.parametrize("config_name", ["level", "high", "low", "splayed"])
def test_c3_bone_lengths_are_preserved(config_name: str, is_right: bool) -> None:
    # Same invariant test_arm_ik.py's own (differently-numbered, predates
    # this task) C2 already checks with a single config -- repeated here,
    # parametrized across this task's own 4 configs, so a future change to
    # the elbow formula that happens to preserve lengths for ONE config but
    # not another still gets caught by this task's own C-numbering.
    shoulder = shoulder_position(is_right)
    pole = POLE_DIRECTION_RIGHT if is_right else POLE_DIRECTION_LEFT
    wrist = _configs(is_right)[config_name]

    elbow = solve_two_bone_ik(shoulder, wrist, pole, _L1, _L2)

    assert np.linalg.norm(elbow - shoulder) == pytest.approx(_L1, abs=1e-6)
    assert np.linalg.norm(wrist - elbow) == pytest.approx(_L2, abs=1e-6)


@pytest.mark.parametrize("config_name", ["level", "high", "low", "splayed"])
def test_c4_mirrored_configs_produce_mirrored_elbows(config_name: str) -> None:
    right_shoulder = shoulder_position(is_right=True)
    left_shoulder = shoulder_position(is_right=False)
    right_wrist = _configs(True)[config_name]
    left_wrist = _configs(False)[config_name]

    right_elbow = solve_two_bone_ik(right_shoulder, right_wrist, POLE_DIRECTION_RIGHT, _L1, _L2)
    left_elbow = solve_two_bone_ik(left_shoulder, left_wrist, POLE_DIRECTION_LEFT, _L1, _L2)

    # Mirror across the body midline (x=0): x negates, y/z match.
    assert right_elbow[0] == pytest.approx(-left_elbow[0], abs=1e-6)
    assert right_elbow[1] == pytest.approx(left_elbow[1], abs=1e-6)
    assert right_elbow[2] == pytest.approx(left_elbow[2], abs=1e-6)


# C5 -- the 3 boundary cases (wrist beyond max reach, closer than min
# reach, coincident with the shoulder) are already covered by
# tests/test_arm_ik.py's test_c3_wrist_*_does_not_raise_or_nan (predates
# this task, unchanged by it -- the boundary-clamping logic in
# solve_two_bone_ik's d_clamped step was not touched by this task's fix,
# only the bend-direction formula and the pole constants were). Not
# duplicated here to keep one source of truth for that coverage.


def test_c6_shoulder_occupies_50_to_70_percent_of_frame_width() -> None:
    fsw = "M508x515S10000493x485S22a04500x500"
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)

    offsets = _component_offsets(pose.header)
    start, _count = offsets["POSE_LANDMARKS"]
    left_x = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("LEFT_SHOULDER"), 0]
    right_x = pose.body.data[0, 0, start + _POSE_POINT_NAMES.index("RIGHT_SHOULDER"), 0]

    fraction = abs(float(left_x - right_x)) / FRAME_WIDTH
    assert 0.50 <= fraction <= 0.70, f"shoulder occupies {fraction:.2%} of frame width, expected 50-70%"


# C7 (this task's brief: "1.412 test cũ pass nguyên") is the whole existing
# suite, not a new test here. The one PRE-EXISTING test that legitimately
# had to change is tests/test_readable_demo_frame.py's
# test_c5_figure_height_stays_in_a_measured_range_after_ik_fix (was
# "70-90% of frame height" -- that specific NUMBER was this task's own
# target to change, per Part B, not a test locking in wrong arm-geometry
# behavior; see that test's own comment for the full reasoning) -- no
# other pre-existing test needed touching, confirmed by running the full
# suite after this task's arm_ik.py/pose_export.py changes.
