"""Scale-invariance guards for the hand<->body anthropometric ratios
(this task's Part B). The hand geometry (``bone_lengths.py`` +
``forward_kinematics.py``) and the body geometry (``body_geometry.py``) now
BOTH derive from one assumed stature (``anthropometry.ASSUMED_STATURE_MM``);
these tests pin the three ratios that would silently regress if a future
edit re-anchored one of the two to a different height, plus left/right
symmetry.

The ranges are acceptance WINDOWS, not exact values: wide enough that small
future tuning of ``HAND_LENGTH_TO_STATURE`` (or the body fractions) does not
break them, tight enough to catch the ~1.5x hand-too-small regression this
task fixed (measured before: palm/shoulder ~= 0.15; anthropometric ~= 0.24).
See PROGRESS.md's before/after table and ``bone_lengths.py``'s docstring for
why the current values sit where they do (near B1's floor -- a documented
symptom of this hand's ~0.43 palm proportion, out of scope to change).
"""

from __future__ import annotations

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from fsw_r.core.types import FingerPose, HandJointPose, HandSide, JointAngle, ThumbPose
from fsw_r.export.anthropometry import ASSUMED_STATURE_MM, HAND_MM_TO_BODY_UNITS
from fsw_r.export.body_geometry import FOREARM_LENGTH_MM, SHOULDER_WIDTH_MM
from fsw_r.export.forward_kinematics import hand_to_landmarks


def _uniform_pose(flexion: float) -> HandJointPose:
    """Every joint at the same flexion, no abduction. ``flexion=0`` is the
    flat, fully-extended hand the length ratios are defined against."""
    angle = JointAngle(flexion=flexion, abduction=0.0)
    finger = FingerPose(mcp=angle, pip=angle, dip=angle)
    return HandJointPose(
        thumb=ThumbPose(cmc=JointAngle(0.0, 0.0), mcp=angle, ip=angle),
        index=finger,
        middle=finger,
        ring=finger,
        pinky=finger,
    )


_EXTENDED = _uniform_pose(0.0)


def _landmarks(pose: HandJointPose, side: HandSide) -> dict[str, NDArray[np.float64]]:
    return hand_to_landmarks(pose, Rotation.identity(), np.zeros(3), side)


def _palm_length_mm(pose: HandJointPose, side: HandSide) -> float:
    """Wrist -> middle-finger MCP distance, in real millimetres.

    B4: this deliberately measures to ``MIDDLE_FINGER_MCP``, NOT
    ``MIDDLE_FINGER_TIP``. The MCP (the knuckle where the metacarpal meets
    the proximal phalanx) is the end of the fixed palm skeleton, so its
    distance from the wrist is invariant to how the FINGERS are flexed --
    it measures anatomy. The TIP, in contrast, swings toward the wrist as
    the finger curls, so a palm measured to the TIP would shrink with
    flexion and this test would be pinning the POSE, not the hand's build.
    ``test_b4_palm_length_is_invariant_to_finger_flexion`` proves this.
    """
    landmarks = _landmarks(pose, side)
    palm_body_units = float(np.linalg.norm(landmarks["MIDDLE_FINGER_MCP"] - landmarks["WRIST"]))
    return palm_body_units / HAND_MM_TO_BODY_UNITS


def _extended_hand_length_mm(side: HandSide) -> float:
    """Wrist -> middle-finger TIP distance for the fully EXTENDED hand
    (flexion=0), in millimetres -- the classic anthropometric "hand length".
    TIP is correct HERE (unlike the palm measure) precisely because the hand
    is extended: with flexion=0 the middle finger points straight out, so
    wrist->TIP is the true maximal hand length, not a pose artifact."""
    landmarks = _landmarks(_EXTENDED, side)
    hand_body_units = float(np.linalg.norm(landmarks["MIDDLE_FINGER_TIP"] - landmarks["WRIST"]))
    return hand_body_units / HAND_MM_TO_BODY_UNITS


def test_b1_palm_to_shoulder_width_ratio_in_window() -> None:
    ratio = _palm_length_mm(_EXTENDED, HandSide.RIGHT) / SHOULDER_WIDTH_MM
    assert 0.20 <= ratio <= 0.28, f"palm/shoulder = {ratio:.4f} outside [0.20, 0.28]"


def test_b2_palm_to_forearm_length_ratio_in_window() -> None:
    ratio = _palm_length_mm(_EXTENDED, HandSide.RIGHT) / FOREARM_LENGTH_MM
    assert 0.33 <= ratio <= 0.43, f"palm/forearm = {ratio:.4f} outside [0.33, 0.43]"


def test_b3_extended_hand_length_to_stature_ratio_in_window() -> None:
    ratio = _extended_hand_length_mm(HandSide.RIGHT) / ASSUMED_STATURE_MM
    assert 0.10 <= ratio <= 0.12, f"hand-length/stature = {ratio:.4f} outside [0.10, 0.12]"


def test_b4_palm_length_is_invariant_to_finger_flexion() -> None:
    """The justification for measuring the palm to the MCP, not the TIP (see
    ``_palm_length_mm``): flexing every finger to a fist must NOT change the
    wrist->MCP palm length. If this ever fails, the palm measure has picked
    up a joint that moves with the fingers and B1/B2 would be measuring pose,
    not anatomy."""
    extended_palm = _palm_length_mm(_EXTENDED, HandSide.RIGHT)
    fist_palm = _palm_length_mm(_uniform_pose(80.0), HandSide.RIGHT)
    assert extended_palm == pytest.approx(fist_palm, abs=1e-9)


def test_b5_left_and_right_hands_share_the_same_scale() -> None:
    """Symmetry: the mirroring that builds the left hand must not change any
    length. Left and right must give the same palm/shoulder ratio (a pure
    x-axis flip preserves distances)."""
    right = _palm_length_mm(_EXTENDED, HandSide.RIGHT) / SHOULDER_WIDTH_MM
    left = _palm_length_mm(_EXTENDED, HandSide.LEFT) / SHOULDER_WIDTH_MM
    assert right == pytest.approx(left, rel=1e-12)
