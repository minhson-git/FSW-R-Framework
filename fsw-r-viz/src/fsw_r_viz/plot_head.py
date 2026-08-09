"""Renders a fsw_r Category 4 head-orientation symbol as a simple 3D head
whose facing shows the orientation, so a HeadSymbol's pitch/yaw/roll can be
checked visually -- the head analogue of plot_hand / plot_face.

A debugging aid: a light sphere for the head, a bold arrow for the nose
(face-forward), two eyes and a crown marker, all rotated by the symbol's
``get_head_orientation()``. Same (x, z, y) display swap as the other 3D
views so our y (up) renders vertical.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.renderable_symbol import FSWHeadRenderable

# Head-local landmarks (before orientation): nose forward +z, crown up +y,
# eyes on the front upper face.
_NOSE = np.array([0.0, 0.0, 1.0])
_CROWN = np.array([0.0, 1.0, 0.0])
_EYES = np.array([[-0.32, 0.22, 0.86], [0.32, 0.22, 0.86]])


def _sphere(n: int = 16) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, np.pi, n)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    return x, y, z


def draw_head_orientation(ax: Axes3D, rot: Rotation, title: str) -> None:
    """Draw the schematic 3D head at one orientation. Split out so an
    animation can draw a frame per time step (see animate_head.py)."""
    sx, sy, sz = _sphere()
    # Light head sphere (display swap x, z, y).
    ax.plot_wireframe(sx, sz, sy, color="0.85", linewidth=0.5)

    nose = rot.apply(_NOSE)
    crown = rot.apply(_CROWN)
    eyes = rot.apply(_EYES)
    ax.quiver(0, 0, 0, nose[0], nose[2], nose[1], color="tab:red", linewidth=3, label="nose")
    ax.plot([0, crown[0]], [0, crown[2]], [0, crown[1]], color="tab:blue", linewidth=2, label="crown")
    ax.scatter(eyes[:, 0], eyes[:, 2], eyes[:, 1], color="black", s=40)

    ax.set_title(title, fontsize="small")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_zlim(-1.3, 1.3)
    ax.set_xlabel("x")
    ax.set_ylabel("z (depth)")
    ax.set_zlabel("y (up)")
    ax.view_init(elev=12, azim=-70)


def _plot_on(ax: Axes3D, symbol: FSWHeadRenderable, title: str) -> None:
    draw_head_orientation(ax, symbol.get_head_orientation(), title)


def render_head_to_file(symbol: FSWHeadRenderable, output_path: str, title: str | None = None) -> None:
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")
    _plot_on(ax, symbol, title or symbol.symbol_id)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_heads_grid(symbols: Sequence[tuple[FSWHeadRenderable, str]], output_path: str) -> None:
    fig = plt.figure(figsize=(5 * len(symbols), 5))
    for i, (symbol, title) in enumerate(symbols):
        ax = fig.add_subplot(1, len(symbols), i + 1, projection="3d")
        _plot_on(ax, symbol, title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
