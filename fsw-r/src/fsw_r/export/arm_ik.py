"""Two-bone IK, solved in closed form (law of cosines + a single known-angle
combination of two orthonormal directions) -- deliberately NOT a general
iterative solver (CCD, FABRIK, ``scipy.optimize``, ...), per this task's
brief: a closed-form two-bone solution cannot produce a hyperextended/
backward-bending elbow, the single biggest cause of "deformed-looking
person" artifacts a general solver can produce.

**Algorithm** (shoulder and wrist positions known, elbow position solved
for): law of cosines gives the angle at the shoulder between the
shoulder->wrist direction (``aim``) and the shoulder->elbow direction; the
pole vector picks WHICH of the two directions perpendicular to
shoulder->wrist (a full circle of otherwise-valid elbow positions) is
used, i.e. which way the elbow bends. The elbow direction is built
DIRECTLY as ``cos(angle) * aim + sin(angle) * bend_direction`` -- since
``aim``/``bend_direction`` are already orthonormal (``_bend_direction``
constructs it that way), this is guaranteed to have unit length and to
lean toward ``bend_direction`` for any ``angle`` in ``[0, pi]``, with no
dependency on a rotation library's own sign/handedness convention.

**"Khung hình dễ đọc hơn + fix hướng xoay IK" task -- corrected diagnosis,
recorded honestly:** that task's brief hypothesized the previous
``Rotation.from_rotvec(axis * angle).apply(aim)`` step (``axis =
cross(aim, bend_direction)``) had a SIGN bug, i.e. rotated away from
``bend_direction`` instead of toward it, and suggested this exact
``cos``/``sin`` formula as the fix. **Verified, not assumed, before
changing anything:** algebraically (Rodrigues' rotation formula) and
numerically (5 random orthonormal ``aim``/``bend_direction`` pairs, see
this task's own investigation notes in PROGRESS.md) that
``Rotation.from_rotvec(cross(aim, bend) * angle).apply(aim)`` was ALREADY
bit-identical to ``cos(angle) * aim + sin(angle) * bend`` -- rotating by
``+angle`` around ``cross(aim, bend_direction)`` always leans toward
``bend_direction``, for any orthonormal pair. **There was no rotation-sign
bug.** Switched to the direct formula anyway (drops the ``scipy``
``Rotation`` dependency for this function, and removes any doubt about
rotation-library conventions for a future reader), but this alone changes
NOTHING numerically -- confirmed by comparing elbow output before/after
the swap, bit-identical.

**"Sửa bug hướng xoay IK + chỉnh khung hình demo" task's own diagnosis --
LATER FOUND TO BE WRONG, recorded honestly (see the follow-up task
below):** that task measured the elbow swinging far below BOTH the
shoulder and the wrist for near-horizontal, medial-reaching ``aim``
directions, and concluded the pole's downward component was the bug --
recalibrating ``POLE_DIRECTION_RIGHT``/``LEFT`` to have a downward (``y``)
component of exactly 0. **This "fix" was itself built on a wrong
invariant** (see the next section) -- a real elbow buoyed at zero downward
droop, never sagging below shoulder-height even when reaching across the
body, is NOT anatomically correct either; it produced a flat, nearly
horizontal-looking arm instead of a natural V.

**"Sửa lại bất biến IK sai (hồi quy từ Pha 10)" task -- the actual root
cause.** The regression traced back one level further: the elbow-position
TEST the previous task added
(``tests/test_arm_configuration.py``'s C1) asserted the elbow stays
BETWEEN the shoulder and the wrist on BOTH sides --
``min(shoulder.y, wrist.y) - eps <= elbow.y <= max(shoulder.y, wrist.y) +
eps``. The UPPER bound is correct (an elbow above both shoulder and wrist
is a genuine hyperextension artifact). **The LOWER bound is anatomically
wrong**: raising a hand to shoulder height to sign, a real elbow hangs
DOWN, often well below both the shoulder and the wrist -- that is the
natural, correct "V" shape (shoulder high, elbow low, wrist raised back
up), not a defect. Recalibrating the pole to satisfy that wrong lower
bound is what flattened the arm. Fixed by (1) removing the lower bound
from that test (kept the upper bound -- see
``tests/test_arm_configuration.py``'s C1, renamed to make the one-sided
nature explicit), and (2) reverting ``POLE_DIRECTION_RIGHT``/``LEFT`` to
this project's ORIGINAL estimate from before either of the two tasks
above touched it (``(∓0.3, -1.0, 1.0)``, back-and-down-and-slightly-out --
see the constant's own comment) -- this value already satisfies the
CORRECT (upper-bound-only) invariant for all 4 of this project's own test
configs (level/high/low/splayed), verified by measurement, not by
assumption: see ``tests/test_arm_configuration.py``'s C1/C2/C3/C4.

The direct ``cos(angle) * aim + sin(angle) * bend_direction`` formula
above (from the "sửa bug hướng xoay IK" task) is UNCHANGED by this
correction -- it was already verified numerically equivalent to the
original ``Rotation.from_rotvec()``-based approach and is kept for its
simplicity/no-external-rotation-convention-dependency, not because it
fixed anything on its own (it didn't -- the bug was never in this
formula, at any point across either task).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

_EPSILON = 1e-6

# ESTIMATED (see module docstring's "actual root cause" section) -- "a real
# elbow points back and down" is this project's own original estimate, not
# sourced from an anthropometric table. Reverted to this value by the "sửa
# lại bất biến IK sai" task after the intervening "sửa bug hướng xoay IK"
# task's y=0 recalibration turned out to satisfy a WRONG invariant (elbow
# clamped between shoulder and wrist on BOTH sides -- see module
# docstring). This value -- back (+z, AWAY from the camera -- see
# pose_export.py's _body_to_pixel, which passes body-space z straight
# through to pose-format's own z, where MediaPipe's real convention is
# "larger z = farther from camera"), down (-y, a real elbow droops below
# shoulder height even when the wrist is raised), and slightly outward
# from the body midline (mirrored per side, same sign as that side's own
# shoulder x-offset in body_geometry.py) -- is verified (not assumed)
# against the CORRECT, upper-bound-only invariant across this project's 4
# own test configs (level/high/low/splayed) and both arms: see
# tests/test_arm_configuration.py's C1/C2/C3/C4.
POLE_DIRECTION_RIGHT: NDArray[np.float64] = np.array([-0.3, -1.0, 1.0])
POLE_DIRECTION_LEFT: NDArray[np.float64] = np.array([0.3, -1.0, 1.0])


def _normalized(v: NDArray[np.float64]) -> NDArray[np.float64]:
    result: NDArray[np.float64] = v / np.linalg.norm(v)
    return result


def solve_two_bone_ik(
    shoulder: NDArray[np.float64],
    wrist: NDArray[np.float64],
    pole_direction: NDArray[np.float64],
    upper_arm_length: float,
    forearm_length: float,
) -> NDArray[np.float64]:
    """Elbow position. Handles the 3 boundary cases this task's brief
    requires without raising or producing NaN (see ``tests/
    test_arm_ik.py``'s C3): wrist beyond max reach (arm straightens, does
    not raise), wrist closer than ``|L1 - L2|`` (arm folds to its tightest
    valid bend), and wrist ~= shoulder (falls back to the pole direction
    as the aim direction, since shoulder->wrist is undefined at d=0)."""
    to_wrist = wrist - shoulder
    d = float(np.linalg.norm(to_wrist))

    pole_norm = _normalized(pole_direction)
    aim = pole_norm if d < _EPSILON else to_wrist / d

    d_min = abs(upper_arm_length - forearm_length) + _EPSILON
    d_max = upper_arm_length + forearm_length - _EPSILON
    d_clamped = min(max(d, d_min), d_max)

    cos_angle = (upper_arm_length**2 + d_clamped**2 - forearm_length**2) / (2 * upper_arm_length * d_clamped)
    cos_angle = min(max(cos_angle, -1.0), 1.0)
    angle = float(np.arccos(cos_angle))

    # Elbow direction, built DIRECTLY from two orthonormal components
    # instead of a library rotation call (see module docstring's
    # "corrected diagnosis" -- this was verified to be numerically
    # equivalent to the previous Rotation.from_rotvec()-based approach,
    # not a behavior change on its own). aim/bend_direction are already
    # orthonormal, so this always has unit length and leans toward
    # bend_direction as angle grows from 0 toward pi.
    bend_direction = _bend_direction(aim, pole_norm)
    rotated_aim = np.cos(angle) * aim + np.sin(angle) * bend_direction

    elbow: NDArray[np.float64] = shoulder + rotated_aim * upper_arm_length
    return elbow


def _bend_direction(aim: NDArray[np.float64], pole_norm: NDArray[np.float64]) -> NDArray[np.float64]:
    """The component of the pole direction perpendicular to ``aim`` --
    i.e. which way, among the full circle perpendicular to shoulder->wrist,
    the elbow bends. Falls back to an arbitrary perpendicular if the pole
    direction happens to be exactly parallel to ``aim`` (a genuine
    degenerate case, not expected for the fixed pole constants above, but
    handled so this never raises/NaNs regardless of caller input)."""
    perpendicular = pole_norm - aim * np.dot(pole_norm, aim)
    length = np.linalg.norm(perpendicular)
    if length < _EPSILON:
        fallback = np.array([0.0, 0.0, 1.0]) if abs(aim[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
        perpendicular = fallback - aim * np.dot(fallback, aim)
        length = np.linalg.norm(perpendicular)
    return _normalized(perpendicular) if length >= _EPSILON else perpendicular
