"""Schematic 2D mouth geometry from ARKit blend-shape weights.

A debugging aid, NOT anatomy: it maps a handful of mouth-related ARKit-52
blend-shapes to a simple parametric lip outline so an authored expression
(Smile vs Frown vs Kiss vs Open...) is visually distinguishable, the way the
hand stick-figure lets a joint pose be eyeballed. The blend-shape ->
geometry mapping here is deliberately crude and lives only in this viz
package -- fsw_r itself stores the real ARKit weights and knows nothing
about this schematic.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np
from numpy.typing import NDArray

# Base mouth half-width in the face-local frame (head circle radius = 1).
_BASE_HALF_WIDTH = 0.45
_SAMPLES = 25


def _avg(blendshapes: Mapping[str, float], left: str, right: str) -> float:
    return (blendshapes.get(left, 0.0) + blendshapes.get(right, 0.0)) / 2.0


def mouth_outline(blendshapes: Mapping[str, float]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return (xs, ys) of a closed mouth outline (upper lip left->right, then
    lower lip right->left) in the face-local frame, centered on the mouth."""
    smile = _avg(blendshapes, "mouthSmileLeft", "mouthSmileRight")
    frown = _avg(blendshapes, "mouthFrownLeft", "mouthFrownRight")
    stretch = _avg(blendshapes, "mouthStretchLeft", "mouthStretchRight")
    press = _avg(blendshapes, "mouthPressLeft", "mouthPressRight") + blendshapes.get("mouthClose", 0.0)
    pucker = blendshapes.get("mouthPucker", 0.0)
    funnel = blendshapes.get("mouthFunnel", 0.0)
    jaw_open = blendshapes.get("jawOpen", 0.0)

    # Corners rise with a smile, drop with a frown.
    corner_y = 0.30 * smile - 0.30 * frown
    # Width widens with stretch, narrows with pucker/funnel.
    half_width = _BASE_HALF_WIDTH * (1.0 + 0.5 * stretch - 0.55 * pucker - 0.25 * funnel)
    half_width = max(half_width, 0.12)
    # Vertical opening from the jaw, plus a small rounded gap for pucker/funnel;
    # pressing/closing the lips flattens it.
    opening = (0.9 * jaw_open + 0.25 * pucker + 0.2 * funnel) * (1.0 - 0.6 * min(press, 1.0))
    lip_thickness = 0.06 * (1.0 - 0.5 * min(press, 1.0))

    x = np.linspace(-half_width, half_width, _SAMPLES)
    arch = 1.0 - (x / half_width) ** 2  # 1 at center, 0 at corners
    upper = corner_y + (opening / 2.0 + lip_thickness) * arch
    lower = corner_y - (opening / 2.0 + lip_thickness) * arch

    xs = np.concatenate([x, x[::-1]])
    ys = np.concatenate([upper, lower[::-1]])
    return xs, ys
