from __future__ import annotations

import numpy as np
import pytest

from fsw_r.export.body_geometry import (
    FOREARM_LENGTH,
    UPPER_ARM_LENGTH,
    hip_position,
    shoulder_position,
    static_head_landmarks,
)


def test_shoulders_are_symmetric_about_the_midline() -> None:
    right = shoulder_position(is_right=True)
    left = shoulder_position(is_right=False)
    assert right[0] == -left[0]
    assert right[1] == left[1] == 0.0
    assert right[2] == left[2]


def test_hips_are_symmetric_and_below_shoulders() -> None:
    right_shoulder = shoulder_position(is_right=True)
    right_hip = hip_position(is_right=True)
    left_hip = hip_position(is_right=False)
    assert right_hip[0] == -left_hip[0]
    # body-space y is up -- hip must be BELOW (smaller y than) the shoulder.
    assert right_hip[1] < right_shoulder[1]


def test_arm_segment_lengths_are_positive_and_named() -> None:
    assert UPPER_ARM_LENGTH > 0
    assert FOREARM_LENGTH > 0


def test_static_head_landmarks_cover_exactly_the_briefs_5_points() -> None:
    landmarks = static_head_landmarks()
    assert set(landmarks) == {"NOSE", "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT"}
    for point in landmarks.values():
        assert np.all(np.isfinite(point))


def test_ears_are_symmetric_about_the_midline() -> None:
    landmarks = static_head_landmarks()
    assert landmarks["LEFT_EAR"][0] == -landmarks["RIGHT_EAR"][0]
    assert landmarks["LEFT_EAR"][1] == pytest.approx(landmarks["RIGHT_EAR"][1])


def test_head_is_above_shoulders() -> None:
    landmarks = static_head_landmarks()
    shoulder_y = shoulder_position(is_right=True)[1]
    assert landmarks["NOSE"][1] > shoulder_y
