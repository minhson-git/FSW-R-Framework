"""A single class for all 8 Category 3 (Dynamics) base symbols -- the
Category 3 analogue of ``hand_symbol.py``'s ``HandSymbol``, except it
implements ``FSWModifierSymbol`` (``get_modifier()``), not any
``FSWRenderableSymbol`` contract -- see ``core/modifier_symbol.py``'s
docstring for why. Looks its own modifier up in ``core/pose_table.py``'s
``DYNAMICS_MODIFIER_TABLE`` by ``base_hex``, same pattern as
``HandSymbol``/``MovementSymbol``/``BodySymbol``.
"""

from __future__ import annotations

from fsw_r.core.dynamics_types import DynamicsModifier
from fsw_r.core.modifier_symbol import FSWModifierSymbol
from fsw_r.core.pose_table import DYNAMICS_MODIFIER_TABLE
from fsw_r.core.types import HandSide


class DynamicsSymbol(FSWModifierSymbol):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        """Deliberately ``None`` -- a Dynamics symbol modifies the whole
        sign's tempo/emphasis, not one hand's pose; ISWA has no per-hand
        Dynamics variant (see ``DynamicsModifier``'s docstring: the
        (fill, rotation) split is by base symbol, not by hand)."""
        return None

    def get_modifier(self) -> DynamicsModifier:
        return DYNAMICS_MODIFIER_TABLE[self.base_hex]
