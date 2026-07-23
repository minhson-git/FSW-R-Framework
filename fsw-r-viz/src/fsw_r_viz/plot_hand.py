"""Renders a fsw_r.FSWRenderableSymbol as a 3D stick-figure hand, using
matplotlib, so a joint pose + wrist orientation can be sanity-checked
visually instead of just reading numbers off a dataclass.

This is a debugging aid, not the final renderer. It depends on fsw_r's
public types only (FSWRenderableSymbol, HandJointPose) -- fsw_r itself has
no knowledge of this package or of matplotlib.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # headless: save to file instead of opening a window

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import HandSide

from fsw_r_viz.hand_geometry import apply_wrist_orientation, hand_local_points, mirror_for_left_hand

_FINGER_COLORS: dict[str, str] = {
    "thumb": "tab:orange",
    "index": "tab:red",
    "middle": "tab:blue",
    "ring": "tab:green",
    "pinky": "tab:purple",
}


def _plot_on(ax: Axes3D, symbol: FSWRenderableSymbol, title: str) -> None:
    local_points = hand_local_points(symbol.get_joint_pose())
    if symbol.hand_side == HandSide.LEFT:
        local_points = mirror_for_left_hand(local_points)
    world_points = apply_wrist_orientation(local_points, symbol.get_wrist_orientation())

    for finger, points in world_points.items():
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        ax.plot(xs, ys, zs, marker="o", color=_FINGER_COLORS[finger], label=finger)

    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-2, 10)
    ax.set_zlim(-6, 6)
    # A genuine oblique 3D view (not a flattened top-down look) -- rotation
    # still spins the whole hand rigidly about the z axis (the wrist, not
    # the finger joints), it's just now viewed at an angle so the render
    # reads as 3D rather than a flat 2D clock face.
    ax.view_init(elev=20, azim=-60)


def render_symbol_to_file(symbol: FSWRenderableSymbol, output_path: str, title: str | None = None) -> None:
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    _plot_on(ax, symbol, title or symbol.symbol_id)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_symbols_grid(
    symbols: Sequence[tuple[FSWRenderableSymbol, str]], output_path: str
) -> None:
    fig = plt.figure(figsize=(6 * len(symbols), 6))
    for i, (symbol, title) in enumerate(symbols):
        ax = fig.add_subplot(1, len(symbols), i + 1, projection="3d")
        _plot_on(ax, symbol, title)
    fig.legend(
        handles=[
            Line2D([0], [0], color=color, marker="o", label=finger)
            for finger, color in _FINGER_COLORS.items()
        ],
        loc="lower center",
        ncol=5,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
