"""Mock of the pre-existing FSW parsing layer.

The real system is assumed to already have a class that parses an ISWA/FSW
symbol string into (category, group, base_symbol_number, fill, rotation) and
computes a full wrist orientation from fill/rotation. This module only
reproduces that contract so the fsw-r layer can inherit from it -- the
in-plane angle helper below (``_rotation_angle_degrees``) is a stand-in for
whatever richer logic the real system already has.

If a real ``FSWBaseSymbol`` implementation exists elsewhere in the codebase,
replace this module with an import of that implementation instead of the
mock below -- nothing outside this file should need to change, since
``FSWRenderableSymbol`` only depends on the interface defined here.

ISWA rotation rule (fixed, not a mock detail -- this is how the format
actually encodes hand symbols): ``rotation`` is a hex digit 0-f, split into
two halves of 8:
  - 0-7: counter-clockwise, angle = (rotation % 8) * 45 degrees, RIGHT hand.
  - 8-f: clockwise (mirror of the 0-7 half), same angle formula, LEFT hand.
16 rotation values exist (instead of 8) precisely because hand_side is
encoded in *which half* rotation falls into -- ISWA has no separate
left/right field. ``rotation`` changes which way the extended finger(s)
point on the page, like a clock hand (0=up, 90=sideways, 180=down, ...).

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

from abc import ABC, abstractmethod

from scipy.spatial.transform import Rotation

from fsw_r.core.types import HandSide


class FSWBaseSymbol(ABC):
    def __init__(
        self,
        category: int,  # 1 = Hands
        group: int,  # 1..10
        base_symbol_number: int,  # 1, 2, 3, ... (within group)
        fill: int,  # 0..5 (6 valid ISWA fill values)
        rotation: int,  # 0..15 (16 valid ISWA rotation values, hex 0-f)
    ) -> None:
        if not (0 <= fill <= 5):
            raise ValueError(f"fill must be in range 0-5, got {fill}")
        if not (0 <= rotation <= 15):
            raise ValueError(f"rotation must be in range 0-15, got {rotation}")
        self.category = category
        self.group = group
        self.base_symbol_number = base_symbol_number
        self.fill = fill
        self.rotation = rotation

    @property
    def hand_side(self) -> HandSide:
        """ISWA rule: rotation 0-7 -> RIGHT, 8-15 -> LEFT (mirror half).

        This is a pure function of ``rotation``, identical for every symbol
        in every group -- it is defined once here and must not be
        overridden or re-derived further down the hierarchy.
        """
        return HandSide.LEFT if self.rotation >= 8 else HandSide.RIGHT

    def _rotation_angle_degrees(self) -> float:
        """In-plane rotation angle, within one hand's own 8-step half-circle."""
        return (self.rotation % 8) * 45.0

    def _fill_facing_degrees(self) -> float:
        """ISWA fill, lower component (fill % 3): which side of the hand
        faces the viewer -- 0 = Palm of Hand, 90 = Side of Hand, 180 = Back
        of Hand. See the "Six Palm Facings" rule documented above."""
        return (self.fill % 3) * 90.0

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

    @abstractmethod
    def get_wrist_orientation(self) -> Rotation:
        """Assumed to already exist (more fully) in the real system: wrist/
        hand orientation derived from fill/rotation (ISWA). Mocked here
        using ``_rotation_angle_degrees()``."""
        raise NotImplementedError

    @property
    def symbol_id(self) -> str:
        return f"{self.category:02d}-{self.group:02d}-{self.base_symbol_number:03d}"
