from __future__ import annotations

import pytest

from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_05_five_fingers import BaseSymbol01_05_001_FiveFingersSpread


def test_joint_pose_identical_across_rotations_and_hand_sides() -> None:
    right_front = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=0)
    right_side = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=2)
    left_mirrored = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=10)

    poses = [right_front.get_joint_pose(), right_side.get_joint_pose(), left_mirrored.get_joint_pose()]
    assert all(pose == poses[0] for pose in poses)

    pose = poses[0]
    assert pose.index.mcp.flexion == 8
    assert pose.thumb.cmc.flexion == 26


def test_wrist_orientation_differs_by_rotation() -> None:
    front = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=0)
    side = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=2)

    assert front.get_wrist_orientation().as_quat() != pytest.approx(
        side.get_wrist_orientation().as_quat()
    )


def test_symbol_id_and_hand_side() -> None:
    right = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=0)
    left = BaseSymbol01_05_001_FiveFingersSpread(fill=1, rotation=10)

    assert right.symbol_id == "01-05-001"
    assert right.hand_side == HandSide.RIGHT
    assert left.hand_side == HandSide.LEFT


def test_symbol_from_fsw_builds_five_fingers_spread() -> None:
    # 0x14c = group 5, base_symbol_number 1 ("Five Fingers Spread").
    symbol = symbol_from_fsw("S14c12")
    assert isinstance(symbol, BaseSymbol01_05_001_FiveFingersSpread)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == "01-05-001"
