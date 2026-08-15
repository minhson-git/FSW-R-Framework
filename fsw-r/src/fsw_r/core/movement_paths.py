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


def _triangle_wave(t: _Samples, freq: float) -> _Samples:
    """A [-1, 1] triangle wave, ``freq`` full cycles over t in [0, 1] --
    sharp, angular vertices (unlike a sine), used for ZIGZAG/ARROWHEAD."""
    phase = t * freq
    result: _Samples = 2.0 * np.abs(2.0 * (phase - np.floor(phase + 0.5))) - 1.0
    return result


def _canonical_shape(path: MotionPath, samples: int) -> _Samples:
    """The un-rotated, un-planed shape for one repeat of this path_type, in
    a local frame -- Y is the primary direction of travel (matching
    Category 1's wrist-to-fingertip convention), starting at the origin.

    The 17 shapes below CONTACT..CIRCLE (see ``PathType``'s own docstring
    for which real ISWA base-symbol NAME family each comes from) are this
    project's own approximation of each name's implied trajectory, same
    caveat as CURVED/CIRCLE already had -- not derived from any ISWA
    glyph measurement, only required to be geometrically DISTINCT from
    STRAIGHT and from each other (see this task's C6: distance between
    point clouds must clear a measurable threshold), not pixel-accurate to
    the real glyph. Flagged in ``data/movement_paths.json``'s own ``_meta``
    too, not silently treated as exact."""
    t = np.linspace(0.0, 1.0, samples)
    a = path.amplitude
    c = path.curvature
    zeros = np.zeros_like(t)
    if path.path_type == PathType.CONTACT:
        # Degenerate: a single location, repeated -- nothing to animate
        # along, just where the contact happens.
        return np.tile(np.array([0.0, a, 0.0]), (samples, 1))
    if path.path_type == PathType.FINGER:
        # Group 12 (Finger Movement): the WRIST does not translate at all
        # -- the movement is joint-angle oscillation on the fingers
        # themselves (see core/finger_articulation.py's
        # articulate_joint_pose(), wired in by timeline/build.py).
        # Degenerate trajectory, same treatment as CONTACT: a single
        # point, repeated -- see module docstring's "UNVERIFIED
        # ASSUMPTIONS" for why this replaced the previous (semantically
        # wrong) side-to-side wrist wiggle.
        return np.tile(np.array([0.0, a, 0.0]), (samples, 1))
    if path.path_type == PathType.STRAIGHT:
        return np.column_stack([zeros, t * a, zeros])
    if path.path_type == PathType.CURVED:
        # A single smooth arc, bulging out and back to the axis -- covers
        # "Curve ... Quarter/Half/3 Quarter Circle" (arc sweep is a
        # curvature/amplitude nuance, not a different path_type).
        x = c * a * np.sin(np.pi * t)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.CIRCLE:
        angle = 2 * np.pi * t
        radius = a / 2
        x = radius * np.cos(angle)
        y = a / 2 + radius * np.sin(angle)
        return np.column_stack([x, y, zeros])
    if path.path_type == PathType.FLEX:
        # Mostly straight; hooks off-axis only in the last ~35% ("Wrist
        # Flex" = a flex at the END of an otherwise straight movement).
        bend = np.where(t > 0.65, ((t - 0.65) / 0.35) ** 2, 0.0)
        x = c * a * bend
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.CROSS:
        # One full sideways sine cycle while advancing -- the path crosses
        # the central travel axis, unlike CURVED which only bulges once.
        x = c * a * np.sin(2 * np.pi * t)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.BEND:
        # One gentle, LINEAR direction change partway (distinguished from
        # CORNER's sharp right angle and FLEX's late hook by being a
        # shallow ramp starting at the midpoint).
        x = c * a * np.where(t < 0.5, 0.0, (t - 0.5) * 2.0)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.CORNER:
        # A genuine right-angle turn: travel along Y for the first half,
        # then along X for the second half.
        half = a / 2
        y = np.minimum(t * 2.0, 1.0) * half
        x = np.maximum((t - 0.5) * 2.0, 0.0) * c * a
        return np.column_stack([x, y, zeros])
    if path.path_type == PathType.CHECK:
        # An asymmetric tick mark: a short dip, then a longer stroke back
        # up past the start ("✓" shape).
        dip_end = 0.35
        y = np.where(
            t < dip_end, -0.5 * a * (t / dip_end), -0.5 * a + (t - dip_end) / (1 - dip_end) * 1.5 * a
        )
        x = c * a * 0.3 * np.sin(np.pi * np.clip((t - dip_end) / (1 - dip_end), 0.0, 1.0))
        return np.column_stack([x, y, zeros])
    if path.path_type == PathType.BOX:
        # A closed 4-sided path, traced in 4 equal quarters of t.
        side = a
        x = np.select(
            [t < 0.25, t < 0.5, t < 0.75],
            [t / 0.25 * side, side, side - (t - 0.5) / 0.25 * side],
            default=0.0,
        )
        y = np.select(
            [t < 0.25, t < 0.5, t < 0.75],
            [0.0, (t - 0.25) / 0.25 * side, side],
            default=side - (t - 0.75) / 0.25 * side,
        )
        return np.column_stack([x, y, zeros])
    if path.path_type == PathType.ZIGZAG:
        # Sharp alternating diagonal segments (a triangle wave) while
        # advancing -- unlike WAVE's smooth sine or PEAKS' one-sided bumps.
        x = c * a * 0.4 * _triangle_wave(t, freq=3.0)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.PEAKS:
        # A one-sided triangle wave (always bulging the same way, like a
        # mountain range) -- distinguishes it from ZIGZAG's signed,
        # alternating triangle wave.
        x = c * a * 0.4 * np.abs(_triangle_wave(t, freq=2.5))
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.TRAVEL_ROTATION:
        # A constant-radius loop while advancing (a helix) -- a few slow,
        # wide oscillations (distinguished from SHAKE's many tight ones).
        radius = c * a * 0.15
        x = radius * np.sin(2 * np.pi * 3.0 * t)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.SHAKE:
        # A tight, high-frequency, small-amplitude wiggle while advancing.
        radius = c * a * 0.05
        x = radius * np.sin(2 * np.pi * 10.0 * t)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.SPIRAL:
        # An expanding-radius loop while advancing -- radius grows from 0
        # to its max as t goes 0->1, unlike TRAVEL_ROTATION's constant one.
        growing_radius = c * a * 0.2 * t
        x = growing_radius * np.cos(2 * np.pi * 3.0 * t)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.HUMP:
        # A single bump concentrated near the midpoint, returning to
        # baseline at both ends -- sharper/more localized than CURVED's
        # smooth full-range arc.
        x = c * a * np.exp(-(((t - 0.5) * 5.0) ** 2))
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.LOOP:
        # One small self-contained loop (a full circle in local xy) with a
        # little net forward travel -- unlike CIRCLE (no net travel) or
        # TRAVEL_ROTATION (many loops, mostly net travel).
        radius = c * a * 0.2
        x = radius * (1.0 - np.cos(2 * np.pi * t))
        y = t * 0.3 * a + radius * np.sin(2 * np.pi * t)
        return np.column_stack([x, y, zeros])
    if path.path_type == PathType.WAVE:
        # A smooth, signed sine wave (2-3 curves) while advancing --
        # distinguished from ZIGZAG (sharp) and PEAKS (one-sided).
        x = c * a * 0.3 * np.sin(2 * np.pi * 2.5 * t)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.CURVE_THEN_STRAIGHT:
        # Curved for the first half (bulges out and back to the axis by
        # the midpoint), dead straight for the second -- one compound path.
        x = np.where(t < 0.5, c * a * np.sin(np.pi * (t / 0.5)), 0.0)
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.CURVED_CROSS:
        # CROSS's sideways crossing, but with an added second harmonic so
        # the strokes read as curved rather than a clean single sine.
        x = c * a * (np.sin(2 * np.pi * t) + 0.3 * np.sin(4 * np.pi * t))
        return np.column_stack([x, t * a, zeros])
    if path.path_type == PathType.ARROWHEAD:
        # A single sharp symmetric tent (chevron apex at the midpoint) --
        # one linear peak, unlike PEAKS' several smoother ones.
        x = c * a * 0.5 * _triangle_wave(t, freq=1.0)
        return np.column_stack([x, t * a, zeros])
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
