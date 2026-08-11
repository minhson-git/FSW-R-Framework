from __future__ import annotations

import numpy as np
import pytest

from pose_format.utils.holistic import HAND_POINTS
from scipy.spatial.transform import Rotation

from fsw_r.core.pose_table import HAND_POSE_TABLE
from fsw_r.core.types import HandSide
from fsw_r.export.forward_kinematics import hand_to_landmarks
from fsw_r.validation.normalization import (
    NORMALIZATION_SIZE,
    get_hand_normalizer,
    hands_to_pose,
    landmarks_dict_to_array,
    normalize_landmarks,
)

_STRAIGHT_INDEX = HAND_POSE_TABLE[0x100]  # "Index", a real Category 1 base symbol


def _sample_landmarks() -> np.ndarray[tuple[int, ...], np.dtype[np.float64]]:
    landmarks = hand_to_landmarks(_STRAIGHT_INDEX, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    return landmarks_dict_to_array(landmarks)


def test_normalizer_uses_size_150_matching_hands_py() -> None:
    assert NORMALIZATION_SIZE == 150.0
    assert get_hand_normalizer().size == 150.0


def test_normalization_is_idempotent() -> None:
    # Part B's mandatory test. This is NOT trivially true of
    # pose_format.utils.normalization_3d.PoseNormalizer on its own -- see
    # normalization.py's module docstring for the real ambiguity found and
    # fixed (a plane-normal sign flip, confirmed on real ground truth data
    # too, not just here) -- this test is what would have caught it.
    once = normalize_landmarks(_sample_landmarks())
    twice = normalize_landmarks(once)
    np.testing.assert_allclose(once, twice, atol=1e-4)


def test_normalization_is_idempotent_on_a_batch() -> None:
    batch = np.stack([_sample_landmarks(), _sample_landmarks() + 5.0])
    once = normalize_landmarks(batch)
    twice = normalize_landmarks(once)
    np.testing.assert_allclose(once, twice, atol=1e-4)


def test_normalized_wrist_is_at_origin() -> None:
    # PoseNormalizer.scale() translates to the line's first point (WRIST).
    normalized = normalize_landmarks(_sample_landmarks())
    assert np.allclose(normalized[0], 0.0)


def test_normalized_line_length_matches_size() -> None:
    normalized = normalize_landmarks(_sample_landmarks())
    wrist = normalized[HAND_POINTS.index("WRIST")]
    middle_mcp = normalized[HAND_POINTS.index("MIDDLE_FINGER_MCP")]
    assert np.linalg.norm(middle_mcp - wrist) == pytest.approx(NORMALIZATION_SIZE, abs=1e-3)


def test_translation_does_not_change_normalized_shape() -> None:
    # Normalization must remove POSITION, not just look similar.
    landmarks = _sample_landmarks()
    translated = landmarks + np.array([10.0, -20.0, 5.0])
    np.testing.assert_allclose(normalize_landmarks(landmarks), normalize_landmarks(translated), atol=1e-3)


def test_scaling_does_not_change_normalized_shape() -> None:
    # Normalization must remove SCALE too.
    landmarks = _sample_landmarks()
    scaled = landmarks * 3.0
    np.testing.assert_allclose(normalize_landmarks(landmarks), normalize_landmarks(scaled), atol=1e-3)


def test_hands_to_pose_builds_a_real_pose_with_right_hand_component() -> None:
    pose = hands_to_pose(_sample_landmarks())
    assert [c.name for c in pose.header.components] == ["RIGHT_HAND_LANDMARKS"]
    assert pose.body.data.shape[-2] == 21
