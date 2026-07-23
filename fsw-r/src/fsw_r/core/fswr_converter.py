"""Converts a parsed FSW AST (``FSWSignAST``) into fsw-r's own object model:
one ``FSWRenderableSymbol`` per hand symbol in the sign, paired with that
symbol's 2D page position from the AST (useful for placing multiple hands
in a scene -- e.g. a two-handed sign).

This is the "AST -> FSWR" half of the pipeline:

    FSW string --[fsw_ast.parse_fsw_to_ast, real signwriting parser]--> AST
    AST        --[this module]--------------------------------------> FSWR

``fsw_to_fswr`` chains both steps for the common case of starting from a raw
FSW string.
"""

from __future__ import annotations

from dataclasses import dataclass

from fsw_r.core.fsw_ast import FSWSignAST, parse_fsw_to_ast
from fsw_r.core.fsw_symbol_key import parse_fsw_symbol_key
from fsw_r.core.registry import build_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol


@dataclass(frozen=True)
class PositionedSymbol:
    symbol: FSWRenderableSymbol
    x: int
    y: int


def ast_to_fswr(ast: FSWSignAST) -> tuple[PositionedSymbol, ...]:
    """Convert every symbol node in a parsed FSW AST into a
    ``PositionedSymbol`` (an actual ``FSWRenderableSymbol`` plus its page
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
