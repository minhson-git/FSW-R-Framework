from __future__ import annotations

import pytest

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.registry import _CATEGORY_SYMBOL, build_symbol, symbol_from_fsw
from fsw_r.core.types import HandSide


def test_category_symbol_covers_all_seven_iswa_categories() -> None:
    # Was {1, 2, 3, 4, 5} while Location and Punctuation were unimplemented.
    # Both now dispatch to AnnotationSymbol -- identity carried, no modelled
    # pose, which is the accurate answer for them rather than a placeholder
    # (see _CATEGORY_SYMBOL's own comment and
    # tests/test_category6_7_coverage.py).
    assert set(_CATEGORY_SYMBOL) == {1, 2, 3, 4, 5, 6, 7}


def test_symbol_from_fsw_builds_index() -> None:
    symbol = symbol_from_fsw("S10012")
    assert isinstance(symbol, HandSymbol)
    # "-01": Index (0x100) has exactly one ISWA variation -- see
    # PROGRESS.md's "Sửa symbol_id dùng symidArr chuẩn" entry.
    assert symbol.symbol_id == "01-01-001-01"
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.hand_side == HandSide.RIGHT


def test_symbol_from_fsw_builds_index_bent() -> None:
    symbol = symbol_from_fsw("S1061a")
    assert isinstance(symbol, HandSymbol)
    assert symbol.symbol_id == "01-01-007-01"
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


def test_build_symbol_raises_for_unsupported_category(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # This test's target base kept moving as coverage grew -- Category 2,
    # then 3, then 6 -- and has now run out of places to move: all seven
    # categories dispatch, so no real ISWA base can reach the guard. Rather
    # than delete the test (the guard is the thing stopping a future partial
    # category from silently building the wrong symbol type), exercise the
    # mechanism directly by removing an entry, the same approach
    # test_fswr_converter.py already uses to reach an unreachable error path.
    monkeypatch.delitem(_CATEGORY_SYMBOL, 6)
    parsed = ParsedFSWSymbol(base_hex=0x37F, fill=0, rotation=0)  # Location
    with pytest.raises(ValueError, match="Category 6 is not supported yet"):
        build_symbol(parsed)


def test_build_symbol_covers_every_real_iswa_base() -> None:
    # The complement of the test above: with the dispatch intact, there is
    # no real base symbol left that raises.
    from fsw_r.core.iswa_data import CATEGORY_START, ISWA_LAST_BASE, valid_combinations_for

    for base_hex in range(CATEGORY_START[0], ISWA_LAST_BASE + 1):
        try:
            combos = valid_combinations_for(base_hex)
        except ValueError:
            continue  # not a real ISWA base symbol
        build_symbol(
            ParsedFSWSymbol(
                base_hex=base_hex,
                fill=min(combos.fills),
                rotation=min(combos.rotations),
            )
        )


def test_symbol_from_fsw_raises_for_malformed_key() -> None:
    with pytest.raises(ValueError):
        symbol_from_fsw("not-a-key")
