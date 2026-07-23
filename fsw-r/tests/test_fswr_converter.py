from __future__ import annotations

import pytest

# Importing this populates the registry (see core/registry.py docstring).
import fsw_r.groups.group_01_index_finger  # noqa: F401
from fsw_r.core.fsw_ast import parse_fsw_to_ast
from fsw_r.core.fswr_converter import ast_to_fswr, fsw_to_fswr
from fsw_r.core.types import HandSide
from fsw_r.groups.group_01_index_finger import (
    BaseSymbol01_01_001_Index,
    BaseSymbol01_01_007_IndexBent,
)


def test_fsw_to_fswr_converts_two_handed_sign() -> None:
    positioned_symbols = fsw_to_fswr("M500x500S10010480x480S1061a520x520")

    assert len(positioned_symbols) == 2

    first, second = positioned_symbols
    assert isinstance(first.symbol, BaseSymbol01_01_001_Index)
    assert (first.x, first.y) == (480, 480)
    assert first.symbol.hand_side == HandSide.RIGHT

    assert isinstance(second.symbol, BaseSymbol01_01_007_IndexBent)
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
    assert from_ast[0].symbol.get_joint_pose() == from_fsw[0].symbol.get_joint_pose()


def test_fsw_to_fswr_empty_sign_returns_empty_tuple() -> None:
    assert fsw_to_fswr("M500x500") == ()


def test_fsw_to_fswr_raises_for_unregistered_base_symbol() -> None:
    # 0x101 = base_symbol_number 2 ("Index on Circle") -- not implemented/registered.
    with pytest.raises(ValueError):
        fsw_to_fswr("M500x500S10110480x480")
