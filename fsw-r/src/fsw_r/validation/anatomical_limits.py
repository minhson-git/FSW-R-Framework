"""Real anatomical joint-limit reference values, and ``validate_pose()``,
which checks a ``HandJointPose`` against them. Answers this evaluation
task's Câu 2 (Part 0): how much of Category 1's 261 hand poses violate real
anatomical limits, quantified precisely instead of the "136/261, 52.1%"
estimate a prior task's brief cited (see PROGRESS.md's Phase 3 entry, which
already flagged that number as not independently reproducible).

**Sources, cited per joint, not blanket-attributed** (a mix of firm
clinical reference values and explicitly-flagged plausibility estimates --
same honesty standard as ``export/bone_lengths.py``):

- Finger (index/middle/ring/pinky) MCP/PIP/DIP flexion: American Academy
  of Orthopaedic Surgeons (AAOS) normal range-of-motion reference values
  (as commonly compiled/cited in clinical goniometry references, e.g.
  goniometer.io's printable AAOS chart) -- MCP 90 deg, PIP 100-120 deg
  across sources, DIP 70-90 deg across sources. This module uses the upper
  end of each reported range as the PLAUSIBILITY ceiling (not the
  "typical" single AAOS number) -- the question here is "is this
  physically possible," not "is this an average hand," so the more
  generous bound is the correct one to flag violations against.
- Thumb CMC: AAOS-cited radial/palmar abduction up to 60-70 deg; flexion
  commonly reported 15-26 deg across clinical ROM studies (mean ~20-25
  deg). Ceiling set generously above the reported range.
- Thumb MCP flexion: AAOS typical ~50 deg, but individual variation
  reported as high as ~126 deg in some studies -- ESTIMATED ceiling here
  (90 deg), deliberately more conservative than that extreme outlier,
  flagged as an estimate, not a firm citation, since no single source
  gives a clean population ceiling.
- Thumb IP flexion: AAOS ~80 deg, small buffer applied.
- MCP/CMC ABDUCTION for individual fingers (finger spread): NOT found in
  the AAOS chart or the clinical ROM literature searched for this task --
  ESTIMATED, flagged explicitly (see FINGER_ABDUCTION_LIMIT_IS_ESTIMATED).
- Hyperextension (negative flexion): no citation found for a clean
  per-joint limit; minimum is set to 0 deg (JointAngle's own documented
  "0 = fully extended" convention) for every joint. This likely
  UNDER-counts real hyperextension violations in the other direction (mild
  hyperextension, e.g. -10 to -30 deg at MCP, is normal in many people) --
  flagged as an acknowledged gap, not silently assumed to be zero
  violations.
"""

from __future__ import annotations

from dataclasses import dataclass

from fsw_r.core.types import HandJointPose

# (joint_name, angle_type) -> (min_degrees, max_degrees). joint_name is
# shared across the 4 non-thumb fingers (index/middle/ring/pinky) -- the
# cited literature does not distinguish limits between them.
JOINT_LIMITS: dict[tuple[str, str], tuple[float, float]] = {
    ("finger_mcp", "flexion"): (0.0, 100.0),  # AAOS 90, generous ceiling
    ("finger_pip", "flexion"): (0.0, 120.0),  # AAOS 100, upper end of range across sources
    ("finger_dip", "flexion"): (0.0, 90.0),  # AAOS 80, upper end of range across sources
    ("thumb_cmc", "flexion"): (0.0, 30.0),  # clinical ROM studies report 15-26 deg mean
    ("thumb_mcp", "flexion"): (0.0, 90.0),  # AAOS 50 typical; ESTIMATED ceiling, see module docstring
    ("thumb_ip", "flexion"): (0.0, 90.0),  # AAOS ~80, small buffer
    ("finger_mcp", "abduction"): (-20.0, 20.0),  # ESTIMATED -- see module docstring
    ("thumb_cmc", "abduction"): (0.0, 70.0),  # AAOS radial/palmar abduction up to 60-70
}

# Which of JOINT_LIMITS' entries are genuinely estimated (no firm clinical
# citation), for the report to flag honestly rather than presenting every
# limit as equally well-sourced.
ESTIMATED_LIMITS: frozenset[tuple[str, str]] = frozenset(
    {
        ("thumb_mcp", "flexion"),
        ("finger_mcp", "abduction"),
    }
)


@dataclass(frozen=True)
class Violation:
    finger: str
    joint: str  # "mcp"/"pip"/"dip"/"cmc"/"ip", the field name on FingerPose/ThumbPose
    angle_type: str  # "flexion" or "abduction"
    value: float
    limit: tuple[float, float]


def _joint_key(finger: str, joint: str) -> str:
    return "thumb_" + joint if finger == "thumb" else "finger_" + joint


def _check(finger: str, joint: str, angle_type: str, value: float) -> Violation | None:
    key = _joint_key(finger, joint)
    limit = JOINT_LIMITS.get((key, angle_type))
    if limit is None:
        return None
    low, high = limit
    if value < low or value > high:
        return Violation(finger=finger, joint=joint, angle_type=angle_type, value=value, limit=limit)
    return None


def validate_pose(pose: HandJointPose) -> list[Violation]:
    """Every joint angle in ``pose`` that falls outside ``JOINT_LIMITS``,
    checking both flexion and abduction where a limit is defined for that
    (joint, angle_type) pair. Empty list = no violations."""
    violations: list[Violation] = []

    for finger_name, finger_pose in (
        ("index", pose.index),
        ("middle", pose.middle),
        ("ring", pose.ring),
        ("pinky", pose.pinky),
    ):
        for joint_name, angle in (
            ("mcp", finger_pose.mcp),
            ("pip", finger_pose.pip),
            ("dip", finger_pose.dip),
        ):
            for angle_type, value in (("flexion", angle.flexion), ("abduction", angle.abduction)):
                v = _check(finger_name, joint_name, angle_type, value)
                if v is not None:
                    violations.append(v)

    for joint_name, angle in (
        ("cmc", pose.thumb.cmc),
        ("mcp", pose.thumb.mcp),
        ("ip", pose.thumb.ip),
    ):
        for angle_type, value in (("flexion", angle.flexion), ("abduction", angle.abduction)):
            v = _check("thumb", joint_name, angle_type, value)
            if v is not None:
                violations.append(v)

    return violations


# 4 fingers x 3 joints x 1 flexion angle checked with a real limit (MCP/PIP/
# DIP all have flexion limits) + thumb's 3 joints x 1 flexion = 15 flexion
# checks per pose -- matches this task's brief citing "3,915 góc" for 261
# symbols (261 x 15 = 3,915). Abduction is checked too (see validate_pose)
# but reported separately (see eval_anatomical.py) since hand_joint_poses.json's
# own abduction values are already documented elsewhere as un-measured
# estimates (see PROGRESS.md), making abduction violations a different,
# weaker signal than flexion violations.
FLEXION_CHECKS_PER_POSE = 15
