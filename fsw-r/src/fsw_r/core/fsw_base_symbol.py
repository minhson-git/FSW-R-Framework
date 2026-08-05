"""The shared base for every renderable ISWA symbol, across all categories.

Holds only what is universal to *every* category: the ``base_hex`` identity
(``category``/``group``/``base_symbol_number``/``symbol_id`` are derived
properties, so they never need reconstructing from pieces further down the
hierarchy -- see ``core/iswa_data.py``), per-symbol ``fill``/``rotation``
validation, and the abstract ``hand_side``.

Deliberately category-agnostic: this base does NOT know how any category
turns ``fill``/``rotation`` into a 3D pose. The Hands "Six Palm Facings"
fill + clock-hand rotation formula lives in ``core/orientation.py``'s
``WristOrientationMixin`` (opt-in), and the joint-pose / expression
accessors live on each category's own concrete class (``HandSymbol``,
future ``FaceSymbol``/``HeadSymbol``). ``FSWRenderableSymbol`` (in
``core/renderable_symbol.py``) is just a marker over this base -- see
``PHASE4_PLAN.md`` (Bước 0) for why the hand-specific parts were moved out.

``fill``/``rotation`` validity is checked **per base symbol**, not just
against the global 0-5/0-15 ranges -- see ``core/iswa_data.py`` for why
(most Category 1 base symbols do have all 6 fills x 16 rotations, but 8 of
them don't, e.g. 01-05-002 only has fill=1).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from fsw_r.core.iswa_data import (
    base_symbol_number_of,
    category_of,
    group_of,
    symbol_id_of,
    valid_combinations_for,
)
from fsw_r.core.types import HandSide


class FSWBaseSymbol(ABC):
    def __init__(
        self,
        base_hex: int,  # ISWA base symbol code, e.g. 0x100 = "Index" (01-01-001)
        fill: int,  # 0..5 (6 syntactically valid ISWA fill values)
        rotation: int,  # 0..15 (16 syntactically valid ISWA rotation values, hex 0-f)
    ) -> None:
        # ISWA defines which (fill, rotation) combinations actually exist
        # per base symbol, not globally -- e.g. 01-05-002 only has fill=1,
        # while most Category 1 base symbols have all 6. See
        # core/iswa_data.py for where this table comes from.
        symbol_id = symbol_id_of(base_hex)  # also validates base_hex is a real ISWA base
        combos = valid_combinations_for(base_hex)
        if fill not in combos.fills:
            raise ValueError(
                f"fill={fill} is not valid for {symbol_id} (base 0x{base_hex:03x}); "
                f"ISWA only defines fills={sorted(combos.fills)}, "
                f"rotations={sorted(combos.rotations)}"
            )
        if rotation not in combos.rotations:
            raise ValueError(
                f"rotation={rotation} is not valid for {symbol_id} (base 0x{base_hex:03x}); "
                f"ISWA only defines fills={sorted(combos.fills)}, "
                f"rotations={sorted(combos.rotations)}"
            )
        self.base_hex = base_hex
        self.fill = fill
        self.rotation = rotation

    @property
    def category(self) -> int:
        return category_of(self.base_hex)

    @property
    def group(self) -> int:
        return group_of(self.base_hex)

    @property
    def base_symbol_number(self) -> int:
        return base_symbol_number_of(self.base_hex)

    @property
    @abstractmethod
    def hand_side(self) -> HandSide | None:
        """Which hand performs this symbol, if ISWA even encodes that in
        this category's own symbols -- ``None`` means it doesn't.

        How this is derived is NOT generic across categories: Category 1
        (Hands) encodes it in ``rotation`` (0-7 -> RIGHT, 8-15 -> LEFT, see
        ``HandSymbol.hand_side``), confirmed against
        ``signwriting.utils.mirror.mirror.py``'s own docstring ("0-7 are
        right-hand ... 8-15 are the corresponding left-hand variants").
        Category 2 (Movement) does NOT follow this rule -- measured on
        ``sign-language-processing/signbank-plus`` (257,800 signs): among
        single-hand-symbol signs, Category 2 rotation 0-7 vs 8-15 occurs at
        nearly the same rate (~62%/38%) regardless of which hand performs
        the sign, so rotation alone doesn't predict hand_side there the way
        it does in Category 1. ``fill`` correlates far better in that same
        corpus (fill=0 vs fill=1 differs ~97%/3% by hand), but with enough
        noise (~27% counterexamples) that this project isn't ready to
        implement it as a hard rule yet -- see ROADMAP.md Pha 2 for the
        numbers and open question. Left abstract here so each category's
        symbol class states its own rule explicitly instead of inheriting
        Category 1's by accident.
        """
        raise NotImplementedError

    @property
    def symbol_id(self) -> str:
        """Display-only ``"01-05-002"``-style id -- never used as a lookup
        key, see ``core/iswa_data.py``'s ``symbol_id_of()``."""
        return symbol_id_of(self.base_hex)
