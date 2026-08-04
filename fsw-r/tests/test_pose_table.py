from __future__ import annotations

from fsw_r.core.pose_table import HAND_NAME_TABLE, HAND_POSE_TABLE
from fsw_r.core.types import FingerPose, ThumbPose

_FLEXION_RANGE = (0.0, 180.0)  # a joint can't hyperextend/flex past a straight line and back


def test_pose_table_has_exactly_261_entries() -> None:
    assert len(HAND_POSE_TABLE) == 261
    assert len(HAND_NAME_TABLE) == 261


def test_pose_table_and_name_table_share_the_same_symbol_ids() -> None:
    assert set(HAND_POSE_TABLE.keys()) == set(HAND_NAME_TABLE.keys())


def test_every_symbol_id_is_well_formed() -> None:
    for symbol_id in HAND_POSE_TABLE:
        category, group, base_symbol_number = symbol_id.split("-")
        assert category == "01"
        assert 1 <= int(group) <= 10
        assert 1 <= int(base_symbol_number) <= 58


def test_every_name_is_a_non_empty_string() -> None:
    for symbol_id, name in HAND_NAME_TABLE.items():
        assert isinstance(name, str) and name, f"{symbol_id} has no real name"


def _finger_angles(finger: FingerPose) -> tuple[float, float, float]:
    return (finger.mcp.flexion, finger.pip.flexion, finger.dip.flexion)


def _thumb_angles(thumb: ThumbPose) -> tuple[float, float, float]:
    return (thumb.cmc.flexion, thumb.mcp.flexion, thumb.ip.flexion)


def test_every_flexion_angle_is_within_physical_range() -> None:
    for symbol_id, pose in HAND_POSE_TABLE.items():
        angles = (
            *_thumb_angles(pose.thumb),
            *_finger_angles(pose.index),
            *_finger_angles(pose.middle),
            *_finger_angles(pose.ring),
            *_finger_angles(pose.pinky),
        )
        for angle in angles:
            assert _FLEXION_RANGE[0] <= angle <= _FLEXION_RANGE[1], f"{symbol_id}: flexion {angle} out of range"


def test_index_pose_matches_the_real_measured_values() -> None:
    # Spot check against the dataset-derived values documented throughout
    # PROGRESS.md/ROADMAP.md, to catch silent data corruption in the JSON.
    pose = HAND_POSE_TABLE["01-01-001"]
    assert pose.index.mcp.flexion == 30
    assert pose.index.pip.flexion == 3
    assert pose.index.dip.flexion == 8
    assert HAND_NAME_TABLE["01-01-001"] == "Index"


def test_index_bent_has_its_own_measured_pose_not_borrowed_from_index() -> None:
    index = HAND_POSE_TABLE["01-01-001"]
    index_bent = HAND_POSE_TABLE["01-01-007"]

    assert index_bent.index.pip.flexion == 46
    # Unlike an earlier version of this codebase, "Index Bent" is not just
    # "Index" with the index finger overridden -- every finger was measured
    # independently for this symbol (see PROGRESS.md).
    assert index_bent.thumb != index.thumb
    assert index_bent.middle != index.middle
    assert index_bent.ring != index.ring
    assert index_bent.pinky != index.pinky
