"""D1-D6 (this task's brief, "Chuyển động khớp ngón tay", Part D). D7
(``reports/fk_accuracy.md`` unchanged) and D8 (1,441 old tests pass) are
process-level checks, not tests in this file -- see PROGRESS.md's entry
for this task for how those were verified.
"""

from __future__ import annotations

import numpy as np
import pytest

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.core.iswa_data import GROUP_START, valid_combinations_for
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.core.types import FingerArticulation, HandJointPose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import TrackName
from fsw_r.validation.anatomical_limits import JOINT_LIMITS

# Global group 12 (GROUP_START index 11) -- Finger Movement, 0x216-0x229.
GROUP_12_BASE_HEXES = list(range(GROUP_START[11], GROUP_START[12]))

# The 5 base symbols covering 76.1% of real Group 12 token usage (this
# task's own Part A measurement table) -- real ISWA names looked up on
# signbank.org before writing any of this (Part A1), see
# scripts/gen_finger_articulations.py's _RESEARCHED table and
# PROGRESS.md's entry for this task.
TOP_5_GROUP_12_BASES = [0x221, 0x225, 0x216, 0x21B, 0x222]

# Index handshape (0x100) + a Group 12 base at fill=0, rotation=0 (valid
# for all 5 researched bases -- see test_movement_symbol.py's own
# TOP_20_MOST_FREQUENT_BASES, independently confirming 0x221's [0-4]
# fills/8 rotations, and this task's own Part A table for the other 4).
def _finger_movement_sign(base_hex: int) -> str:
    return f"M500x500S10010480x480S{base_hex:03x}00500x500"


# A moving sign that does NOT use Group 12 -- Straight Wall Plane (0x22a),
# same sign used throughout this project's existing test suite.
_NON_FINGER_MOVING_SIGN = "M500x500S10010480x480S22a10500x500"


def _all_flexion_angles(joint_pose: HandJointPose) -> list[tuple[str, str, float]]:
    """(finger, joint, flexion) for every joint in a HandJointPose --
    local helper, not importing anything private."""
    result = []
    for finger_name in ("index", "middle", "ring", "pinky"):
        finger_pose = getattr(joint_pose, finger_name)
        for joint_name in ("mcp", "pip", "dip"):
            result.append((finger_name, joint_name, getattr(finger_pose, joint_name).flexion))
    thumb = joint_pose.thumb
    for joint_name in ("cmc", "mcp", "ip"):
        result.append(("thumb", joint_name, getattr(thumb, joint_name).flexion))
    return result


def test_d1_joint_pose_varies_across_frames_for_a_group_12_sign() -> None:
    fsw = _finger_movement_sign(0x221)
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)

    first = frames[0].tracks[TrackName.RIGHT_HAND].joint_pose
    middle = frames[len(frames) // 2].tracks[TrackName.RIGHT_HAND].joint_pose
    last = frames[-1].tracks[TrackName.RIGHT_HAND].joint_pose

    assert first != middle
    assert middle != last
    assert first != last


def test_d2_joint_pose_stays_constant_for_a_non_group_12_sign() -> None:
    # No regression: a moving sign WITHOUT a Group 12 symbol must keep
    # exactly the old behavior (same joint_pose baked into every keyframe).
    positioned = fsw_to_fswr(_NON_FINGER_MOVING_SIGN)
    timeline = build_timeline(positioned)
    frames = sample(timeline)

    poses = [f.tracks[TrackName.RIGHT_HAND].joint_pose for f in frames]
    assert all(p == poses[0] for p in poses)


def test_d3_wrist_position_stays_still_for_a_group_12_sign() -> None:
    fsw = _finger_movement_sign(0x221)
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)

    positions = [f.tracks[TrackName.RIGHT_HAND].position for f in frames]
    first_position = positions[0]
    assert first_position is not None
    for position in positions:
        assert position is not None
        assert np.array_equal(position, first_position)


@pytest.mark.parametrize("base_hex", TOP_5_GROUP_12_BASES)
def test_d4_oscillated_angles_stay_within_anatomical_limits(base_hex: int) -> None:
    # Only checks the (finger, joint) pairs this symbol's OWN
    # FingerArticulation actually oscillates -- a joint this task never
    # touches can already sit outside JOINT_LIMITS in the pre-existing
    # static hand_joint_poses.json data (Pha 6's own documented finding:
    # 224/261 base symbols violate at least one limit there), and this
    # task's brief explicitly does not touch that data or "fix" it -- only
    # the clamp on joints THIS task's oscillation actually modifies is in
    # scope here.
    combos = valid_combinations_for(base_hex)
    symbol = MovementSymbol(base_hex=base_hex, fill=min(combos.fills), rotation=min(combos.rotations))
    articulation = symbol.get_finger_articulation()
    assert articulation is not None

    fsw = _finger_movement_sign(base_hex)
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)

    checked_any = False
    for frame in frames:
        joint_pose = frame.tracks[TrackName.RIGHT_HAND].joint_pose
        assert joint_pose is not None
        for finger, joint, value in _all_flexion_angles(joint_pose):
            if finger not in articulation.fingers or joint not in articulation.joints:
                continue
            checked_any = True
            key = "thumb_" + joint if finger == "thumb" else "finger_" + joint
            limit = JOINT_LIMITS.get((key, "flexion"))
            if limit is None:
                continue
            low, high = limit
            assert low - 1e-6 <= value <= high + 1e-6, f"{finger}.{joint}={value} outside [{low}, {high}]"
    assert checked_any, f"base 0x{base_hex:x}: no oscillated joint was actually checked -- test is vacuous"


@pytest.mark.parametrize("base_hex", GROUP_12_BASE_HEXES)
def test_d5_every_group_12_base_constructs_and_gets_an_articulation(base_hex: int) -> None:
    combos = valid_combinations_for(base_hex)
    symbol = MovementSymbol(base_hex=base_hex, fill=min(combos.fills), rotation=min(combos.rotations))
    articulation = symbol.get_finger_articulation()
    assert isinstance(articulation, FingerArticulation)
    assert len(articulation.fingers) > 0
    assert len(articulation.joints) > 0


def test_d5_non_group_12_movement_symbol_has_no_articulation() -> None:
    # 0x22a (Straight Wall Plane) is Category 2 but NOT Group 12.
    combos = valid_combinations_for(0x22A)
    symbol = MovementSymbol(base_hex=0x22A, fill=min(combos.fills), rotation=min(combos.rotations))
    assert symbol.get_finger_articulation() is None


@pytest.mark.parametrize("base_hex", TOP_5_GROUP_12_BASES)
def test_d6_amplitude_is_visibly_large_for_the_top_5_bases(base_hex: int) -> None:
    # This task's brief, Part D6: the largest flexion difference between
    # any two frames must be >= 15 degrees for the 5 leading bases -- the
    # whole point of this task (visible finger movement, not a static
    # hand sliding along a path).
    fsw = _finger_movement_sign(base_hex)
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)

    all_values: list[list[float]] = []
    for frame in frames:
        joint_pose = frame.tracks[TrackName.RIGHT_HAND].joint_pose
        assert joint_pose is not None
        all_values.append([value for _finger, _joint, value in _all_flexion_angles(joint_pose)])

    array = np.array(all_values)  # frames x joints
    max_diff = float((array.max(axis=0) - array.min(axis=0)).max())
    assert max_diff >= 15.0, f"base 0x{base_hex:x}: max angle difference across frames is only {max_diff:.1f} deg"
