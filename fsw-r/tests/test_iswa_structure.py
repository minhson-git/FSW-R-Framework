from __future__ import annotations

import pytest

from fsw_r.core.iswa_data import (
    CATEGORY_START,
    GROUP_START,
    ISWA_LAST_BASE,
    base_hex_of,
    base_symbol_number_of,
    category_of,
    group_of,
    symbol_id_of,
)

# (base_hex, category, group, base_symbol_number) -- the boundary cases most
# likely to be off-by-one, from Category 1's own group boundaries through
# every category boundary up to the very last ISWA base.
BOUNDARY_CASES = [
    (0x100, 1, 1, 1),
    (0x10D, 1, 1, 14),
    (0x10E, 1, 2, 1),
    (0x204, 1, 10, 16),
    (0x205, 2, 11, 1),
    (0x2F6, 2, 20, 20),
    (0x2F7, 3, 21, 1),
    (0x38B, 7, 30, 5),  # last group (30, punctuation) starts at 0x387, 5 wide
]


@pytest.mark.parametrize("base_hex,category,group,base_symbol_number", BOUNDARY_CASES)
def test_boundary_cases(base_hex: int, category: int, group: int, base_symbol_number: int) -> None:
    assert category_of(base_hex) == category
    assert group_of(base_hex) == group
    assert base_symbol_number_of(base_hex) == base_symbol_number


def test_category_start_has_7_entries() -> None:
    # Resolved discrepancy: the real fsw-structure.js `category` array has 7
    # entries (Trunk & Limb share one category), not 8 -- see iswa_data.py's
    # module docstring.
    assert len(CATEGORY_START) == 7


def test_group_start_has_30_entries() -> None:
    assert len(GROUP_START) == 30


def test_full_round_trip_across_all_652_base_symbols() -> None:
    for base_hex in range(GROUP_START[0], ISWA_LAST_BASE + 1):
        category = category_of(base_hex)
        group = group_of(base_hex)
        base_symbol_number = base_symbol_number_of(base_hex)
        assert base_hex_of(category, group, base_symbol_number) == base_hex


def test_symbol_id_of_matches_display_format() -> None:
    # D2 (this task's brief, "Sửa symbol_id dùng symidArr chuẩn") -- the
    # real ISWA Symbol ID, from data/iswa_symbol_ids.json, NOT derived from
    # GROUP_START/group_of() anymore (see symbol_id_of()'s own docstring).
    # 10 milestones spanning every category boundary plus the two
    # multi-variation cases (0x216/0x217) the old GROUP_START-based formula
    # got wrong.
    assert symbol_id_of(0x100) == "01-01-001-01"
    assert symbol_id_of(0x14D) == "01-05-002-01"
    assert symbol_id_of(0x216) == "02-02-001-01"
    assert symbol_id_of(0x217) == "02-02-001-02"
    assert symbol_id_of(0x218) == "02-02-002-01"
    assert symbol_id_of(0x22A) == "02-03-001-01"
    assert symbol_id_of(0x2F7) == "03-01-001-01"
    assert symbol_id_of(0x36D) == "05-01-001-01"
    assert symbol_id_of(0x387) == "07-01-001-01"
    assert symbol_id_of(0x38B) == "07-01-003-01"


def test_category_of_raises_outside_iswa_range() -> None:
    with pytest.raises(ValueError):
        category_of(0x0FF)
    with pytest.raises(ValueError):
        category_of(0x38C)


def test_base_hex_of_raises_for_group_category_mismatch() -> None:
    with pytest.raises(ValueError):
        base_hex_of(category=1, group=11, base_symbol_number=1)  # group 11 is Movement (cat 2)


def test_base_hex_of_raises_when_base_symbol_number_spills_into_next_group() -> None:
    with pytest.raises(ValueError):
        base_hex_of(category=1, group=1, base_symbol_number=99)  # group 1 only has 14
