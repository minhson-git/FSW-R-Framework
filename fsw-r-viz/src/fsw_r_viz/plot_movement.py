"""Renders a fsw_r Category 2 (Movement) symbol as its 3D trajectory, using
matplotlib, so a MotionPath can be sanity-checked visually instead of just
reading sample points off an array -- the Movement analogue of plot_hand
(static hand pose) and plot_face (static expression).

Like the others this is a debugging aid, not the final renderer. It takes an
``FSWMotionRenderable`` and samples it through fsw_r's own
``sample_trajectory`` (no trajectory math is reimplemented here). The start
of the path is drawn green and the end red, so the direction of travel is
visible; a degenerate CONTACT path (a single repeated point) shows as just
that point.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # headless: save to file instead of opening a window

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.renderable_symbol import FSWMotionRenderable


def _plot_on(ax: Axes3D, symbol: FSWMotionRenderable, title: str) -> None:
    points = sample_trajectory(symbol.get_motion_path(), symbol.rotation)
    # Same display convention as plot_hand: our data has y = primary travel
    # direction (should read vertical) and z = depth, but matplotlib always
    # draws its 3rd argument as the vertical screen axis -- so hand it
    # (x, z, y), not (x, y, z). Display-only swap; the geometry is untouched.
    xs, ys_depth, zs_up = points[:, 0], points[:, 2], points[:, 1]
    ax.plot(xs, ys_depth, zs_up, color="tab:blue", linewidth=2, alpha=0.8)
    ax.scatter(xs[0], ys_depth[0], zs_up[0], color="green", s=50, label="start")
    ax.scatter(xs[-1], ys_depth[-1], zs_up[-1], color="red", s=50, label="end")

    ax.set_title(title, fontsize="small")
    ax.set_xlabel("x")
    ax.set_ylabel("z (depth)")
    ax.set_zlabel("y (travel)")
    span = 12.0
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    ax.set_zlim(-span, span)
    ax.view_init(elev=20, azim=-60)


def render_movement_to_file(symbol: FSWMotionRenderable, output_path: str, title: str | None = None) -> None:
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")
    _plot_on(ax, symbol, title or symbol.symbol_id)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_movements_grid(symbols: Sequence[tuple[FSWMotionRenderable, str]], output_path: str) -> None:
    fig = plt.figure(figsize=(5 * len(symbols), 5))
    for i, (symbol, title) in enumerate(symbols):
        ax = fig.add_subplot(1, len(symbols), i + 1, projection="3d")
        _plot_on(ax, symbol, title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
