from __future__ import annotations

import pytest

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.registry import build_symbol, symbol_from_fsw
from fsw_r.core.types import HandSide


def test_symbol_from_fsw_builds_index() -> None:
    symbol = symbol_from_fsw("S10012")
    assert isinstance(symbol, HandSymbol)
    assert symbol.symbol_id == "01-01-001"
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.hand_side == HandSide.RIGHT


def test_symbol_from_fsw_builds_index_bent() -> None:
    symbol = symbol_from_fsw("S1061a")
    assert isinstance(symbol, HandSymbol)
    assert symbol.symbol_id == "01-01-007"
    assert symbol.fill == 1
    assert symbol.rotation == 10
    assert symbol.hand_side == HandSide.LEFT


def test_symbol_from_fsw_matches_direct_construction() -> None:
    from_key = symbol_from_fsw("S10014")
    direct = HandSymbol(base_hex=0x100, fill=1, rotation=4)
    assert isinstance(from_key, HandSymbol)
    assert from_key.get_joint_pose() == direct.get_joint_pose()
    assert from_key.get_wrist_orientation().as_quat() == pytest.approx(
        direct.get_wrist_orientation().as_quat()
    )


def test_build_symbol_raises_for_unsupported_category() -> None:
    # 0x37f is a real ISWA base (Category 6, Location) -- parses fine, but
    # _CATEGORY_SYMBOL has no entry for category 6 yet (1, 2, 3, 4, 5 do --
    # this test's target base has moved as coverage grew: it used to point
    # at Category 2, then Category 3, both since gained real support; see
    # PROGRESS.md's Category 3/5 entry).
    parsed = ParsedFSWSymbol(base_hex=0x37F, fill=0, rotation=0)
    with pytest.raises(ValueError):
        build_symbol(parsed)


def test_symbol_from_fsw_raises_for_malformed_key() -> None:
    with pytest.raises(ValueError):
        symbol_from_fsw("not-a-key")
