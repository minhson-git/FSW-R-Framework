from __future__ import annotations

import pytest

# Importing this populates the registry (see core/registry.py docstring).
import fsw_r.groups.group_01_index_finger  # noqa: F401
from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol
from fsw_r.core.registry import build_symbol, symbol_from_fsw
from fsw_r.core.types import HandSide
from fsw_r.groups.group_01_index_finger import (
    BaseSymbol01_01_001_Index,
    BaseSymbol01_01_007_IndexBent,
)


def test_symbol_from_fsw_builds_index() -> None:
    symbol = symbol_from_fsw("S10012")
    assert isinstance(symbol, BaseSymbol01_01_001_Index)
    assert symbol.fill == 1
    assert symbol.rotation == 2
    assert symbol.symbol_id == "01-01-001"
    assert symbol.hand_side == HandSide.RIGHT


def test_symbol_from_fsw_builds_index_bent() -> None:
    symbol = symbol_from_fsw("S1061a")
    assert isinstance(symbol, BaseSymbol01_01_007_IndexBent)
    assert symbol.fill == 1
    assert symbol.rotation == 10
    assert symbol.symbol_id == "01-01-007"
    assert symbol.hand_side == HandSide.LEFT


def test_symbol_from_fsw_matches_direct_construction() -> None:
    from_key = symbol_from_fsw("S10014")
    direct = BaseSymbol01_01_001_Index(fill=1, rotation=4)
    assert from_key.get_joint_pose() == direct.get_joint_pose()
    assert from_key.get_wrist_orientation().as_quat() == pytest.approx(
        direct.get_wrist_orientation().as_quat()
    )


def test_build_symbol_raises_for_unregistered_base_symbol() -> None:
    # All 261 Category-1 base symbols are registered now, so there's no
    # valid-range Hands FSW key left to exercise this path through a real
    # key string -- build a synthetic ParsedFSWSymbol instead, targeting a
    # (group, base_symbol_number) pair that doesn't exist in any group.
    parsed = ParsedFSWSymbol(category=1, group=1, base_symbol_number=99, fill=1, rotation=0)
    with pytest.raises(ValueError):
        build_symbol(parsed)


def test_symbol_from_fsw_raises_for_malformed_key() -> None:
    with pytest.raises(ValueError):
        symbol_from_fsw("not-a-key")
