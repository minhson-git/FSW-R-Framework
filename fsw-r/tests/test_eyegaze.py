"""Locks the eyegaze rotation->direction convention that was verified
against the real ISWA glyph (rot 0 = up, 2 = viewer-left, 4 = down,
6 = viewer-right; counter-clockwise) -- so a later change can't silently
flip it. See core/eyegaze.py."""

from __future__ import annotations

import pytest

from fsw_r.core.eyegaze import EYEGAZE_BASES, gaze_blendshapes
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.registry import symbol_from_fsw


def test_gaze_up_at_rotation_0() -> None:
    g = gaze_blendshapes(0)
    assert g["eyeLookUpLeft"] > 0 and g["eyeLookUpRight"] > 0
    assert "eyeLookDownLeft" not in g


def test_gaze_down_at_rotation_4() -> None:
    g = gaze_blendshapes(4)
    assert g["eyeLookDownLeft"] > 0 and g["eyeLookDownRight"] > 0
    assert "eyeLookUpLeft" not in g


def test_gaze_viewer_left_at_rotation_2_is_person_right() -> None:
    # Viewer's left = the signer looking to THEIR right: left eye in, right eye out.
    g = gaze_blendshapes(2)
    assert g["eyeLookInLeft"] > 0 and g["eyeLookOutRight"] > 0
    assert "eyeLookOutLeft" not in g and "eyeLookInRight" not in g


def test_gaze_viewer_right_at_rotation_6_is_person_left() -> None:
    g = gaze_blendshapes(6)
    assert g["eyeLookOutLeft"] > 0 and g["eyeLookInRight"] > 0
    assert "eyeLookInLeft" not in g and "eyeLookOutRight" not in g


@pytest.mark.parametrize("rotation", range(8))
def test_gaze_weights_in_range(rotation: int) -> None:
    for weight in gaze_blendshapes(rotation).values():
        assert 0.0 < weight <= 1.0


def test_eyegaze_symbol_merges_gaze_into_expression() -> None:
    # 0x321 Eyegaze Straight Wall Plane at rotation 0 (up), fill 0.
    symbol = symbol_from_fsw("S32100")
    assert isinstance(symbol, FaceSymbol)
    assert symbol.base_hex in EYEGAZE_BASES
    weights = symbol.get_expression().blendshapes
    assert weights["eyeLookUpLeft"] > 0 and weights["eyeLookUpRight"] > 0


def test_eyegaze_direction_changes_with_rotation() -> None:
    up, down = symbol_from_fsw("S32100"), symbol_from_fsw("S32104")
    assert isinstance(up, FaceSymbol) and isinstance(down, FaceSymbol)
    assert up.get_expression().blendshapes != down.get_expression().blendshapes
