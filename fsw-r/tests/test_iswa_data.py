from __future__ import annotations

import pytest

from fsw_r.core.iswa_data import is_valid_symbol, valid_combinations_for
from fsw_r.groups.group_05_five_fingers import BaseSymbol01_05_002_FiveFingersSpreadHeel

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
    with pytest.raises(ValueError):
        BaseSymbol01_05_002_FiveFingersSpreadHeel(fill=0, rotation=0)


def test_fsw_base_symbol_accepts_the_one_valid_fill() -> None:
    symbol = BaseSymbol01_05_002_FiveFingersSpreadHeel(fill=1, rotation=0)
    assert symbol.fill == 1


def test_every_category_1_base_symbol_constructible_with_its_own_first_valid_fill() -> None:
    import fsw_r.groups.group_01_index_finger  # noqa: F401
    import fsw_r.groups.group_02_index_middle_fingers  # noqa: F401
    import fsw_r.groups.group_03_index_middle_thumb  # noqa: F401
    import fsw_r.groups.group_04_four_fingers  # noqa: F401
    import fsw_r.groups.group_05_five_fingers  # noqa: F401
    import fsw_r.groups.group_06_baby_finger  # noqa: F401
    import fsw_r.groups.group_07_ring_finger  # noqa: F401
    import fsw_r.groups.group_08_middle_finger  # noqa: F401
    import fsw_r.groups.group_09_index_thumb  # noqa: F401
    import fsw_r.groups.group_10_thumb  # noqa: F401
    from fsw_r.core.iswa_data import HAND_GROUP_START
    from fsw_r.core.registry import build_symbol
    from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol

    group_sizes = [14, 16, 38, 8, 58, 30, 22, 19, 40, 16]
    for group, size in enumerate(group_sizes, start=1):
        for base_symbol_number in range(1, size + 1):
            base_hex = HAND_GROUP_START[group - 1] + (base_symbol_number - 1)
            first_valid_fill = min(valid_combinations_for(base_hex).fills)
            parsed = ParsedFSWSymbol(
                category=1,
                group=group,
                base_symbol_number=base_symbol_number,
                fill=first_valid_fill,
                rotation=0,
            )
            symbol = build_symbol(parsed)
            assert symbol.fill == first_valid_fill
