"""Two-bone IK, solved in closed form (law of cosines + a single known-angle
rotation) -- deliberately NOT a general iterative solver (CCD, FABRIK,
``scipy.optimize``, ...), per this task's brief: a closed-form two-bone
solution cannot produce a hyperextended/backward-bending elbow, the single
biggest cause of "deformed-looking person" artifacts a general solver can
produce. There is exactly one ``Rotation.from_rotvec()`` call below, which
applies ONE already-computed angle around ONE already-computed axis -- not
an iterative search, the same category of operation
``forward_kinematics.py`` already uses throughout (e.g.
``Rotation.from_euler``).

**Algorithm** (shoulder and wrist positions known, elbow position solved
for): law of cosines gives the angle at the shoulder between the
shoulder->wrist direction and the shoulder->elbow direction; the pole
vector picks WHICH of the two directions perpendicular to shoulder->wrist
(a full circle of otherwise-valid elbow positions) is used, i.e. which way
the elbow bends.

**Pole vector directions are ESTIMATED**, not measured -- "a real elbow
points back and down" is this task's own brief, not sourced from an
anthropometric table. See ``POLE_DIRECTION_RIGHT``/``POLE_DIRECTION_LEFT``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

_EPSILON = 1e-6

# ESTIMATED (see module docstring): elbow bends backward (+z, AWAY from the
# camera -- see pose_export.py's _body_to_pixel, which passes body-space z
# straight through to pose-format's own z, where MediaPipe's real
# convention is "larger z = farther from camera"), downward (-y, body-space
# y is up), and slightly outward from the body midline (mirrored per side,
# same sign as that side's own shoulder x-offset in body_geometry.py).
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

    bend_direction = _bend_direction(aim, pole_norm)
    axis = np.cross(aim, bend_direction)  # always well-defined: bend_direction is constructed perpendicular to aim
    rotated_aim = Rotation.from_rotvec(axis * angle).apply(aim)

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
