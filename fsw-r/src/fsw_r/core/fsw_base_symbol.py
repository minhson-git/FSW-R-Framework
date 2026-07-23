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
left/right field.
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

    @abstractmethod
    def get_wrist_orientation(self) -> Rotation:
        """Assumed to already exist (more fully) in the real system: wrist/
        hand orientation derived from fill/rotation (ISWA). Mocked here
        using ``_rotation_angle_degrees()``."""
        raise NotImplementedError

    @property
    def symbol_id(self) -> str:
        return f"{self.category:02d}-{self.group:02d}-{self.base_symbol_number:03d}"
