"""Coverage manifest for ISWA Category 4 (Head & Face).

The "Phase 4 complete" guarantee (choice B): EVERY one of the 110 Category-4
base symbols BUILDS -- never a crash, wrong type, or un-decided base -- and
is exactly one of three kinds:
  * ``FaceSymbol``: an ARKit-52 blend-shape expression (mouth/brow/eye/cheek/
    nose/tongue) or a rotation-driven eyegaze -- a real, modelled pose.
  * ``HeadSymbol``: a rigid 3D head orientation (the head-direction bases).
  * ``AnnotationSymbol``: a labelled marker with no modelled pose -- the
    honest home for non-facial marks (teeth/ears/hair/neck/airflow), facial
    *movements*, and angled "dreamy" brows (see ``annotation_symbol.py``).
New modelling flips a base from AnnotationSymbol to a real class (as eyegaze
and head did) and the counts below move together -- so this test also pins
the split.
"""

from __future__ import annotations

import pytest

from fsw_r.core.annotation_symbol import AnnotationSymbol
from fsw_r.core.face_pose_table import EXPECTED_FACE_SYMBOL_COUNT
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.head_symbol import HEAD_ORIENTATION_BASES, HeadSymbol
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
def test_every_base_builds_as_face_head_or_annotation(base_hex: int) -> None:
    symbol = symbol_from_fsw(_first_valid_key(base_hex))
    assert isinstance(symbol, (FaceSymbol, HeadSymbol, AnnotationSymbol))


def test_type_split_is_pinned() -> None:
    face = head = annotation = 0
    for base_hex in _CATEGORY_4_BASES:
        symbol = symbol_from_fsw(_first_valid_key(base_hex))
        if isinstance(symbol, FaceSymbol):
            face += 1
        elif isinstance(symbol, HeadSymbol):
            head += 1
        elif isinstance(symbol, AnnotationSymbol):
            annotation += 1
    assert face == EXPECTED_FACE_SYMBOL_COUNT
    assert head == len(HEAD_ORIENTATION_BASES)  # 5 head-orientation bases
    assert face + head + annotation == 110  # every base decided, none left out
