"""Tests eval_fk_accuracy.py's pure functions with a small FAKE array --
NOT the real 18 MB hands.npy -- so CI can run this without fetching
anything (Part D's mandatory requirement)."""

from __future__ import annotations

import numpy as np

from eval_fk_accuracy import (
    BASE_COUNT,
    average_pose,
    group_of_base_hex,
    ground_truth_median,
    landmark_taxonomy,
    per_landmark_error,
    predict_landmarks,
    select_subset,
    verify_index_to_base_hex_mapping,
)
from fsw_r.core.pose_table import HAND_POSE_TABLE


def _fake_raw(bases: int = 3, fills: int = 6, crops: int = 48) -> np.ndarray[tuple[int, ...], np.dtype[np.float64]]:
    rng = np.random.default_rng(0)
    return rng.normal(size=(crops, bases, fills, 21, 3))


def test_select_subset_matches_hands_py_slicing() -> None:
    raw = _fake_raw(bases=3)
    subset = select_subset(raw)
    assert subset.shape == (16, 3, 3, 21, 3)
    np.testing.assert_array_equal(subset, raw[16:32, :, :3])


def test_ground_truth_median_shape_and_finiteness() -> None:
    raw = _fake_raw(bases=4)
    subset = select_subset(raw)
    median = ground_truth_median(subset)
    assert median.shape == (4, 21, 3)
    assert np.isfinite(median).all()


def test_ground_truth_median_is_deterministic() -> None:
    raw = _fake_raw(bases=2)
    subset = select_subset(raw)
    a = ground_truth_median(subset)
    b = ground_truth_median(subset)
    np.testing.assert_array_equal(a, b)


def test_predict_landmarks_shape() -> None:
    pose = HAND_POSE_TABLE[0x100]
    predicted = predict_landmarks(pose)
    assert predicted.shape == (21, 3)


def test_per_landmark_error_zero_for_identical_input() -> None:
    landmarks = predict_landmarks(HAND_POSE_TABLE[0x100])
    errors = per_landmark_error(landmarks, landmarks)
    assert np.allclose(errors, 0.0)


def test_landmark_taxonomy_covers_all_20_non_wrist_landmarks() -> None:
    taxonomy = landmark_taxonomy()
    assert len(taxonomy) == 20
    fingers = {t.finger for t in taxonomy}
    assert fingers == {"thumb", "index", "middle", "ring", "pinky"}


def test_average_pose_of_identical_poses_equals_that_pose() -> None:
    pose = HAND_POSE_TABLE[0x100]
    avg = average_pose([pose, pose, pose])
    assert avg.index.mcp.flexion == pose.index.mcp.flexion
    assert avg.thumb.cmc.flexion == pose.thumb.cmc.flexion


def test_group_of_base_hex_covers_all_10_groups() -> None:
    assert group_of_base_hex(0x100) == 1  # first base of group 1
    assert group_of_base_hex(0x204) == 10  # last base of group 10 (0x205 is Category 2)
    groups_seen = {group_of_base_hex(0x100 + i) for i in range(BASE_COUNT)}
    assert groups_seen == set(range(1, 11))


def test_verify_index_to_base_hex_mapping_finds_the_known_7_exceptions() -> None:
    # A3 -- cross-checked in the task brief against the real
    # iswa_valid_combinations.json: exactly 7 bases have fill=0 invalid
    # (fills=[1] only), each producing 2 warnings (fill=0 and fill=2, since
    # hands.py's ground truth always includes fills 0-2).
    warnings = verify_index_to_base_hex_mapping()
    assert len(warnings) == 14
    assert all("0x14d" in w or "0x14f" in w or "0x151" in w or "0x15c" in w or "0x15e" in w
               or "0x1f6" in w or "0x204" in w for w in warnings)
