from __future__ import annotations

import pytest

from fsw_r.core.annotation_symbol import AnnotationSymbol
from fsw_r.core.face_pose_table import EXPECTED_FACE_SYMBOL_COUNT, FACE_NAME_TABLE, FACE_POSE_TABLE
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.face_types import ARKIT_BLENDSHAPES
from fsw_r.core.iswa_data import category_of, group_of, symbol_id_of
from fsw_r.core.registry import symbol_from_fsw

# Every authored facial base symbol, as (base_hex, fill=0) FSW keys.
_FACE_BASES = sorted(FACE_POSE_TABLE.base_hexes())


def test_table_has_expected_count() -> None:
    assert len(_FACE_BASES) == EXPECTED_FACE_SYMBOL_COUNT


@pytest.mark.parametrize("base_hex", _FACE_BASES)
def test_every_authored_base_is_category4_face(base_hex: int) -> None:
    # All authored bases are Category 4, facial-expression groups (24-26 so far).
    assert category_of(base_hex) == 4
    assert group_of(base_hex) in {23, 24, 25, 26}


@pytest.mark.parametrize("base_hex", _FACE_BASES)
def test_symbol_from_fsw_builds_face_symbol(base_hex: int) -> None:
    key = f"S{base_hex:03x}00"  # fill 0, rotation 0
    symbol = symbol_from_fsw(key)
    assert isinstance(symbol, FaceSymbol)
    assert symbol.symbol_id == symbol_id_of(base_hex)
    assert symbol.name == FACE_NAME_TABLE[base_hex]
    assert symbol.hand_side is None  # a face doesn't encode a performing hand


@pytest.mark.parametrize("base_hex", _FACE_BASES)
def test_expression_uses_only_arkit_names(base_hex: int) -> None:
    symbol = symbol_from_fsw(f"S{base_hex:03x}00")
    assert isinstance(symbol, FaceSymbol)
    assert set(symbol.get_expression().blendshapes) <= ARKIT_BLENDSHAPES


def test_both_fills_are_authored_for_mouth() -> None:
    # ISWA mouth symbols are valid at fill 0 and fill 1; both must build and
    # return an expression (currently identical -- fill nuance unresolved,
    # see the data file's _meta).
    fill0 = symbol_from_fsw("S33e00")  # Mouth Smile, fill 0
    fill1 = symbol_from_fsw("S33e10")  # Mouth Smile, fill 1
    assert isinstance(fill0, FaceSymbol) and isinstance(fill1, FaceSymbol)
    assert fill0.get_expression().blendshapes == fill1.get_expression().blendshapes


def test_known_symbol_expression_is_meaningful() -> None:
    # A concrete pin so a silent data corruption is caught: Mouth Smile must
    # drive the two smile blend-shapes and nothing wildly off.
    smile = symbol_from_fsw("S33e00")
    assert isinstance(smile, FaceSymbol)
    weights = smile.get_expression().blendshapes
    assert weights["mouthSmileLeft"] > 0.5
    assert weights["mouthSmileRight"] > 0.5


def test_unmodelled_category4_bases_build_as_annotation() -> None:
    # Bases with no modelled pose build as AnnotationSymbol (marker): 0x356
    # Mouth Corners (annotation mark), 0x330 Ears / 0x335 Air Blowing Out,
    # 0x361 Teeth / 0x36a Neck (non-facial), 0x320 Eyelashes Fluttering /
    # 0x362 Teeth Movement (movements with no ARKit target), 0x30d Dreamy brow.
    for key in ("S35600", "S33000", "S33500", "S36100", "S36a00", "S32000", "S36200", "S30d00"):
        symbol = symbol_from_fsw(key)
        assert isinstance(symbol, AnnotationSymbol)
        assert not isinstance(symbol, FaceSymbol)
