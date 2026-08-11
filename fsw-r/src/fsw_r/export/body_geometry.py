"""A static, neutral torso/head pose, plus the two arm segment lengths
two-bone IK (``arm_ik.py``) needs -- the geometry that goes AROUND the hand
this project already renders, so a video shows a signer, not a hand
floating in space (see this task's brief, Part 0's diagnosis: 21/576
points filled, no body to anchor the hand to).

**Cited source for the 4 proportions that matter for arm reach**
(shoulder width, hip width, upper-arm length, forearm length): Drillis, R.,
& Contini, R. (1966), "Body Segment Parameters" -- fetched directly from
its reproduction in Winter, D.A., *Biomechanics and Motor Control of Human
Movement*, 4th ed., Figure 4.1 (the real page, not paraphrased), which
gives segment length as a fraction of body height ``H``:

    shoulder width (biacromial)      = 0.259 H
    hip width                        = 0.191 H
    upper arm (shoulder -> elbow)    = 0.186 H
    forearm (elbow -> wrist)         = 0.146 H
    hand (wrist -> fingertip)        = 0.108 H   -- cross-check only, see below

``H`` (assumed adult stature) is NOT from that source -- ``ASSUMED_STATURE_MM``
below is a commonly-cited round approximate adult height, not a specific
population statistic. Flagged as an assumption, same as
``bone_lengths.py``'s ``HAND_MM_TO_BODY_UNITS``.

**Cross-check, not reconciled**: 0.108 H = 183.6 mm at the assumed stature,
vs. this project's own FK-derived middle-finger chain length (metacarpal +
3 phalanges, ``bone_lengths.py``) = 151.1 mm -- an ~18% difference, most
likely because ``bone_lengths.py``'s metacarpal length is itself a derived
estimate (flagged "WEAKER" there), not because this module's ratio is
wrong. This task's brief explicitly puts hand-geometry recalibration out of
scope (Part 0) -- noted here, not fixed.

**NOT from Drillis-Contini, individually flagged as ESTIMATED:**
- ``TORSO_LENGTH_MM`` (shoulder-to-hip vertical) -- the source figure's own
  vertical landmark labels could not be read unambiguously from the
  fetched page (only the horizontal segment brackets this module actually
  needs were legible), so this is a separate, simpler estimate, not
  mis-attributed to the cited source.
- Head landmark offsets (nose/ear/mouth relative to a neck/head anchor).
- The shoulder line's vertical anchor in body-space -- see
  ``SHOULDER_CENTER_BODY_SPACE``'s own comment for the reasoning (not
  arbitrary, but not a citation either).
- Elbow pole vector direction (``arm_ik.py``'s own module, not here) --
  "a real elbow points back and down" is this task brief's own instruction,
  not sourced from an anthropometric table.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from fsw_r.export.bone_lengths import HAND_MM_TO_BODY_UNITS

# Commonly-cited round approximate adult stature -- NOT a specific
# population statistic, just the scale Drillis-Contini's fractions are
# applied to. See module docstring.
ASSUMED_STATURE_MM = 1700.0

SHOULDER_WIDTH_MM = 0.259 * ASSUMED_STATURE_MM
HIP_WIDTH_MM = 0.191 * ASSUMED_STATURE_MM
UPPER_ARM_LENGTH_MM = 0.186 * ASSUMED_STATURE_MM  # shoulder -> elbow, IK's L1
FOREARM_LENGTH_MM = 0.146 * ASSUMED_STATURE_MM  # elbow -> wrist, IK's L2

# ESTIMATED -- see module docstring's "NOT from Drillis-Contini" note.
TORSO_LENGTH_MM = 0.30 * ASSUMED_STATURE_MM  # shoulder-to-hip vertical
NECK_TO_HEAD_CENTER_MM = 0.5 * 0.130 * ASSUMED_STATURE_MM  # half of Drillis-Contini's own head-height fraction, as a neck+head-center proxy
NOSE_FORWARD_OFFSET_MM = 60.0  # small forward (toward viewer) offset so the nose isn't coincident with ear/mouth depth
EAR_SIDE_OFFSET_MM = 80.0
MOUTH_DROP_MM = 40.0  # below the head center used for the nose

# All the above, converted once into fsw_r.timeline's body-space units --
# the SAME conversion bone_lengths.py's hand geometry already uses, so the
# body and the hand share one consistent scale (otherwise the hand would
# render too large/small relative to the arm it's attached to).
UPPER_ARM_LENGTH = UPPER_ARM_LENGTH_MM * HAND_MM_TO_BODY_UNITS
FOREARM_LENGTH = FOREARM_LENGTH_MM * HAND_MM_TO_BODY_UNITS
_SHOULDER_WIDTH = SHOULDER_WIDTH_MM * HAND_MM_TO_BODY_UNITS
_HIP_WIDTH = HIP_WIDTH_MM * HAND_MM_TO_BODY_UNITS
_TORSO_LENGTH = TORSO_LENGTH_MM * HAND_MM_TO_BODY_UNITS
_NECK_TO_HEAD_CENTER = NECK_TO_HEAD_CENTER_MM * HAND_MM_TO_BODY_UNITS
_NOSE_FORWARD = NOSE_FORWARD_OFFSET_MM * HAND_MM_TO_BODY_UNITS
_EAR_SIDE = EAR_SIDE_OFFSET_MM * HAND_MM_TO_BODY_UNITS
_MOUTH_DROP = MOUTH_DROP_MM * HAND_MM_TO_BODY_UNITS

# ESTIMATED: where the shoulder line sits in fsw_r.timeline's body space.
# Not arbitrary -- timeline/anchor.py's own y=0 (signbox y=500) was
# calibrated against real corpus medians where HEAD (483) and HAND (496)
# symbols land almost on top of each other, i.e. y=0 is already close to
# head/shoulder height for a real sign (hands are typically signed near
# chest/shoulder level). Placing the shoulder line AT y=0 reuses that
# existing calibration rather than inventing a second, uncoordinated one --
# but it is still a design choice, not a measurement, hence ESTIMATED.
SHOULDER_CENTER_BODY_SPACE: NDArray[np.float64] = np.array([0.0, 0.0, 0.0])


# MediaPipe's own real, documented convention: LEFT_*/RIGHT_* landmark
# names are the SUBJECT's own anatomical left/right, which appear MIRRORED
# to the viewer/camera when the subject faces it (a selfie/mirror view --
# the subject's right hand shows on the screen's left side). This
# project's pixel mapping (_body_to_pixel in pose_export.py) has body-space
# +x -> LARGER pixel x (further right on screen), so the subject's RIGHT
# side must be placed at NEGATIVE body-space x to match that convention --
# matching it matters because interoperability with the wider pose-format
# ecosystem (the whole reason this project chose the format, see
# PROGRESS.md) depends on following the SAME left/right convention real
# .pose files use, not an internally-consistent-but-different one.
def shoulder_position(is_right: bool) -> NDArray[np.float64]:
    sign = -1.0 if is_right else 1.0
    result: NDArray[np.float64] = SHOULDER_CENTER_BODY_SPACE + np.array([sign * _SHOULDER_WIDTH / 2, 0.0, 0.0])
    return result


def hip_position(is_right: bool) -> NDArray[np.float64]:
    sign = -1.0 if is_right else 1.0
    result: NDArray[np.float64] = SHOULDER_CENTER_BODY_SPACE + np.array([sign * _HIP_WIDTH / 2, -_TORSO_LENGTH, 0.0])
    return result


def static_head_landmarks() -> dict[str, NDArray[np.float64]]:
    """NOSE/LEFT_EAR/RIGHT_EAR/MOUTH_LEFT/MOUTH_RIGHT -- POSE_LANDMARKS
    indices 0, 7, 8, 9, 10 per this task's brief Part B1 (eyes, indices
    1-6, deliberately left out -- not listed in the brief's own table)."""
    head_center = SHOULDER_CENTER_BODY_SPACE + np.array([0.0, _NECK_TO_HEAD_CENTER, 0.0])
    return {
        "NOSE": head_center + np.array([0.0, 0.0, _NOSE_FORWARD]),
        "LEFT_EAR": head_center + np.array([_EAR_SIDE, 0.0, 0.0]),
        "RIGHT_EAR": head_center + np.array([-_EAR_SIDE, 0.0, 0.0]),
        "MOUTH_LEFT": head_center + np.array([_EAR_SIDE / 3, -_MOUTH_DROP, _NOSE_FORWARD / 2]),
        "MOUTH_RIGHT": head_center + np.array([-_EAR_SIDE / 3, -_MOUTH_DROP, _NOSE_FORWARD / 2]),
    }
