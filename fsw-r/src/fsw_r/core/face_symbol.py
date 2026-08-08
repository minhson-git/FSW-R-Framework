"""A single class for every authored Category 4 facial-expression base
symbol (Groups 23-26), the face analogue of ``HandSymbol``.

It carries no wrist orientation (a face isn't rigidly oriented by
fill/rotation the way a hand is -- that's why ``get_wrist_orientation`` is
no longer on the shared base; see PHASE4_PLAN.md Bước 0) and no
``hand_side`` (ISWA doesn't encode a performing hand in a face symbol, so it
returns ``None``). Its pose accessor is ``get_expression()``, looked up by
``(base_hex, fill)`` in ``core/face_pose_table.py``.
"""

from __future__ import annotations

from fsw_r.core.face_pose_table import FACE_NAME_TABLE, FACE_POSE_TABLE
from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.renderable_symbol import FSWFaceRenderable
from fsw_r.core.types import HandSide


class FaceSymbol(FSWFaceRenderable):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        """A facial-expression symbol doesn't encode a performing hand -- so
        ``None``, per ``FSWBaseSymbol.hand_side``'s per-category contract."""
        return None

    @property
    def name(self) -> str:
        """The base symbol's real ISWA name (e.g. "Mouth Smile")."""
        return FACE_NAME_TABLE[self.base_hex]

    def get_expression(self) -> FaceExpressionPose:
        """ARKit-52 blend-shape weights for this symbol at its current
        ``fill``. Raises ``KeyError`` with a clear message if this
        particular fill wasn't authored (the constructor already accepted
        it as ISWA-valid, so a gap here means missing data, not bad input)."""
        by_fill = FACE_POSE_TABLE[self.base_hex]
        try:
            return by_fill[self.fill]
        except KeyError:
            raise KeyError(
                f"{self.symbol_id} (base 0x{self.base_hex:03x}) has no authored expression "
                f"for fill={self.fill}; authored fills are {sorted(by_fill)}"
            ) from None
