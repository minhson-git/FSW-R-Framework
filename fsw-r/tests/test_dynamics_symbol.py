from __future__ import annotations

import pytest

from fsw_r.core.dynamics_symbol import DynamicsSymbol
from fsw_r.core.iswa_data import category_of, group_of, valid_combinations_for
from fsw_r.core.modifier_symbol import FSWModifierSymbol
from fsw_r.core.pose_table import DYNAMICS_MODIFIER_TABLE, EXPECTED_DYNAMICS_COUNT
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.renderable_symbol import FSWRenderableSymbol

_DYNAMICS_BASES = sorted(DYNAMICS_MODIFIER_TABLE.base_hexes())


def test_table_has_expected_count() -> None:
    assert len(_DYNAMICS_BASES) == EXPECTED_DYNAMICS_COUNT == 8


@pytest.mark.parametrize("base_hex", _DYNAMICS_BASES)
def test_every_base_is_category3_group21(base_hex: int) -> None:
    assert category_of(base_hex) == 3
    assert group_of(base_hex) == 21


@pytest.mark.parametrize("base_hex", _DYNAMICS_BASES)
def test_symbol_builds_and_get_modifier_does_not_raise(base_hex: int) -> None:
    # C2: first valid (fill, rotation) for this base, real FSW key.
    combos = valid_combinations_for(base_hex)
    fill, rotation = min(combos.fills), min(combos.rotations)
    key = f"S{base_hex:03x}{fill:x}{rotation:x}"
    symbol = symbol_from_fsw(key)
    assert isinstance(symbol, DynamicsSymbol)
    assert isinstance(symbol, FSWModifierSymbol)
    assert symbol.hand_side is None
    symbol.get_modifier()  # must not raise


def test_c4_dynamics_symbol_is_not_renderable() -> None:
    # C4: a Dynamics symbol renders nothing of its own -- it is NOT part of
    # the FSWRenderableSymbol tree at all (see core/modifier_symbol.py).
    symbol = symbol_from_fsw("S2fb00")  # Same Time
    assert isinstance(symbol, DynamicsSymbol)
    assert isinstance(symbol, FSWModifierSymbol)
    assert not isinstance(symbol, FSWRenderableSymbol)


def test_fast_and_slow_have_opposite_speed_direction() -> None:
    fast = symbol_from_fsw("S2f700")
    slow = symbol_from_fsw("S2f800")
    assert isinstance(fast, DynamicsSymbol) and isinstance(slow, DynamicsSymbol)
    assert fast.get_modifier().speed < 1.0 < slow.get_modifier().speed


def test_tense_and_relaxed_have_opposite_tension() -> None:
    tense = symbol_from_fsw("S2f900")
    relaxed = symbol_from_fsw("S2fa00")
    assert isinstance(tense, DynamicsSymbol) and isinstance(relaxed, DynamicsSymbol)
    assert tense.get_modifier().tension is True
    assert relaxed.get_modifier().tension is False


def test_same_time_alternating_family_sets_alternating() -> None:
    same_time = symbol_from_fsw("S2fb00")  # Same Time
    same_time_alt = symbol_from_fsw("S2fc00")  # Same Time Alternating
    every_other = symbol_from_fsw("S2fd00")  # Every Other Time
    assert isinstance(same_time, DynamicsSymbol)
    assert isinstance(same_time_alt, DynamicsSymbol)
    assert isinstance(every_other, DynamicsSymbol)
    assert same_time.get_modifier().alternating is False
    assert same_time_alt.get_modifier().alternating is True
    assert every_other.get_modifier().alternating is True
    assert every_other.get_modifier().repeat == 2


def test_c3_valid_combinations_reject_out_of_range_rotation() -> None:
    # 0x2f7 ("Fast") only has rotation [0] -- rotation=1 (hex digit '1')
    # must be rejected by the real ISWA valid-combinations table.
    with pytest.raises(ValueError):
        symbol_from_fsw("S2f701")
