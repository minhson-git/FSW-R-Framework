"""Coverage manifest for ISWA Category 6 (Location) and 7 (Punctuation) --
the last two categories, and the point at which all 652 ISWA base symbols
build.

Both categories build as ``AnnotationSymbol``: the symbol's identity is
carried, no pose is modelled. That is the accurate answer rather than a
placeholder, and the two categories reach it for different reasons, so the
tests below pin the reasons, not just the class:

  * Punctuation is writing-system notation between signs. It is never
    performed by the body, so "no modelled pose" is final, not a gap.
  * Location is a spatial anchor, and this framework positions from the
    SIGNBOX coordinates the FSW string already carries
    (``timeline/anchor.py``). Mapping an ISWA location glyph onto that space
    would need a convention no source has been found for -- so it is not
    invented.

The measured reason this matters: these 13 bases were the ONLY cause of
symbol-mapping failure across the whole SignBank+ corpus (118,251
Punctuation tokens and 367 Location tokens -- see
``reports/corpus_coverage.md``). A sign containing a full stop could not be
processed at all because of the full stop.
"""

from __future__ import annotations

import pytest

from fsw_r.core.annotation_symbol import AnnotationSymbol
from fsw_r.core.iswa_data import (
    CATEGORY_START,
    ISWA_LAST_BASE,
    category_of,
    valid_combinations_for,
)
from fsw_r.core.registry import build_symbol, symbol_from_fsw
from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol

_CATEGORY_6_BASES = tuple(range(CATEGORY_START[5], CATEGORY_START[6]))
_CATEGORY_7_BASES = tuple(range(CATEGORY_START[6], ISWA_LAST_BASE + 1))

EXPECTED_CATEGORY_6 = 8
EXPECTED_CATEGORY_7 = 5


def _first_valid_key(base_hex: int) -> str:
    combos = valid_combinations_for(base_hex)
    return f"S{base_hex:03x}{min(combos.fills):x}{min(combos.rotations):x}"


def test_category_ranges_are_the_expected_size() -> None:
    """Pins the two ranges so a GROUP_START/CATEGORY_START edit that silently
    reshapes them fails here rather than quietly changing coverage."""
    assert len(_CATEGORY_6_BASES) == EXPECTED_CATEGORY_6
    assert len(_CATEGORY_7_BASES) == EXPECTED_CATEGORY_7
    assert {category_of(b) for b in _CATEGORY_6_BASES} == {6}
    assert {category_of(b) for b in _CATEGORY_7_BASES} == {7}


@pytest.mark.parametrize("base_hex", _CATEGORY_6_BASES + _CATEGORY_7_BASES)
def test_every_base_builds_as_an_annotation_symbol(base_hex: int) -> None:
    combos = valid_combinations_for(base_hex)
    symbol = build_symbol(
        ParsedFSWSymbol(
            base_hex=base_hex, fill=min(combos.fills), rotation=min(combos.rotations)
        )
    )
    assert isinstance(symbol, AnnotationSymbol)
    assert symbol.base_hex == base_hex


@pytest.mark.parametrize("base_hex", _CATEGORY_6_BASES + _CATEGORY_7_BASES)
def test_every_base_round_trips_through_a_real_fsw_key(base_hex: int) -> None:
    """The whole point is that a real FSW string containing one of these no
    longer fails -- so go through the parser, not just the registry."""
    symbol = symbol_from_fsw(_first_valid_key(base_hex))
    assert isinstance(symbol, AnnotationSymbol)
    assert symbol.base_hex == base_hex


@pytest.mark.parametrize("base_hex", _CATEGORY_6_BASES + _CATEGORY_7_BASES)
def test_annotation_symbols_encode_no_performing_hand(base_hex: int) -> None:
    """Neither a location mark nor a punctuation mark is performed by a hand;
    claiming one would be a fabricated attribute."""
    combos = valid_combinations_for(base_hex)
    symbol = build_symbol(
        ParsedFSWSymbol(
            base_hex=base_hex, fill=min(combos.fills), rotation=min(combos.rotations)
        )
    )
    assert symbol.hand_side is None


def test_every_valid_fill_and_rotation_builds() -> None:
    """These 13 bases carry a wide fill/rotation spread (one has all 16
    rotations), and a real corpus string can use any of them -- so cover the
    whole valid space, not just the first combination."""
    built = 0
    for base_hex in _CATEGORY_6_BASES + _CATEGORY_7_BASES:
        combos = valid_combinations_for(base_hex)
        for fill in sorted(combos.fills):
            for rotation in sorted(combos.rotations):
                symbol = build_symbol(
                    ParsedFSWSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
                )
                assert isinstance(symbol, AnnotationSymbol)
                built += 1
    assert built == sum(
        len(valid_combinations_for(b).fills) * len(valid_combinations_for(b).rotations)
        for b in _CATEGORY_6_BASES + _CATEGORY_7_BASES
    )


def test_all_652_iswa_base_symbols_now_build() -> None:
    """The headline this change earns: no ISWA base symbol is unsupported.
    Asserted over the real font-derived table, not a hardcoded list."""
    unbuildable: list[int] = []
    for base_hex in range(CATEGORY_START[0], ISWA_LAST_BASE + 1):
        try:
            combos = valid_combinations_for(base_hex)
        except ValueError:
            continue  # not a real ISWA base symbol
        try:
            build_symbol(
                ParsedFSWSymbol(
                    base_hex=base_hex,
                    fill=min(combos.fills),
                    rotation=min(combos.rotations),
                )
            )
        except Exception:  # noqa: BLE001 -- any failure is a coverage hole
            unbuildable.append(base_hex)
    assert unbuildable == []
