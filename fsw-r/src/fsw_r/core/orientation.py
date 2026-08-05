"""The ISWA ``fill``/``rotation`` -> 3D wrist-orientation formula, as a
mixin so any category whose symbols are a rigid orientation of one part
(Category 1 Hands; Category 4 Group 22 "Head") can reuse it without
inheriting a hand-specific pose contract.

This logic used to live directly on ``FSWBaseSymbol``, but it is NOT
universal to every ISWA category (facial-expression symbols are
blend-shapes, not a rigid orientation), so it was moved out of the shared
base and into this opt-in mixin -- see ``PHASE4_PLAN.md`` (Bước 0) for why.
The formulas below are unchanged from that move; the behavior-critical
regression tests in ``tests/test_wrist_orientation.py`` pin them.

ISWA rotation rule for **Category 1 (Hands) specifically** (this is how the
format actually encodes hand symbols, see ``HandSymbol.hand_side`` for why
this is Category-1-only, not generic): ``rotation`` is a hex digit 0-f,
split into two halves of 8:
  - 0-7: counter-clockwise, angle = (rotation % 8) * 45 degrees, RIGHT hand.
  - 8-f: clockwise (mirror of the 0-7 half), same angle formula, LEFT hand.
16 rotation values exist (instead of 8) precisely because hand_side is
encoded in *which half* rotation falls into, for Hands -- ISWA has no
separate left/right field. ``rotation`` changes which way the extended
finger(s) point on the page, like a clock hand (0=up, 90=sideways,
180=down, ...) -- verified against the real chart for Category 1 only (see
ROADMAP.md's risk note); NOT assumed to generalize to other categories
without its own verification.

ISWA fill rule for hand symbols ("Six Palm Facings", confirmed against the
real chart at
https://www.signwriting.org/lessons/iswa/group01/01-01-001-01.html --
../ISWA2010_Symbol_Charts/01-01-001-ISWA_Chart.jpg): ``fill`` is 0-5 (6
values), and unlike ``rotation`` it does NOT change which way the finger
points -- it changes which side of the hand is presented, as two combined
components:
  - fill % 3: 0 = Palm of Hand, 1 = Side of Hand, 2 = Back of Hand.
  - fill // 3: 0 = Wall Plane (front view, arm reaching forward), 1 = Floor
    Plane (top view, arm reaching down).
So fill 0-2 are Palm/Side/Back in the Wall Plane, and fill 3-5 are the same
three in the Floor Plane, in that order -- matching the chart's 6 rows
top-to-bottom.
"""

from __future__ import annotations

from scipy.spatial.transform import Rotation


class WristOrientationMixin:
    """Provides ``_default_wrist_orientation()`` (and its three component
    helpers) to a symbol class that also inherits ``FSWBaseSymbol``.

    ``fill`` and ``rotation`` are supplied by ``FSWBaseSymbol.__init__`` on
    the concrete class this is mixed into; they are declared here (annotation
    only, no assignment) so this mixin type-checks in isolation without
    shadowing the real instance attributes at runtime."""

    fill: int
    rotation: int

    def _rotation_angle_degrees(self) -> float:
        """In-plane rotation angle, within one hand's own 8-step half-circle."""
        return (self.rotation % 8) * 45.0

    def _fill_facing_degrees(self) -> float:
        """ISWA fill, lower component (fill % 3): which side of the hand
        faces the viewer -- 0 = Palm of Hand, -90 = Side of Hand, -180 =
        Back of Hand. Negative so Side of Hand's palm normal ends up
        pointing toward -x (confirmed concretely: fill=1, rotation=0 must
        have the palm normal at -x, not +x) -- see
        test_fill_facing_shows_palm_side_or_back_at_rest. Back of Hand
        (180 vs -180) is unaffected by the sign either way, since a
        half-turn of a vector along the rotation axis's perpendicular
        lands in the same place regardless of direction."""
        return -(self.fill % 3) * 90.0

    def _fill_plane_degrees(self) -> float:
        """ISWA fill, upper component (fill // 3): which plane the whole
        hand/arm is held in -- 0 = Wall Plane (front view, arm reaching
        forward), -90 = Floor Plane (top view, arm reaching down). Negative
        so that, combined with the composition order in
        ``_default_wrist_orientation``, Palm of Hand (fill=3) ends up
        facing straight up at a top-view camera and Back of Hand (fill=5)
        straight down -- confirmed against the real chart's Floor Plane
        photos, see test_fill_palm_faces_up_in_floor_plane /
        test_fill_back_faces_down_in_floor_plane."""
        return -(self.fill // 3) * 90.0

    def _default_wrist_orientation(self) -> Rotation:
        """Combines the three ISWA-documented components into one
        quaternion: fill's facing twist (Palm/Side/Back, about y) is
        applied first/innermost, fill's plane pitch (Wall/Floor, about x)
        next, and rotation's page-plane compass sweep (about z) last/
        outermost. Base symbols with no quirks of their own can just return
        this directly from ``get_wrist_orientation()``.

        Facing must be applied BEFORE plane, not after: the Floor Plane
        pitch (about x) rotates the palm-normal vector onto the y axis --
        the same axis facing rotates around. Applying facing after plane
        would try to spin a vector that's now lying exactly on facing's own
        rotation axis, which cannot change it at all (a gimbal-lock-style
        degeneracy) -- Palm (fill=3) and Back (fill=5) would collapse onto
        the same orientation in the Floor Plane. Applying facing first
        (while the palm normal is still off-axis) avoids that."""
        facing = Rotation.from_euler("y", self._fill_facing_degrees(), degrees=True)
        plane = Rotation.from_euler("x", self._fill_plane_degrees(), degrees=True)
        compass = Rotation.from_euler("z", self._rotation_angle_degrees(), degrees=True)
        return compass * plane * facing
