"""Dedicated D1-D7 tests for this task's brief ("Sửa symbol_id dùng symidArr
chuẩn") -- ``data/iswa_symbol_ids.json`` (``scripts/gen_symbol_ids.py``) and
the ``variation_of()``/``base_symbol_id_of()``/``symbol_id_of()`` trio in
``core/iswa_data.py`` it backs.

D2 (the 10 milestone cases) is also covered inline in ``test_iswa_structure.py``'s
``test_symbol_id_of_matches_display_format`` -- reproduced here too as an
explicit ``@pytest.mark.parametrize`` so each milestone reports as its own
test case, matching the brief's own D2 table.

D6 ("regeneration script byte-identical on rerun") and D7 ("1,481 old tests
pass") are NOT pytest tests in this file, deliberately: D6 needs ``npm pack``
network access, which would make the whole suite non-offline-runnable (the
same reasoning ``eval_anatomical.py`` already documents for why it needs no
fetch step) -- it was verified by hand this session (two separate runs of
``scripts/gen_symbol_ids.py``, diffed byte-for-byte identical) and is recorded
in PROGRESS.md, not re-checked on every ``pytest`` run. D7 is a property of
the whole suite (it *is* "pytest is green"), not a thing a single test inside
the suite can assert about itself.
"""

from __future__ import annotations

import pytest

from fsw_r.core.iswa_data import (
    GROUP_START,
    ISWA_LAST_BASE,
    _load_symbol_id_table,
    base_symbol_id_of,
    category_of,
    symbol_id_of,
    variation_of,
)

# D2 -- same 10 milestones as test_iswa_structure.py's
# test_symbol_id_of_matches_display_format, spanning every category boundary
# plus the two multi-variation cases (0x216/0x217) the old GROUP_START-based
# formula got wrong.
D2_MILESTONES = [
    (0x100, "01-01-001-01"),
    (0x14D, "01-05-002-01"),
    (0x216, "02-02-001-01"),
    (0x217, "02-02-001-02"),
    (0x218, "02-02-002-01"),
    (0x22A, "02-03-001-01"),
    (0x2F7, "03-01-001-01"),
    (0x36D, "05-01-001-01"),
    (0x387, "07-01-001-01"),
    (0x38B, "07-01-003-01"),
]


def test_d1_table_has_exactly_652_entries_with_continuous_keys() -> None:
    table = _load_symbol_id_table()
    assert len(table) == 652
    assert sorted(table.keys()) == list(range(0x100, 0x38C))
    assert min(table) == GROUP_START[0] == 0x100
    assert max(table) == ISWA_LAST_BASE == 0x38B


@pytest.mark.parametrize("base_hex,expected_symbol_id", D2_MILESTONES)
def test_d2_milestones(base_hex: int, expected_symbol_id: str) -> None:
    assert symbol_id_of(base_hex) == expected_symbol_id
    # base_symbol_id_of() is the same string minus the trailing "-variation".
    assert expected_symbol_id == f"{base_symbol_id_of(base_hex)}-{variation_of(base_hex):02d}"


def test_d3_unique_base_symbols_and_multi_variation_count() -> None:
    table = _load_symbol_id_table()
    assert len(table) == 652

    base_symbol_ids = {base_symbol_id_of(base_hex) for base_hex in table}
    assert len(base_symbol_ids) == 469

    variation_counts: dict[str, int] = {}
    for base_hex in table:
        key = base_symbol_id_of(base_hex)
        variation_counts[key] = variation_counts.get(key, 0) + 1
    multi_variation = sum(1 for count in variation_counts.values() if count > 1)
    # Independently measured from the real symidArr, not assumed: 94, not the
    # brief's stated 95 -- see gen_symbol_ids.py's EXPECTED_MULTI_VARIATION_BASES
    # and PROGRESS.md's entry for this task for the honest discrepancy note.
    assert multi_variation == 94


def test_d4_category_of_agrees_with_symid_arr_for_all_652_bases() -> None:
    # If this ever fails, GROUP_START's category boundaries themselves are
    # wrong -- a bigger, out-of-scope problem than this task fixes. The brief
    # says to stop and report rather than silently patch around it.
    table = _load_symbol_id_table()
    mismatches = []
    for base_hex in table:
        expected_category = int(symbol_id_of(base_hex).split("-")[0])
        actual_category = category_of(base_hex)
        if expected_category != actual_category:
            mismatches.append((base_hex, expected_category, actual_category))
    assert mismatches == []


def test_d5_group_of_and_movement_paths_are_unaffected() -> None:
    # group_of() stays the framework-internal GLOBAL numbering (1-30) -- this
    # task does not touch GROUP_START or group_of() at all. Spot check a few
    # values that movement_paths.py/finger_articulation.py depend on, plus
    # confirm those tables still resolve real entries.
    from fsw_r.core.iswa_data import group_of
    from fsw_r.core.pose_table import MOVEMENT_PATH_TABLE

    assert group_of(0x100) == 1  # Category 1, group 1 (global == per-category here)
    assert group_of(0x205) == 11  # Category 2, group 11 globally == ISWA's group 1 (see symbol_id_of)
    assert symbol_id_of(0x205).split("-")[1] == "01"  # ISWA's own per-category group for the same base

    # group 12 (global) = Finger Movement, per the module docstring's example.
    assert any(group_of(base_hex) == 12 for base_hex in MOVEMENT_PATH_TABLE.base_hexes())


def test_variation_of_is_1_for_every_category_1_base_symbol() -> None:
    # Verified fact (not assumed) this task's investigation relied on: every
    # Category 1 (Hands) base has exactly one ISWA variation.
    for base_hex in range(GROUP_START[0], GROUP_START[10]):  # GROUP_START[10] = start of Category 2
        assert variation_of(base_hex) == 1
