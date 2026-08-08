"""Coverage manifest for ISWA Category 4 (Head & Face).

The "Phase 4 done for its scope" guarantee: EVERY one of the 110 Category-4
base symbols is *accounted for* -- it either builds a real ``FaceSymbol``
(authored blend-shape) or raises a clear ``ValueError`` from
``symbol_from_fsw`` (deferred / not-yet-supported, with a reason). Nothing is
silently mishandled: no crash, no wrong type, no un-decided base. New
authoring flips a base from the "raises" side to the "builds" side and the
counts below move together -- so this test also pins the current split.
"""

from __future__ import annotations

import pytest

from fsw_r.core.face_pose_table import EXPECTED_FACE_SYMBOL_COUNT
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.iswa_data import CATEGORY_START, category_of, valid_combinations_for
from fsw_r.core.registry import symbol_from_fsw

# All real Category-4 base symbols: [0x2ff, 0x36d).
_CATEGORY_4_BASES = tuple(range(CATEGORY_START[3], CATEGORY_START[4]))


def _first_valid_key(base_hex: int) -> str:
    combos = valid_combinations_for(base_hex)
    return f"S{base_hex:03x}{min(combos.fills):x}{min(combos.rotations):x}"


def test_category_4_has_110_base_symbols() -> None:
    assert len(_CATEGORY_4_BASES) == 110
    assert all(category_of(b) == 4 for b in _CATEGORY_4_BASES)


@pytest.mark.parametrize("base_hex", _CATEGORY_4_BASES)
def test_every_base_is_authored_or_raises_cleanly(base_hex: int) -> None:
    key = _first_valid_key(base_hex)
    try:
        symbol = symbol_from_fsw(key)
    except ValueError:
        return  # deferred / not supported yet -- an honest, accounted-for outcome
    # Otherwise it must be a real, authored facial symbol -- never a wrong type.
    assert isinstance(symbol, FaceSymbol)


def test_authored_vs_deferred_split_is_pinned() -> None:
    built = 0
    raised = 0
    for base_hex in _CATEGORY_4_BASES:
        try:
            symbol_from_fsw(_first_valid_key(base_hex))
            built += 1
        except ValueError:
            raised += 1
    assert built == EXPECTED_FACE_SYMBOL_COUNT
    assert built + raised == 110  # every base decided one way or the other
