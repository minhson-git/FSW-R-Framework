"""Category 2 (Movement) trajectory geometry: turns a ``MotionPath`` (what
kind of movement, in what plane) plus a symbol's ``rotation`` into actual
3D sample points -- the Category 2 analogue of ``fsw_base_symbol.py``'s
``_default_wrist_orientation()`` (which does the equivalent for Category
1's static wrist quaternion).

Structural basis (see PROGRESS.md's Phase 2 entry for the full derivation):
Category 2's 10 groups are not 10 independent concepts -- they are the
product of two orthogonal axes, ``path_type`` (5 values) x ``plane`` (3
values, or none for a few groups) -- see ``core/types.py``'s ``PathType``/
``MovementPlane``. That structure is what makes generating (not measuring)
all 242 base symbols' geometry from a handful of formulas possible, unlike
Category 1 where the 10 groups are independent hand shapes with no shared
formula.

** UNVERIFIED ASSUMPTIONS ** (flagged here, in ``_meta`` of the generated
JSON, and in PROGRESS.md's Phase 2 entry -- not silently treated as fact):
- The canonical (un-rotated, un-planed) shape for each ``PathType`` below
  is this project's own approximation (straight line, circular arc, ...),
  not derived from any ISWA measurement or spec.
- **FINGER, corrected by this project's "Chuyển động khớp ngón tay" task:**
  FINGER used to be modeled here as the WRIST wiggling side-to-side in
  place ("small sinusoidal wiggle") -- semantically wrong: ISWA Group 12
  ("Finger Movement") means the FINGER JOINTS move, not the wrist/hand as
  a whole. FINGER's canonical shape is now a single fixed point, same
  degenerate treatment as CONTACT (the wrist genuinely does not move at
  all for Group 12) -- the actual joint-angle oscillation lives in
  ``core/finger_articulation.py``'s ``FingerArticulation``/
  ``articulate_joint_pose()``, wired into keyframe generation by
  ``timeline/build.py``, not here. See PROGRESS.md's entry for that task
  for the measured diagnosis and the corpus data (Group 12 = 16.8% of
  real signs, 5 base symbols cover 76.1% of its token usage) that
  motivated fixing this instead of just tuning the old wiggle's amplitude.
- ``rotation`` is applied about Z using the exact same formula as
  Category 1's compass sweep (``(rotation % 8) * 45``) -- reused for
  consistency with the rest of the codebase, NOT independently verified
  for Category 2's own rotation semantics.
- ``MovementPlane`` -> axis reorientation (WALL identity, FLOOR pitched
  -90 about X, DIAGONAL pitched -45 about X, halfway between) mirrors
  Category 1's Wall/Floor Plane treatment (``_fill_plane_degrees``) --
  again reused, not verified against any Category 2 source.
- Groups 11 (Contact), 12 (Finger Movement), and 20 (Circles) don't have a
  plane implied by their own names the way groups 13-19 do -- ``plane`` is
  ``None`` for those, and this module falls back to treating that as WALL
  (the least-arbitrary default, not a confirmed rule).
- ``repeat`` (1/2/3) is modeled as simply concatenating the same shape N
  times back to back -- not verified against what "double"/"triple"
  actually look like for a real Movement symbol.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from fsw_r.core.types import MotionPath, MovementPlane, PathType

_Samples = NDArray[np.float64]


def _canonical_shape(path: MotionPath, samples: int) -> _Samples:
    """The un-rotated, un-planed shape for one repeat of this path_type, in
    a local frame -- Y is the primary direction of travel (matching
    Category 1's wrist-to-fingertip convention), starting at the origin."""
    t = np.linspace(0.0, 1.0, samples)
    if path.path_type == PathType.CONTACT:
        # Degenerate: a single location, repeated -- nothing to animate
        # along, just where the contact happens.
        return np.tile(np.array([0.0, path.amplitude, 0.0]), (samples, 1))
    if path.path_type == PathType.FINGER:
        # Group 12 (Finger Movement): the WRIST does not translate at all
        # -- the movement is joint-angle oscillation on the fingers
        # themselves (see core/finger_articulation.py's
        # articulate_joint_pose(), wired in by timeline/build.py).
        # Degenerate trajectory, same treatment as CONTACT: a single
        # point, repeated -- see module docstring's "UNVERIFIED
        # ASSUMPTIONS" for why this replaced the previous (semantically
        # wrong) side-to-side wrist wiggle.
        return np.tile(np.array([0.0, path.amplitude, 0.0]), (samples, 1))
    if path.path_type == PathType.STRAIGHT:
        y = t * path.amplitude
        return np.column_stack([np.zeros_like(t), y, np.zeros_like(t)])
    if path.path_type == PathType.CURVED:
        y = t * path.amplitude
        x = path.curvature * path.amplitude * np.sin(np.pi * t)
        return np.column_stack([x, y, np.zeros_like(t)])
    if path.path_type == PathType.CIRCLE:
        angle = 2 * np.pi * t
        radius = path.amplitude / 2
        x = radius * np.cos(angle)
        y = path.amplitude / 2 + radius * np.sin(angle)
        return np.column_stack([x, y, np.zeros_like(t)])
    raise ValueError(f"unhandled path_type: {path.path_type}")


def _plane_rotation(plane: MovementPlane | None) -> Rotation:
    if plane is None or plane == MovementPlane.WALL:
        degrees = 0.0
    elif plane == MovementPlane.FLOOR:
        degrees = -90.0
    elif plane == MovementPlane.DIAGONAL:
        degrees = -45.0
    else:
        raise ValueError(f"unhandled plane: {plane}")
    return Rotation.from_euler("x", degrees, degrees=True)


def sample_trajectory(path: MotionPath, rotation: int, samples: int = 24) -> _Samples:
    """canonical (base) -> rotated about the page normal (``rotation``,
    same formula as Category 1's compass sweep) -> reoriented into the
    symbol's plane. Returns ``samples * path.repeat`` points, shape
    ``(N, 3)``. Uses ``scipy.spatial.transform.Rotation`` throughout, same
    as Category 1 -- no hand-rolled quaternion math."""
    shape = _canonical_shape(path, samples)
    compass = Rotation.from_euler("z", (rotation % 8) * 45.0, degrees=True)
    plane_rotation = _plane_rotation(path.plane)
    oriented: _Samples = plane_rotation.apply(compass.apply(shape))
    if path.repeat > 1:
        oriented = np.tile(oriented, (path.repeat, 1))
    return oriented
