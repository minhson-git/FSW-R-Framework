"""Plays a Category 4 facial *movement* (a blink, a jaw open, a tongue
lick...) back over time on the schematic face -- the facial analogue of
animate_movement.py. Samples the symbol's ``expression_at(t)`` and draws each
frame with plot_face's ``draw_face_expression``; no facial geometry is
reimplemented.

Two outputs, same frames: a real animated GIF and a static filmstrip (N
frames side by side) so the motion is checkable as one image.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.axes import Axes

from fsw_r.core.face_movement import FaceMovementSymbol

from fsw_r_viz.plot_face import draw_face_expression


def _draw(ax: Axes, symbol: FaceMovementSymbol, t: float) -> None:
    ax.clear()
    draw_face_expression(ax, symbol.expression_at(t).blendshapes, f"{symbol.name}  t={t:.2f}")


def animate_face_movement_to_gif(
    symbol: FaceMovementSymbol, output_path: str, samples: int = 48, fps: int = 16
) -> None:
    fig, ax = plt.subplots(figsize=(4, 4))

    def update(frame: int) -> None:
        _draw(ax, symbol, frame / (samples - 1))

    animation = FuncAnimation(fig, update, frames=samples, interval=1000 // fps)
    animation.save(output_path, writer=PillowWriter(fps=fps))
    plt.close(fig)


def render_face_movement_filmstrip(
    symbol: FaceMovementSymbol, output_path: str, frames: int = 6
) -> None:
    fig, axes = plt.subplots(1, frames, figsize=(3 * frames, 3))
    for i, ax in enumerate(np.atleast_1d(axes)):
        _draw(ax, symbol, i / (frames - 1) if frames > 1 else 0.0)
    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
