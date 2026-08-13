"""A single class for all 242 Category 2 (Movement) base symbols -- the
Category 2 analogue of ``hand_symbol.py``'s ``HandSymbol``. Looks its own
motion path up in ``core/pose_table.py``'s ``MOVEMENT_PATH_TABLE`` by
``base_hex``, same pattern as ``HandSymbol``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.pose_table import FINGER_ARTICULATION_TABLE, MOVEMENT_PATH_TABLE
from fsw_r.core.renderable_symbol import FSWMotionRenderable
from fsw_r.core.types import FingerArticulation, HandSide, MotionPath


class MovementSymbol(FSWMotionRenderable):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        """Deliberately ``None`` -- Category 1's rotation-based rule does
        NOT hold for Category 2. Measured on
        sign-language-processing/signbank-plus (257,800 signs, filtered to
        signs with exactly one Category 2 symbol so the performing hand is
        known from that sign's single Category 1 symbol):

            hand (from Cat 1) | Cat 2 rotation 0-7 | Cat 2 rotation 8-15
            RIGHT             | 62.2%              | 37.8%
            LEFT              | 58.5%               | 41.5%

        If ``rotation >= 8`` meant LEFT the way it does for Category 1,
        the LEFT row would be near 100%; it's nearly identical to the
        RIGHT row instead -- rotation does not predict hand_side here (it
        is instead a mirror/direction of the movement itself).

            hand (from Cat 1) | Cat 2 fill=0 | Cat 2 fill=1
            RIGHT             | 97.4%        | 0.5%
            LEFT              | 72.0%        | 26.7%

        ``fill`` correlates far better (fill=1 is ~53x more common when
        the hand is LEFT -- consistent with the SignWriting convention
        that fill code 0/1/2 = ISWA fill 1/2/3 = right/left/both), but
        with real noise (LEFT still uses fill=0 72% of the time).

        **That cross-check against Lessons in SignWriting is now done (MVP-2).**
        The arrowhead fill IS the cited performing-hand rule (dark = right,
        light = left, superposed = both; ``fill % 3`` collapses the "flipped"
        arrowhead variants -- see ``timeline/classify.tracks_for_movement``).
        The ~28% "noise" is not the rule being wrong: it is one-handed signs,
        where the arrowhead has no second hand to distinguish and defaults to
        dark, so the fill is only meaningful in TWO-handed signs -- which is
        exactly where ``tracks_for_movement`` uses it and where the ambiguity
        actually exists.

        This property still returns ``None``, deliberately: a *single*
        performing hand isn't a well-defined attribute of a movement symbol in
        isolation (fill=2 means BOTH), and one-handed signs don't consult it
        at all. Track routing -- the place that actually needs it, and only in
        the two-handed case -- lives in ``tracks_for_movement`` (which returns
        a *tuple* of tracks, so "both" needs no ``HandSide.BOTH`` member).
        """
        return None

    def get_motion_path(self) -> MotionPath:
        return MOVEMENT_PATH_TABLE[self.base_hex]

    def get_finger_articulation(self) -> FingerArticulation | None:
        """``FINGER_ARTICULATION_TABLE`` only has entries for Group 12
        (``PathType.FINGER``, 20 base symbols, 0x216-0x229) -- ``None``
        for every other Category 2 symbol, same "table membership IS the
        category/group check" pattern ``HAND_POSE_TABLE``/
        ``MOVEMENT_PATH_TABLE`` already use elsewhere in this module (no
        separate ``if path_type == FINGER`` branch needed here)."""
        if self.base_hex not in FINGER_ARTICULATION_TABLE:
            return None
        return FINGER_ARTICULATION_TABLE[self.base_hex]

    def get_wrist_orientation(self) -> Rotation:
        """Reuses the same generic fill/rotation -> quaternion formula
        Category 1 uses (``_default_wrist_orientation()``). UNVERIFIED for
        Category 2: this has only been chart-confirmed for Category 1's
        "Six Palm Facings" -- Category 2's fill/rotation semantics for
        orientation have not been checked against any Movement-specific
        source. Kept as the least-arbitrary default rather than inventing
        a second, equally unverified formula."""
        return self._default_wrist_orientation()

    def sample_trajectory(self, samples: int = 24) -> NDArray[np.float64]:
        return sample_trajectory(self.get_motion_path(), self.rotation, samples)
