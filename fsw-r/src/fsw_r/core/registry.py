"""Builds an actual, correctly-typed ``FSWRenderableSymbol`` from an
already-decoded FSW symbol -- e.g. a decoded "Index, fill=1, rotation=1"
becomes a real ``HandSymbol`` instance, not a bag of raw ints.

Dispatch is by **category**, not by per-symbol registration: ``_CATEGORY_SYMBOL``
maps a category number to the one class (or factory) that handles every base
symbol in it (``{1: HandSymbol, 2: MovementSymbol, 4: <face factory>}``).
Adding a new category (once its own ``PoseTable`` + symbol class exist, see
``core/pose_table.py``) is exactly one more entry here -- nothing else in
``core/`` needs to change. This is the whole point of keying everything by
``base_hex`` through the pipeline (``fsw_symbol_key.py``,
``fsw_base_symbol.py``): a category dispatch this simple wouldn't be possible
if base_hex had already been decomposed into category/group/
base_symbol_number and thrown away, the way it used to be.

``_OVERRIDES`` is an explicit, currently-empty escape hatch for a future
*individual* base symbol that needs genuinely distinct behavior (e.g. a
wrist-orientation formula that turns out not to be generic) rather than
just distinct joint angles -- keyed by ``base_hex``, checked before the
category dispatch. See PROGRESS.md's "Refactor tang Group sang
data-driven" entry for why the previous one-class-per-base-symbol design
(and its ``@register_symbol`` decorator) was replaced.

This is the "converter" half of the FSW -> AST -> FSWR pipeline (see
``fsw_ast.py`` for the AST half, ``fswr_converter.py`` for the version that
converts a whole parsed sign at once). ``symbol_from_fsw`` is kept here as a
convenience for the common single-key case.
"""

from __future__ import annotations

from typing import Callable

from fsw_r.core.face_pose_table import FACE_POSE_TABLE
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol, parse_fsw_symbol_key
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.iswa_data import symbol_id_of
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol

# A concrete symbol's constructor -- (base_hex, fill, rotation) ->
# FSWRenderableSymbol, the shape HandSymbol/MovementSymbol both use.
_Constructor = Callable[..., FSWRenderableSymbol]


def _make_category4_symbol(base_hex: int, fill: int, rotation: int) -> FSWRenderableSymbol:
    """Category 4 (Head & Face) dispatch. Unlike Categories 1 and 2, this
    category is only partially covered: the facial-expression groups are
    authored symbol-by-symbol (see face_pose_table.py) and the Head group's
    movement paths / non-facial marks (teeth, ears, ...) aren't blend-shapes.
    So build a FaceSymbol only for what's actually authored, and reject the
    rest honestly rather than pretend an un-authored base exists."""
    if base_hex in FACE_POSE_TABLE:
        return FaceSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    raise ValueError(
        f"Category 4 symbol {symbol_id_of(base_hex)} (base 0x{base_hex:03x}) "
        f"is not supported yet (Head movement paths, non-facial marks, and "
        f"un-authored facial symbols -- see PHASE4_PLAN.md)"
    )


# category -> the one class (or factory) that covers every base symbol in it.
# Adding a category is one more entry here -- see PROGRESS.md's Phase 2 entry
# for the "extensibility check" that adding {2: MovementSymbol} needed no
# other change in core/; {4: ...} followed the same pattern for Head & Face.
_CATEGORY_SYMBOL: dict[int, _Constructor] = {
    1: HandSymbol,
    2: MovementSymbol,
    4: _make_category4_symbol,
}

# Escape hatch for a future INDIVIDUAL base symbol needing distinct
# behavior, not just distinct numbers -- keyed by base_hex. Empty today:
# 0/261 Category 1 base symbols need this.
_OVERRIDES: dict[int, _Constructor] = {}


def build_symbol(parsed: ParsedFSWSymbol) -> FSWRenderableSymbol:
    """Instantiate the symbol matching ``parsed.base_hex`` with the decoded
    fill/rotation.

    Raises ``ValueError`` if ``parsed``'s category has no entry in
    ``_CATEGORY_SYMBOL`` yet -- e.g. a real, well-formed Category 3
    (Dynamics) key parses fine (``parse_fsw_symbol_key`` doesn't block it)
    but building an object for it fails here, honestly, as "category not
    supported" rather than a parse error.
    """
    cls = _OVERRIDES.get(parsed.base_hex)
    if cls is None:
        cls = _CATEGORY_SYMBOL.get(parsed.category)
        if cls is None:
            raise ValueError(
                f"Category {parsed.category} is not supported yet "
                f"(base 0x{parsed.base_hex:03x}, symbol_id {parsed.symbol_id})"
            )
    return cls(base_hex=parsed.base_hex, fill=parsed.fill, rotation=parsed.rotation)


def symbol_from_fsw(key: str) -> FSWRenderableSymbol:
    """Decode a single, bare real FSW symbol key (e.g. ``"S10011"``) and
    instantiate the matching base symbol.

    Convenience wrapper around ``parse_fsw_symbol_key`` + ``build_symbol``
    for the common case of a single symbol, not a full multi-symbol sign --
    for that, see ``fswr_converter.fsw_to_fswr``.
    """
    return build_symbol(parse_fsw_symbol_key(key))
