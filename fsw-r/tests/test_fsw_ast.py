from __future__ import annotations

from fsw_r.core.fsw_ast import FSWSignAST, FSWSymbolNode, parse_fsw_to_ast


def test_parses_box_and_single_symbol() -> None:
    ast = parse_fsw_to_ast("M500x500S10011480x480")
    assert ast == FSWSignAST(
        box_symbol="M",
        box_x=500,
        box_y=500,
        symbols=(FSWSymbolNode(key="S10011", x=480, y=480),),
    )


def test_parses_two_symbol_sign() -> None:
    ast = parse_fsw_to_ast("M500x500S10010480x480S1061a520x520")
    assert ast.symbols == (
        FSWSymbolNode(key="S10010", x=480, y=480),
        FSWSymbolNode(key="S1061a", x=520, y=520),
    )


def test_parses_sign_with_no_symbols() -> None:
    ast = parse_fsw_to_ast("M500x500")
    assert ast.symbols == ()
