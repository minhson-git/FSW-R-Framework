from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_07_ring_finger import BaseSymbol01_07_001_IndexMiddleBaby


def test_joint_pose_identical_across_rotations_and_hand_sides() -> None:
    right_front = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=0)
    right_side = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=2)
    left_mirrored = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)

    pose = poses[0]
    assert pose.index.mcp.flexion == 0
    assert pose.middle.mcp.flexion == 0
    assert pose.ring.mcp.flexion == 90
    assert pose.pinky.mcp.flexion == 0


def test_wrist_orientation_differs_by_rotation() -> None:
    front = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=0)
    side = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=2)

    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


def test_symbol_id_and_hand_side() -> None:
    right = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=0)
    left = BaseSymbol01_07_001_IndexMiddleBaby(fill=1, rotation=10)

    assert right.symbol_id == "01-07-001"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


def test_symbol_from_fsw_builds_index_middle_baby() -> None:
    # 0x1a4 = group 7, base_symbol_number 1 ("Index Middle Baby").
    symbol = symbol_from_fsw("S1a412")
    assert isinstance(symbol, BaseSymbol01_07_001_IndexMiddleBaby)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == "01-07-001"
