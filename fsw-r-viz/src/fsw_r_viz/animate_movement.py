"""Plays a fsw_r Category 2 (Movement) symbol back over time: a marker
travelling along the trajectory, with a growing trail. This is the "time
axis" the static plot_movement.py doesn't show -- the first step toward a
real 3D motion clip (a later stage would drive a rigged hand along the path
instead of a bare marker).

Two outputs, same underlying frames:
- ``animate_movement_to_gif``: an actual animated GIF (via matplotlib's
  PillowWriter -- pillow ships with matplotlib, no extra dependency).
- ``render_movement_filmstrip``: a static PNG of N equally-spaced frames
  side by side, so the motion can be sanity-checked at a glance (and read
  off a single image) without opening the GIF.

Like the rest of fsw-r-viz this is a debugging aid: it samples the symbol
through fsw_r's own ``sample_trajectory`` and reimplements no trajectory
math. Same (x, z, y) display swap as plot_movement / plot_hand.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless

import numpy as np
from numpy.typing import NDArray

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.renderable_symbol import FSWMotionRenderable

_AXIS_SPAN = 12.0
_Cols = tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]


def _display_columns(symbol: FSWMotionRenderable, samples: int) -> _Cols:
    """Sampled trajectory as display-space columns (x, depth=z, up=y)."""
    points = sample_trajectory(symbol.get_motion_path(), symbol.rotation, samples)
    return points[:, 0], points[:, 2], points[:, 1]


def _draw_frame(ax: Axes3D, cols: _Cols, i: int, title: str) -> None:
    xs, depth, up = cols
    ax.clear()
    ax.plot(xs, depth, up, color="0.85", linewidth=1)  # faint full path
    ax.plot(xs[: i + 1], depth[: i + 1], up[: i + 1], color="tab:blue", linewidth=2)  # trail
    ax.scatter(xs[i], depth[i], up[i], color="red", s=60)  # current position
    ax.set_title(title, fontsize="small")
    ax.set_xlim(-_AXIS_SPAN, _AXIS_SPAN)
    ax.set_ylim(-_AXIS_SPAN, _AXIS_SPAN)
    ax.set_zlim(-_AXIS_SPAN, _AXIS_SPAN)
    ax.set_xlabel("x")
    ax.set_ylabel("z")
    ax.set_zlabel("y")
    ax.view_init(elev=20, azim=-60)


def animate_movement_to_gif(
    symbol: FSWMotionRenderable, output_path: str, samples: int = 48, fps: int = 16
) -> None:
    cols = _display_columns(symbol, samples)
    n = len(cols[0])
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int) -> None:
        _draw_frame(ax, cols, frame, symbol.symbol_id)

    animation = FuncAnimation(fig, update, frames=n, interval=1000 // fps)
    animation.save(output_path, writer=PillowWriter(fps=fps))
    plt.close(fig)


def render_movement_filmstrip(
    symbol: FSWMotionRenderable, output_path: str, frames: int = 6, samples: int = 48
) -> None:
    cols = _display_columns(symbol, samples)
    n = len(cols[0])
    idxs = np.linspace(0, n - 1, frames).astype(int)
    fig = plt.figure(figsize=(3 * frames, 3))
    for panel, i in enumerate(idxs):
        ax = fig.add_subplot(1, frames, panel + 1, projection="3d")
        t = panel / (frames - 1) if frames > 1 else 0.0
        _draw_frame(ax, cols, int(i), f"t={t:.1f}")
    fig.suptitle(symbol.symbol_id, fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
