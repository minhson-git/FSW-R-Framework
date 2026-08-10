from __future__ import annotations

import numpy as np
import pytest
from pose_format.utils.holistic import HAND_POINTS
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, HandSide, JointAngle, ThumbPose
from fsw_r.export.forward_kinematics import hand_to_landmarks


def _uniform_pose(flexion: float) -> HandJointPose:
    angle = JointAngle(flexion=flexion, abduction=0.0)
    finger = FingerPose(mcp=angle, pip=angle, dip=angle)
    return HandJointPose(
        thumb=ThumbPose(cmc=JointAngle(0.0, 0.0), mcp=angle, ip=angle),
        index=finger,
        middle=finger,
        ring=finger,
        pinky=finger,
    )


_STRAIGHT = _uniform_pose(0.0)
_FIST = _uniform_pose(80.0)


def test_e1_returns_exactly_21_landmarks_matching_hand_points() -> None:
    landmarks = hand_to_landmarks(_STRAIGHT, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    assert len(landmarks) == 21 == len(HAND_POINTS)
    assert set(landmarks) == set(HAND_POINTS)


@pytest.mark.parametrize("finger", ["index", "middle", "ring", "pinky"])
def test_e3_straight_hand_finger_points_are_collinear(finger: str) -> None:
    landmarks = hand_to_landmarks(_STRAIGHT, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    prefix = {"index": "INDEX_FINGER", "middle": "MIDDLE_FINGER", "ring": "RING_FINGER", "pinky": "PINKY"}[finger]
    mcp, pip, dip, tip = (landmarks[f"{prefix}_{joint}"] for joint in ("MCP", "PIP", "DIP", "TIP"))
    v1 = pip - mcp
    v2 = tip - pip
    cross = np.cross(v1, v2)
    assert np.linalg.norm(cross) < 1e-9


@pytest.mark.parametrize("finger", ["index", "middle", "ring", "pinky", "thumb"])
def test_e4_fist_tip_is_closer_to_wrist_than_straight(finger: str) -> None:
    straight = hand_to_landmarks(_STRAIGHT, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    fist = hand_to_landmarks(_FIST, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    tip_name = {
        "index": "INDEX_FINGER_TIP",
        "middle": "MIDDLE_FINGER_TIP",
        "ring": "RING_FINGER_TIP",
        "pinky": "PINKY_TIP",
        "thumb": "THUMB_TIP",
    }[finger]
    d_straight = np.linalg.norm(straight[tip_name] - straight["WRIST"])
    d_fist = np.linalg.norm(fist[tip_name] - fist["WRIST"])
    assert d_fist < d_straight


def test_e5_forward_kinematics_is_deterministic() -> None:
    wrist_pos = np.array([0.1, 0.2, 0.3])
    wrist_rot = Rotation.from_euler("xyz", [10, 20, 30], degrees=True)
    a = hand_to_landmarks(_FIST, wrist_rot, wrist_pos, HandSide.LEFT)
    b = hand_to_landmarks(_FIST, wrist_rot, wrist_pos, HandSide.LEFT)
    for name in HAND_POINTS:
        assert np.array_equal(a[name], b[name]), f"{name} differs between identical calls"


def test_left_hand_thumb_mirrors_right_hand_thumb_across_x() -> None:
    right = hand_to_landmarks(_STRAIGHT, Rotation.identity(), np.zeros(3), HandSide.RIGHT)
    left = hand_to_landmarks(_STRAIGHT, Rotation.identity(), np.zeros(3), HandSide.LEFT)
    for name in ("THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP"):
        assert left[name] == pytest.approx(right[name] * np.array([-1.0, 1.0, 1.0]))


def test_unrecognized_hand_points_name_raises() -> None:
    from fsw_r.export.forward_kinematics import _finger_and_joint

    with pytest.raises(ValueError):
        _finger_and_joint("NOT_A_REAL_LANDMARK")
