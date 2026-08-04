"""Builds an actual, correctly-typed ``FSWRenderableSymbol`` from an
already-decoded FSW symbol -- e.g. a decoded "Index, fill=1, rotation=1"
becomes a real ``HandSymbol`` instance, not a bag of raw ints.

Category 1 (Hands) base symbols no longer need per-class registration: all
261 resolve to ``HandSymbol`` (``core/hand_symbol.py``), which looks its
pose up in ``core/pose_table.py`` by ``symbol_id``. ``_OVERRIDES`` is an
explicit, currently-empty escape hatch for a future base symbol that needs
genuinely distinct *behavior* (e.g. a wrist-orientation formula that turns
out not to be generic) rather than just distinct joint angles -- see
PROGRESS.md's "Refactor tang Group sang data-driven" entry for why the
previous one-class-per-base-symbol design (and its ``@register_symbol``
decorator) was replaced.

This is the "converter" half of the FSW -> AST -> FSWR pipeline (see
``fsw_ast.py`` for the AST half, ``fswr_converter.py`` for the version that
converts a whole parsed sign at once). ``symbol_from_fsw`` is kept here as a
convenience for the common single-key case.
"""

from __future__ import annotations

from typing import Callable

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol, parse_fsw_symbol_key
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.pose_table import HAND_POSE_TABLE
from fsw_r.core.renderable_symbol import FSWRenderableSymbol

# A concrete symbol's constructor -- (base_hex, fill, rotation) ->
# FSWRenderableSymbol, the shape HandSymbol itself uses.
_Constructor = Callable[..., FSWRenderableSymbol]

# Escape hatch for a future base symbol needing distinct behavior, not just
# distinct numbers -- keyed by symbol_id (e.g. "01-01-001"). Empty today:
# 0/261 Category 1 base symbols need this: HandSymbol covers all of them.
_OVERRIDES: dict[str, _Constructor] = {}


def build_symbol(parsed: ParsedFSWSymbol) -> FSWRenderableSymbol:
    """Look up the given base_hex and instantiate the matching symbol with
    the decoded fill/rotation.

    Raises ``ValueError`` if that symbol_id has no entry in
    ``HAND_POSE_TABLE`` -- for Category 1 keys parsed from a real FSW
    string this can no longer actually happen (all 261 are covered), but it
    remains reachable via a synthetic ``ParsedFSWSymbol`` naming a
    base_hex that doesn't exist in any group.
    """
    symbol_id = parsed.symbol_id
    if symbol_id not in HAND_POSE_TABLE:
        raise ValueError(
            f"no base symbol registered for base_hex=0x{parsed.base_hex:03x} "
            f"(symbol_id={symbol_id})"
        )
    cls = _OVERRIDES.get(symbol_id, HandSymbol)
    return cls(base_hex=parsed.base_hex, fill=parsed.fill, rotation=parsed.rotation)


def symbol_from_fsw(key: str) -> FSWRenderableSymbol:
    """Decode a single, bare real FSW symbol key (e.g. ``"S10011"``) and
    instantiate the matching base symbol.

    Convenience wrapper around ``parse_fsw_symbol_key`` + ``build_symbol``
    for the common case of a single symbol, not a full multi-symbol sign --
    for that, see ``fswr_converter.fsw_to_fswr``.
    """
    return build_symbol(parse_fsw_symbol_key(key))
