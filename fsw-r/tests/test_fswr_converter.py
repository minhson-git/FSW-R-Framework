from __future__ import annotations

import pytest

from fsw_r.core import fswr_converter
from fsw_r.core.fsw_ast import FSWSignAST, FSWSymbolNode, parse_fsw_to_ast
from fsw_r.core.fswr_converter import ast_to_fswr, fsw_to_fswr
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.types import HandSide


def test_fsw_to_fswr_converts_two_handed_sign() -> None:
    positioned_symbols = fsw_to_fswr("M500x500S10010480x480S1061a520x520")

    assert len(positioned_symbols) == 2

    first, second = positioned_symbols
    assert isinstance(first.symbol, HandSymbol)
    assert first.symbol.symbol_id == "01-01-001"
    assert (first.x, first.y) == (480, 480)
    assert first.symbol.hand_side == HandSide.RIGHT

    assert isinstance(second.symbol, HandSymbol)
    assert second.symbol.symbol_id == "01-01-007"
    assert (second.x, second.y) == (520, 520)
    assert second.symbol.hand_side == HandSide.LEFT


def test_ast_to_fswr_matches_fsw_to_fswr() -> None:
    # FSWRenderableSymbol instances aren't value-comparable, so compare the
    # fields that matter instead of the PositionedSymbol tuples directly.
    fsw = "M500x500S10011480x480"
    from_ast = ast_to_fswr(parse_fsw_to_ast(fsw))
    from_fsw = fsw_to_fswr(fsw)

    assert len(from_ast) == len(from_fsw) == 1
    assert from_ast[0].x == from_fsw[0].x
    assert from_ast[0].y == from_fsw[0].y
    assert from_ast[0].symbol.symbol_id == from_fsw[0].symbol.symbol_id
    ast_symbol, fsw_symbol = from_ast[0].symbol, from_fsw[0].symbol
    assert isinstance(ast_symbol, HandSymbol)
    assert isinstance(fsw_symbol, HandSymbol)
    assert ast_symbol.get_joint_pose() == fsw_symbol.get_joint_pose()


def test_fsw_to_fswr_empty_sign_returns_empty_tuple() -> None:
    assert fsw_to_fswr("M500x500") == ()


def test_ast_to_fswr_raises_for_unregistered_base_symbol(monkeypatch: pytest.MonkeyPatch) -> None:
    # All 261 Category-1 base symbols are covered by HAND_POSE_TABLE, so
    # there's no valid-range Hands FSW key left that ``parse_fsw_symbol_key``
    # will accept and ``build_symbol`` will still reject -- exercise the
    # propagation of build_symbol's ValueError directly instead.
    def _always_unregistered(*_args: object, **_kwargs: object) -> object:
        raise ValueError("no base symbol class registered for group=1, base_symbol_number=99")

    monkeypatch.setattr(fswr_converter, "build_symbol", _always_unregistered)
    ast = FSWSignAST(
        box_symbol="M",
        box_x=500,
        box_y=500,
        symbols=(FSWSymbolNode(key="S10010", x=480, y=480),),
    )
    with pytest.raises(ValueError):
        ast_to_fswr(ast)
