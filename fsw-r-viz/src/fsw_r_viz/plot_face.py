"""Renders a fsw_r.FaceSymbol as a schematic 2D face, using matplotlib, so
an authored facial expression can be sanity-checked visually.

Like plot_hand for hands, this is a debugging aid, not the final renderer.
Only the mouth is expression-driven so far (Category 4 Group 25); the head
outline, eyes, brows and nose are drawn neutral as reference features. It
takes FaceSymbol directly (it calls get_expression()).
"""

from __future__ import annotations

from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # headless: save to file instead of opening a window

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from fsw_r.core.face_symbol import FaceSymbol

from fsw_r_viz.face_geometry import mouth_outline


def _plot_on(ax: Axes, symbol: FaceSymbol, title: str) -> None:
    # Neutral reference features (head, eyes, brows, nose).
    head = Circle((0.0, 0.0), 1.0, fill=False, color="0.6", linewidth=1.5)
    ax.add_patch(head)
    for eye_x in (-0.35, 0.35):
        ax.add_patch(Circle((eye_x, 0.35), 0.09, color="0.4"))
        ax.plot([eye_x - 0.15, eye_x + 0.15], [0.55, 0.55], color="0.6", linewidth=2)  # brow
    ax.plot([0.0, 0.0], [0.2, -0.1], color="0.7", linewidth=1.5)  # nose

    # Expression-driven mouth (centered around y = -0.45).
    xs, ys = mouth_outline(symbol.get_expression().blendshapes)
    ax.fill(xs, ys - 0.45, color="tab:red", alpha=0.35)
    ax.plot(xs, ys - 0.45, color="tab:red", linewidth=2)

    ax.set_title(title, fontsize="small")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")


def render_face_to_file(symbol: FaceSymbol, output_path: str, title: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(4, 4))
    _plot_on(ax, symbol, title or f"{symbol.symbol_id} {symbol.name}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def render_faces_grid(symbols: Sequence[tuple[FaceSymbol, str]], output_path: str) -> None:
    fig, axes = plt.subplots(1, len(symbols), figsize=(4 * len(symbols), 4))
    axes_list = axes if len(symbols) > 1 else [axes]
    for ax, (symbol, title) in zip(axes_list, symbols):
        _plot_on(ax, symbol, title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
