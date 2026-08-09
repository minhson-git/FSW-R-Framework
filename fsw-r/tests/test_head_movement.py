"""Pins the head-movement temporal model (see head_movement.py): each base
animates the head orientation, and the nod actually pitches the head."""

from __future__ import annotations

import numpy as np
import pytest

from fsw_r.core.head_movement import HEAD_MOVEMENT_BASES, HeadMovementSymbol
from fsw_r.core.registry import symbol_from_fsw


@pytest.mark.parametrize("base_hex", sorted(HEAD_MOVEMENT_BASES))
def test_symbol_from_fsw_builds_head_movement(base_hex: int) -> None:
    symbol = symbol_from_fsw(f"S{base_hex:03x}00")
    assert isinstance(symbol, HeadMovementSymbol)
    assert symbol.hand_side is None


@pytest.mark.parametrize("base_hex", sorted(HEAD_MOVEMENT_BASES))
def test_orientation_varies_over_time(base_hex: int) -> None:
    symbol = HeadMovementSymbol(base_hex, fill=0, rotation=0)
    a = symbol.orientation_at(0.0).as_quat()
    b = symbol.orientation_at(0.25).as_quat()
    assert not np.allclose(a, b)  # the head actually moves


def test_straight_wall_nod_pitches_the_head() -> None:
    nod = HeadMovementSymbol(0x301, fill=0, rotation=0)  # Straight Wall = nod
    # A quarter into the cycle the nose (+z) should be tilted off centre in y.
    nose = np.asarray(nod.orientation_at(0.25).apply([0.0, 0.0, 1.0]), dtype=float)
    assert abs(nose[1]) > 0.3
