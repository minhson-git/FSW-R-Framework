from __future__ import annotations

import pytest

from fsw_r.groups.group_01_index_finger import (
    BaseSymbol01_01_001_Index,
    BaseSymbol01_01_007_IndexBent,
)


def test_joint_pose_identical_across_rotations_and_hand_sides() -> None:
    idx_front = BaseSymbol01_01_001_Index(fill=1, rotation=0)  # RIGHT
    idx_side = BaseSymbol01_01_001_Index(fill=1, rotation=2)  # RIGHT
    idx_back = BaseSymbol01_01_001_Index(fill=1, rotation=4)  # RIGHT
    idx_mirrored = BaseSymbol01_01_001_Index(fill=1, rotation=10)  # LEFT

    poses = [
        idx_front.get_joint_pose(),
        idx_side.get_joint_pose(),
        idx_back.get_joint_pose(),
        idx_mirrored.get_joint_pose(),
    ]
    assert all(pose == poses[0] for pose in poses)


def test_wrist_orientation_differs_by_rotation() -> None:
    idx_front = BaseSymbol01_01_001_Index(fill=1, rotation=0)
    idx_side = BaseSymbol01_01_001_Index(fill=1, rotation=2)
    idx_back = BaseSymbol01_01_001_Index(fill=1, rotation=4)

    front_quat = idx_front.get_wrist_orientation().as_quat()
    side_quat = idx_side.get_wrist_orientation().as_quat()
    back_quat = idx_back.get_wrist_orientation().as_quat()

    assert front_quat != pytest.approx(side_quat)
    assert front_quat != pytest.approx(back_quat)
    assert side_quat != pytest.approx(back_quat)

    # rotation=0 is the identity rotation
    assert front_quat == pytest.approx([0.0, 0.0, 0.0, 1.0])


def test_index_bent_overrides_only_index_finger() -> None:
    straight = BaseSymbol01_01_001_Index(fill=1, rotation=0)
    bent = BaseSymbol01_01_007_IndexBent(fill=1, rotation=0)

    straight_pose = straight.get_joint_pose()
    bent_pose = bent.get_joint_pose()

    assert bent_pose.index.pip.flexion == 90
    assert bent_pose.thumb == straight_pose.thumb
    assert bent_pose.middle == straight_pose.middle
    assert bent_pose.ring == straight_pose.ring
    assert bent_pose.pinky == straight_pose.pinky
