"""Renders a fsw_r.FSWHandRenderable as a 3D stick-figure hand, using
matplotlib, so a joint pose + wrist orientation can be sanity-checked
visually instead of just reading numbers off a dataclass.

This is a debugging aid, not the final renderer. It depends on fsw_r's
public types only (FSWHandRenderable, HandJointPose) -- fsw_r itself has
no knowledge of this package or of matplotlib. Takes FSWHandRenderable
specifically (not the generic FSWRenderableSymbol marker), same reasoning
as fsw_r.core.renderer.HandMeshRenderer3D: this module only knows how to
draw a hand, so its signature says so -- a Category 2 (Movement) symbol is
a type error here, not a runtime isinstance branch.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib
import numpy as np

matplotlib.use("Agg")  # headless: save to file instead of opening a window

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.renderable_symbol import FSWHandRenderable
from fsw_r.core.types import HandSide

from fsw_r_viz.hand_geometry import apply_wrist_orientation, hand_local_points, mirror_for_left_hand

_FINGER_COLORS: dict[str, str] = {
    "thumb": "tab:orange",
    "index": "tab:red",
    "middle": "tab:blue",
    "ring": "tab:green",
    "pinky": "tab:purple",
}


def _plot_on(ax: Axes3D, symbol: FSWHandRenderable, title: str) -> None:
    local_points = hand_local_points(symbol.get_joint_pose())
    if symbol.hand_side == HandSide.LEFT:
        local_points = mirror_for_left_hand(local_points)
    world_points = apply_wrist_orientation(local_points, symbol.get_wrist_orientation())

    # matplotlib's Axes3D always draws its 3rd plot argument ("Z") as the
    # vertical screen axis, regardless of what we call our own axes. Our
    # data convention has y = wrist->fingertip (the axis that should look
    # vertical, e.g. index finger pointing "up") and z = palm normal (depth,
    # toward the viewer) -- so we hand matplotlib (x, z, y), not (x, y, z),
    # to make our y actually render vertically. This is a display-only
    # swap; the underlying geometry/rotation math is untouched.
    for finger, points in world_points.items():
        xs = [p[0] for p in points]
        depths = [p[2] for p in points]
        heights = [p[1] for p in points]
        ax.plot(xs, depths, heights, marker="o", color=_FINGER_COLORS[finger], label=finger)

    # A wireframe stick figure has no surface to shade, so "palm faces you"
    # vs "back faces you" (fill's effect) isn't visually obvious from bone
    # positions alone at a fixed camera angle -- draw the palm-normal vector
    # explicitly (green = pointing at the viewer/palm, red = pointing away/
    # back of hand) so fill's effect can actually be seen, not just trusted.
    # mirror_for_left_hand only flips the spread axis (x), not z, so the
    # local palm normal is still +z regardless of hand_side at this point.
    palm_normal_local = np.array([0.0, 0.0, 1.0])
    palm_normal_world = symbol.get_wrist_orientation().apply(palm_normal_local)
    wrist = world_points["index"][0]
    arrow_color = "green" if palm_normal_world[2] > 0 else "red"
    ax.quiver(
        wrist[0], wrist[2], wrist[1],
        palm_normal_world[0], palm_normal_world[2], palm_normal_world[1],
        length=4.0, color=arrow_color, linewidth=2,
    )

    ax.set_title(title)
    ax.set_xlabel("x (spread)")
    ax.set_ylabel("z (depth)")
    ax.set_zlabel("y (up)")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_zlim(-2, 10)
    # A genuine oblique 3D view (not a flattened top-down look) -- rotation
    # still spins the whole hand rigidly about the z axis (the wrist, not
    # the finger joints), it's just now viewed at an angle so the render
    # reads as 3D rather than a flat 2D clock face.
    ax.view_init(elev=20, azim=-60)


def render_symbol_to_file(symbol: FSWHandRenderable, output_path: str, title: str | None = None) -> None:
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    _plot_on(ax, symbol, title or symbol.symbol_id)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_symbols_grid(
    symbols: Sequence[tuple[FSWHandRenderable, str]], output_path: str
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
