"""Plays a Category 4 head *movement* (nod/shake/tilt/circle) back over time
on the schematic 3D head -- the head analogue of animate_face.py. Samples the
symbol's ``orientation_at(t)`` and draws each frame with plot_head's
``draw_head_orientation``.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.head_movement import HeadMovementSymbol

from fsw_r_viz.plot_head import draw_head_orientation


def animate_head_movement_to_gif(
    symbol: HeadMovementSymbol, output_path: str, samples: int = 48, fps: int = 16
) -> None:
    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111, projection="3d")
    assert isinstance(ax, Axes3D)

    def update(frame: int) -> None:
        ax.clear()
        t = frame / (samples - 1)
        draw_head_orientation(ax, symbol.orientation_at(t), f"{symbol.name}  t={t:.2f}")

    animation = FuncAnimation(fig, update, frames=samples, interval=1000 // fps)
    animation.save(output_path, writer=PillowWriter(fps=fps))
    plt.close(fig)


def render_head_movement_filmstrip(
    symbol: HeadMovementSymbol, output_path: str, frames: int = 6
) -> None:
    fig = plt.figure(figsize=(3 * frames, 3))
    for i in range(frames):
        ax = fig.add_subplot(1, frames, i + 1, projection="3d")
        assert isinstance(ax, Axes3D)
        t = i / (frames - 1) if frames > 1 else 0.0
        draw_head_orientation(ax, symbol.orientation_at(t), f"t={t:.2f}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
