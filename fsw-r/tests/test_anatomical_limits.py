from __future__ import annotations

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.validation.anatomical_limits import ESTIMATED_LIMITS, JOINT_LIMITS, validate_pose

_FLAT = JointAngle(flexion=0.0, abduction=0.0)
_FLAT_FINGER = FingerPose(mcp=_FLAT, pip=_FLAT, dip=_FLAT)
_VALID_POSE = HandJointPose(
    thumb=ThumbPose(cmc=_FLAT, mcp=_FLAT, ip=_FLAT),
    index=_FLAT_FINGER,
    middle=_FLAT_FINGER,
    ring=_FLAT_FINGER,
    pinky=_FLAT_FINGER,
)


def test_valid_pose_has_no_violations() -> None:
    assert validate_pose(_VALID_POSE) == []


def test_pip_beyond_limit_is_flagged() -> None:
    bad_index = FingerPose(mcp=_FLAT, pip=JointAngle(flexion=167.0), dip=_FLAT)
    pose = HandJointPose(
        thumb=ThumbPose(cmc=_FLAT, mcp=_FLAT, ip=_FLAT),
        index=bad_index,
        middle=_FLAT_FINGER,
        ring=_FLAT_FINGER,
        pinky=_FLAT_FINGER,
    )
    violations = validate_pose(pose)
    assert len(violations) == 1
    v = violations[0]
    assert v.finger == "index"
    assert v.joint == "pip"
    assert v.angle_type == "flexion"
    assert v.value == 167.0


def test_exact_boundary_is_not_a_violation() -> None:
    # JointAngle's own convention: 0 = fully extended. The upper bound
    # itself must be valid (a limit is "up to and including", not "up to
    # but excluding").
    low, high = JOINT_LIMITS[("finger_pip", "flexion")]
    boundary_finger = FingerPose(mcp=_FLAT, pip=JointAngle(flexion=high), dip=_FLAT)
    pose = HandJointPose(
        thumb=ThumbPose(cmc=_FLAT, mcp=_FLAT, ip=_FLAT),
        index=boundary_finger,
        middle=_FLAT_FINGER,
        ring=_FLAT_FINGER,
        pinky=_FLAT_FINGER,
    )
    assert validate_pose(pose) == []


def test_multiple_violations_are_all_reported() -> None:
    bad_finger = FingerPose(mcp=JointAngle(flexion=999.0), pip=JointAngle(flexion=999.0), dip=_FLAT)
    pose = HandJointPose(
        thumb=ThumbPose(cmc=_FLAT, mcp=_FLAT, ip=_FLAT),
        index=bad_finger,
        middle=_FLAT_FINGER,
        ring=_FLAT_FINGER,
        pinky=_FLAT_FINGER,
    )
    violations = validate_pose(pose)
    assert len(violations) == 2
    assert {v.joint for v in violations} == {"mcp", "pip"}


def test_thumb_joints_use_thumb_specific_limits() -> None:
    bad_thumb = ThumbPose(cmc=JointAngle(flexion=999.0), mcp=_FLAT, ip=_FLAT)
    pose = HandJointPose(
        thumb=bad_thumb, index=_FLAT_FINGER, middle=_FLAT_FINGER, ring=_FLAT_FINGER, pinky=_FLAT_FINGER
    )
    violations = validate_pose(pose)
    assert len(violations) == 1
    assert violations[0].finger == "thumb"
    assert violations[0].joint == "cmc"
    assert violations[0].limit == JOINT_LIMITS[("thumb_cmc", "flexion")]


def test_abduction_beyond_limit_is_flagged_separately_from_flexion() -> None:
    bad_index = FingerPose(mcp=JointAngle(flexion=0.0, abduction=999.0), pip=_FLAT, dip=_FLAT)
    pose = HandJointPose(
        thumb=ThumbPose(cmc=_FLAT, mcp=_FLAT, ip=_FLAT),
        index=bad_index,
        middle=_FLAT_FINGER,
        ring=_FLAT_FINGER,
        pinky=_FLAT_FINGER,
    )
    violations = validate_pose(pose)
    assert len(violations) == 1
    assert violations[0].angle_type == "abduction"


def test_every_estimated_limit_key_is_a_real_joint_limits_entry() -> None:
    # Consistency check: ESTIMATED_LIMITS must only reference keys that
    # actually exist in JOINT_LIMITS, so the "which limits are estimated"
    # disclosure in reports can never silently go stale.
    assert ESTIMATED_LIMITS <= set(JOINT_LIMITS)
