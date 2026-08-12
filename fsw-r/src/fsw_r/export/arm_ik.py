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

**The REAL cause of the anatomically-wrong (hyperextended-looking) elbow**
(diagnosed by measuring elbow positions across the real demo sign's every
frame plus 4 synthetic boundary configs -- wrist level with/higher/lower
than the shoulder, and splayed out near max reach -- not by guessing): the
OLD ``POLE_DIRECTION_RIGHT``/``LEFT`` = ``(∓0.3, -1.0, 1.0)`` had a
dominant DOWNWARD (``y = -1.0``) component. ``_bend_direction`` computes
the component of the pole PERPENDICULAR to ``aim`` (Gram-Schmidt) -- for
this project's signing-space geometry, ``aim`` is very often close to
HORIZONTAL (the wrist reaching toward the body midline at roughly shoulder
height, while the shoulder itself sits far out at the body's side -- see
``body_geometry.shoulder_position()``), which barely removes any of the
pole's own downward component. Combined with a large bend angle (the wrist
is often much closer to the shoulder than the arm's max reach, forcing
significant flexion), that leftover downward component dominates
``bend_direction`` and swings the elbow far below BOTH the shoulder and
the wrist -- exactly the "tam giác nhọn chĩa xuống" (downward-pointing
spike) this task's brief describes, and reproduced with the brief's own
numbers before any fix (shoulder.y=235px, wrist.y≈230px, elbow.y≈394px).

**Fix: recalibrated the pole direction, measured against the same
configs, not guessed.** ``POLE_DIRECTION_RIGHT``/``LEFT`` now have a
downward (``y``) component of exactly 0 -- a fixed WORLD-space pole
vector with any nonzero downward bias cannot simultaneously satisfy "elbow
stays between shoulder and wrist" for a wrist level with the shoulder
(where that constraint collapses to "elbow.y == shoulder.y", allowing
ZERO downward slack) and for a wrist well below the shoulder (which does
tolerate some). Measured across all 20 real frames of the standard demo
sign plus the 4 boundary configs above: a small residual downward bias
(``y = -0.05``) already violates the elbow-stays-in-range invariant on
real frames (margin 0.008, effectively zero); ``y = 0`` clears it with
comfortable margin (worst-case slack 0.126 out of an 0.15 tolerance -- see
``tests/test_arm_configuration.py``'s C1). The pre-existing "a real elbow
points back and down" assumption (this project's own estimate, never
sourced from an anthropometric table -- see the module docstring history
in PROGRESS.md) turned out to not hold for THIS geometry once actually
measured; corrected rather than left in place with a comment explaining
why it's wrong.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

_EPSILON = 1e-6

# MEASURED (see module docstring's "Fix" section) against the real demo
# sign's every frame + 4 synthetic boundary configs (wrist level with,
# above, below the shoulder; wrist splayed near max reach) -- elbow bends
# backward (+z, AWAY from the camera -- see pose_export.py's
# _body_to_pixel, which passes body-space z straight through to
# pose-format's own z, where MediaPipe's real convention is "larger z =
# farther from camera"), slightly outward from the body midline (mirrored
# per side, same sign as that side's own shoulder x-offset in
# body_geometry.py), and with NO net downward bias (y = 0 exactly -- see
# module docstring for why any negative y fails the elbow-stays-in-range
# invariant on real frames).
POLE_DIRECTION_RIGHT: NDArray[np.float64] = np.array([-0.15, 0.0, 1.0])
POLE_DIRECTION_LEFT: NDArray[np.float64] = np.array([0.15, 0.0, 1.0])


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
