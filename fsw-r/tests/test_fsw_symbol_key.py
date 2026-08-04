from __future__ import annotations

import pytest

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol, parse_fsw_symbol_key


def test_parses_index_base_symbol() -> None:
    assert parse_fsw_symbol_key("S10011") == ParsedFSWSymbol(base_hex=0x100, fill=1, rotation=1)


def test_parses_index_bent_base_symbol() -> None:
    # 0x106 = 0x100 + 6 -> group 1, base_symbol_number 7 ("Index Bent").
    parsed = parse_fsw_symbol_key("S1061a")
    assert parsed == ParsedFSWSymbol(base_hex=0x106, fill=1, rotation=10)
    assert parsed.group == 1
    assert parsed.base_symbol_number == 7


def test_parses_last_symbol_of_group_1() -> None:
    # 0x10d = 0x100 + 13 -> group 1, base_symbol_number 14 (last of the group).
    parsed = parse_fsw_symbol_key("S10d00")
    assert parsed == ParsedFSWSymbol(base_hex=0x10D, fill=0, rotation=0)
    assert parsed.group == 1
    assert parsed.base_symbol_number == 14


def test_parses_first_symbol_of_group_2() -> None:
    # 0x10e is the first base code of group 2.
    parsed = parse_fsw_symbol_key("S10e00")
    assert parsed.group == 2
    assert parsed.base_symbol_number == 1


def test_hex_rotation_digits_parsed_as_hex() -> None:
    assert parse_fsw_symbol_key("S1001f").rotation == 15


def test_parses_keys_outside_category_1_too() -> None:
    """The parser only knows the FSW key grammar and the full ISWA range
    (0x100-0x38b) -- it does NOT block by category. Whether a category is
    actually supported is registry.py's concern (build_symbol() raises
    there), not the parser's -- see fsw_symbol_key.py's module docstring."""
    parsed = parse_fsw_symbol_key("S2f700")  # Category 3, Dynamics
    assert parsed.base_hex == 0x2F7
    assert parsed.category == 3

    parsed_movement = parse_fsw_symbol_key("S22b03")
    assert parsed_movement.base_hex == 0x22B
    assert parsed_movement.category == 2


@pytest.mark.parametrize(
    "invalid_key",
    [
        "10011",  # missing leading S
        "S1001",  # too short
        "S100111",  # too long
        "S10061",  # fill digit 6 is out of range (0-5)
        "S0ff00",  # base just below the full ISWA range (0x100-0x38b)
        "S38c00",  # base just above the full ISWA range
        "not-a-key",
    ],
)
def test_rejects_invalid_keys(invalid_key: str) -> None:
    with pytest.raises(ValueError):
        parse_fsw_symbol_key(invalid_key)
