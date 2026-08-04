from __future__ import annotations

import pytest

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.iswa_data import HAND_GROUP_START, is_valid_symbol, valid_combinations_for
from fsw_r.core.registry import build_symbol

# The 8 Category 1 (Hands) base symbols that do NOT have all 6 fills x 16
# rotations -- independently verified against the real ISWA font (see
# scripts/gen_valid_combinations.py's EXPECTED_CAT1_EXCEPTIONS).
CAT1_EXCEPTIONS = {
    0x14D: [1],
    0x14F: [1],
    0x151: [1],
    0x15B: [0, 1, 2, 3],
    0x15C: [1],
    0x15E: [1],
    0x1F6: [1],
    0x204: [1],
}

GROUP_SIZES = [14, 16, 38, 8, 58, 30, 22, 19, 40, 16]


def test_table_has_652_base_symbols_and_37811_total_combinations() -> None:
    total_bases = 0
    total_symbols = 0
    for base in range(0x100, 0x38C):
        try:
            combos = valid_combinations_for(base)
        except ValueError:
            continue
        total_bases += 1
        total_symbols += len(combos.fills) * len(combos.rotations)

    assert total_bases == 652
    assert total_symbols == 37811


@pytest.mark.parametrize("base_hex,expected_fills", sorted(CAT1_EXCEPTIONS.items()))
def test_category_1_exceptions_have_restricted_fills(base_hex: int, expected_fills: list[int]) -> None:
    combos = valid_combinations_for(base_hex)
    assert sorted(combos.fills) == expected_fills
    assert sorted(combos.rotations) == list(range(16))


def test_valid_combinations_for_raises_for_base_outside_iswa_range() -> None:
    with pytest.raises(ValueError):
        valid_combinations_for(0x0)


def test_is_valid_symbol_true_and_false_cases() -> None:
    assert is_valid_symbol(0x100, fill=0, rotation=0) is True
    assert is_valid_symbol(0x14D, fill=1, rotation=0) is True
    assert is_valid_symbol(0x14D, fill=0, rotation=0) is False


def test_fsw_base_symbol_raises_for_invalid_fill() -> None:
    # 01-05-002 (base 0x14d) only has fill=1 in real ISWA.
    with pytest.raises(ValueError):
        HandSymbol(base_hex=0x14D, fill=0, rotation=0)


def test_fsw_base_symbol_accepts_the_one_valid_fill() -> None:
    symbol = HandSymbol(base_hex=0x14D, fill=1, rotation=0)
    assert symbol.fill == 1


def test_every_category_1_base_symbol_constructible_with_its_own_first_valid_fill() -> None:
    for group, size in enumerate(GROUP_SIZES, start=1):
        for base_symbol_number in range(1, size + 1):
            base_hex = HAND_GROUP_START[group - 1] + (base_symbol_number - 1)
            first_valid_fill = min(valid_combinations_for(base_hex).fills)
            parsed = ParsedFSWSymbol(base_hex=base_hex, fill=first_valid_fill, rotation=0)
            symbol = build_symbol(parsed)
            assert symbol.fill == first_valid_fill
