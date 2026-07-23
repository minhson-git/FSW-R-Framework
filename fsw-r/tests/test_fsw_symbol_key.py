from __future__ import annotations

import pytest

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol, parse_fsw_symbol_key


def test_parses_index_base_symbol() -> None:
    assert parse_fsw_symbol_key("S10011") == ParsedFSWSymbol(
        category=1, group=1, base_symbol_number=1, fill=1, rotation=1
    )


def test_parses_index_bent_base_symbol() -> None:
    # 0x106 = 0x100 + 6 -> group 1, base_symbol_number 7 ("Index Bent").
    assert parse_fsw_symbol_key("S1061a") == ParsedFSWSymbol(
        category=1, group=1, base_symbol_number=7, fill=1, rotation=10
    )


def test_parses_last_symbol_of_group_1() -> None:
    # 0x10d = 0x100 + 13 -> group 1, base_symbol_number 14 (last of the group).
    assert parse_fsw_symbol_key("S10d00") == ParsedFSWSymbol(
        category=1, group=1, base_symbol_number=14, fill=0, rotation=0
    )


def test_parses_first_symbol_of_group_2() -> None:
    # 0x10e is the first base code of group 2.
    parsed = parse_fsw_symbol_key("S10e00")
    assert parsed.group == 2
    assert parsed.base_symbol_number == 1


def test_hex_rotation_digits_parsed_as_hex() -> None:
    assert parse_fsw_symbol_key("S1001f").rotation == 15


@pytest.mark.parametrize(
    "invalid_key",
    [
        "10011",  # missing leading S
        "S1001",  # too short
        "S100111",  # too long
        "S10061",  # fill digit 6 is out of range (0-5)
        "S2f700",  # outside the Hands range (0x100-0x204) -- e.g. a "face" symbol
        "not-a-key",
    ],
)
def test_rejects_invalid_keys(invalid_key: str) -> None:
    with pytest.raises(ValueError):
        parse_fsw_symbol_key(invalid_key)
