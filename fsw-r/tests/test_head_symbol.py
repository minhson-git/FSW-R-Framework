"""Pins the head-orientation mapping (grounded in Lessons in SignWriting
Lesson 10, numerically this project's interpretation, see head_symbol.py) so
a later change can't silently flip pitch/yaw. Checks where the nose
(face-forward, +z) points after the orientation."""

from __future__ import annotations

import numpy as np

from fsw_r.core.head_symbol import HEAD_ORIENTATION_BASES, HeadSymbol
from fsw_r.core.registry import symbol_from_fsw


def _nose(base_hex: int, rotation: int) -> np.ndarray:
    orientation = HeadSymbol(base_hex, fill=0, rotation=rotation).get_head_orientation()
    return np.asarray(orientation.apply([0.0, 0.0, 1.0]), dtype=float)


def test_static_head_is_neutral() -> None:
    assert np.allclose(HeadSymbol(0x2FF, 0, 0).get_head_orientation().as_matrix(), np.eye(3))
    assert np.allclose(HeadSymbol(0x300, 0, 0).get_head_orientation().as_matrix(), np.eye(3))


def test_nose_up_points_up() -> None:
    assert _nose(0x308, 0)[1] > 0.3  # +y


def test_nose_down_points_down() -> None:
    assert _nose(0x308, 4)[1] < -0.3  # -y


def test_nose_viewer_left_points_left() -> None:
    # rotation 2 = viewer-left; -x is the viewer's left in the display frame.
    assert _nose(0x308, 2)[0] < -0.3


def test_nose_viewer_right_points_right() -> None:
    assert _nose(0x308, 6)[0] > 0.3


def test_symbol_from_fsw_builds_head_symbol() -> None:
    for base_hex in HEAD_ORIENTATION_BASES:
        symbol = symbol_from_fsw(f"S{base_hex:03x}00")
        assert isinstance(symbol, HeadSymbol)
        assert symbol.hand_side is None
