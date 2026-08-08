from __future__ import annotations

import numpy as np

from fsw_r_viz.face_geometry import mouth_outline


def _corner_and_center_gap(blendshapes: dict[str, float]) -> tuple[float, float]:
    xs, ys = mouth_outline(blendshapes)
    n = len(xs) // 2
    upper, lower = ys[:n], ys[n:][::-1]
    corner_y = float(upper[0])  # leftmost corner (upper == lower there)
    center_gap = float(upper[n // 2] - lower[n // 2])  # vertical opening at center
    return corner_y, center_gap


def test_smile_raises_corners_above_frown() -> None:
    smile_corner, _ = _corner_and_center_gap({"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8})
    frown_corner, _ = _corner_and_center_gap({"mouthFrownLeft": 0.8, "mouthFrownRight": 0.8})
    assert smile_corner > frown_corner


def test_jaw_open_increases_vertical_gap() -> None:
    _, closed_gap = _corner_and_center_gap({})
    _, open_gap = _corner_and_center_gap({"jawOpen": 0.8})
    assert open_gap > closed_gap


def test_outline_is_closed_and_finite() -> None:
    xs, ys = mouth_outline({"mouthSmileLeft": 0.5, "jawOpen": 0.3})
    assert len(xs) == len(ys)
    assert np.all(np.isfinite(xs)) and np.all(np.isfinite(ys))
