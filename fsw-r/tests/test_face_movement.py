"""Pins the facial-movement temporal model (see face_movement.py): what each
movement animates, and that its blend-shapes stay valid ARKit-52 targets in
range across time."""

from __future__ import annotations

import pytest

from fsw_r.core.face_movement import FACE_MOVEMENT_BASES, FaceMovementSymbol
from fsw_r.core.face_types import ARKIT_BLENDSHAPES
from fsw_r.core.registry import symbol_from_fsw

_TS = [0.0, 0.25, 0.5, 0.75, 1.0]


@pytest.mark.parametrize("base_hex", sorted(FACE_MOVEMENT_BASES))
def test_symbol_from_fsw_builds_face_movement(base_hex: int) -> None:
    symbol = symbol_from_fsw(f"S{base_hex:03x}00")
    assert isinstance(symbol, FaceMovementSymbol)
    assert symbol.hand_side is None


@pytest.mark.parametrize("base_hex", sorted(FACE_MOVEMENT_BASES))
def test_expression_over_time_stays_valid(base_hex: int) -> None:
    symbol = FaceMovementSymbol(base_hex, fill=0, rotation=0)
    for t in _TS:
        weights = symbol.expression_at(t).blendshapes
        assert set(weights) <= ARKIT_BLENDSHAPES
        assert all(0.0 <= w <= 1.0 for w in weights.values())


def test_blink_closes_then_opens() -> None:
    blink = FaceMovementSymbol(0x317, fill=0, rotation=0)  # Eye Blink Single
    start = blink.expression_at(0.0).blendshapes.get("eyeBlinkLeft", 0.0)
    mid = blink.expression_at(0.5).blendshapes.get("eyeBlinkLeft", 0.0)
    end = blink.expression_at(1.0).blendshapes.get("eyeBlinkLeft", 0.0)
    assert start < 0.2 and end < 0.2 and mid > 0.8  # open -> closed -> open


def test_jaw_movement_opens_mid_motion() -> None:
    jaw = FaceMovementSymbol(0x368, fill=0, rotation=0)  # Jaw Movement Wall Plane
    assert jaw.expression_at(0.5).blendshapes.get("jawOpen", 0.0) > 0.3


def test_get_expression_returns_the_peak_frame() -> None:
    blink = FaceMovementSymbol(0x317, fill=0, rotation=0)
    assert blink.get_expression().blendshapes == blink.expression_at(0.5).blendshapes
