"""Parses a full FSW *sign* string into an AST -- a box marker/position plus
every positioned symbol in the sign -- using the real parser from
sutton-signwriting/core's Python port, the ``signwriting`` PyPI package
(``signwriting.formats.fsw_to_sign.fsw_to_sign``). This module makes the
actual library call; it does not re-implement the sign-level grammar.

A full FSW sign string looks like ``"M500x500S10010480x480S1061a520x520"``:
a box marker (``B``/``L``/``M``/``R``) + position, followed by one or more
``S<key><x>x<y>`` symbol entries -- e.g. a two-handed sign made of two Group
1 hand symbols placed side by side.

This is the "AST" half of the FSW -> AST -> FSWR pipeline. Decoding each
individual symbol *key* (e.g. ``"S10010"``) into category/group/
base_symbol_number/fill/rotation is a separate concern -- see
``fsw_symbol_key.py`` -- and turning that into an actual ``FSWRenderableSymbol``
is the converter in ``fswr_converter.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

from signwriting.formats.fsw_to_sign import fsw_to_sign


@dataclass(frozen=True)
class FSWSymbolNode:
    """One positioned symbol entry in a parsed FSW sign, exactly as the
    real parser extracted it -- ``key`` is still a raw, undecoded string
    (e.g. ``"S10010"``)."""

    key: str
    x: int
    y: int


@dataclass(frozen=True)
class FSWSignAST:
    box_symbol: str
    box_x: int
    box_y: int
    symbols: tuple[FSWSymbolNode, ...]


def parse_fsw_to_ast(fsw: str) -> FSWSignAST:
    """Parse a full FSW sign string via the real ``signwriting`` library
    and return it as this project's ``FSWSignAST``."""
    sign = fsw_to_sign(fsw)
    box_x, box_y = sign["box"]["position"]
    return FSWSignAST(
        box_symbol=sign["box"]["symbol"],
        box_x=box_x,
        box_y=box_y,
        symbols=tuple(
            FSWSymbolNode(key=entry["symbol"], x=entry["position"][0], y=entry["position"][1])
            for entry in sign["symbols"]
        ),
    )
