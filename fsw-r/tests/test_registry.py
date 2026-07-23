from __future__ import annotations

import pytest

# Importing this populates the registry (see core/registry.py docstring).
import fsw_r.groups.group_01_index_finger  # noqa: F401
from fsw_r.core.registry import symbol_from_fsw
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


def test_symbol_from_fsw_raises_for_unregistered_base_symbol() -> None:
    # 0x101 = base_symbol_number 2 ("Index on Circle") -- not implemented/registered.
    with pytest.raises(ValueError):
        symbol_from_fsw("S10110")


def test_symbol_from_fsw_raises_for_malformed_key() -> None:
    with pytest.raises(ValueError):
        symbol_from_fsw("not-a-key")
