"""Converts a parsed FSW AST (``FSWSignAST``) into fsw-r's own object model:
one ``FSWBaseSymbol`` per symbol in the sign, paired with that symbol's 2D
page position from the AST (useful for placing multiple symbols in a scene
-- e.g. a two-handed sign, or a sign mixing Category 1 hand shapes with
Category 2 movement paths). ``PositionedSymbol.symbol`` is typed as the
generic ``FSWBaseSymbol`` marker on purpose -- this module doesn't care
which category a symbol belongs to, so a sign's symbol list can freely mix
categories without any type or runtime branching here.

``FSWBaseSymbol``, not the narrower ``FSWRenderableSymbol``: Category 3
(Dynamics) symbols are deliberately NOT ``FSWRenderableSymbol`` (a Dynamics
symbol renders nothing of its own, see ``core/modifier_symbol.py``), so a
sign containing one still needs a common type to flow through here. Callers
that need the narrower type (e.g. ``timeline/build.py``, which only ever
accepts Category 1/2 symbols) already ``isinstance``-narrow before calling
anything renderable-specific -- this widening changes no runtime behavior,
verified by reading every call site (see PROGRESS.md's Category 3/5 entry).

This is the "AST -> FSWR" half of the pipeline:

    FSW string --[fsw_ast.parse_fsw_to_ast, real signwriting parser]--> AST
    AST        --[this module]--------------------------------------> FSWR

``fsw_to_fswr`` chains both steps for the common case of starting from a raw
FSW string.
"""

from __future__ import annotations

from dataclasses import dataclass

from fsw_r.core.fsw_ast import FSWSignAST, parse_fsw_to_ast
from fsw_r.core.fsw_base_symbol import FSWBaseSymbol
from fsw_r.core.fsw_symbol_key import parse_fsw_symbol_key
from fsw_r.core.registry import build_symbol


@dataclass(frozen=True)
class PositionedSymbol:
    symbol: FSWBaseSymbol
    x: int
    y: int


def ast_to_fswr(ast: FSWSignAST) -> tuple[PositionedSymbol, ...]:
    """Convert every symbol node in a parsed FSW AST into a
    ``PositionedSymbol`` (an actual ``FSWBaseSymbol`` plus its page
    position). Raises ``ValueError`` (via ``build_symbol``) for any symbol
    whose base symbol isn't registered yet."""
    return tuple(
        PositionedSymbol(
            symbol=build_symbol(parse_fsw_symbol_key(node.key)),
            x=node.x,
            y=node.y,
        )
        for node in ast.symbols
    )


def fsw_to_fswr(fsw: str) -> tuple[PositionedSymbol, ...]:
    """End-to-end: a real FSW sign string straight to fsw-r objects."""
    return ast_to_fswr(parse_fsw_to_ast(fsw))
