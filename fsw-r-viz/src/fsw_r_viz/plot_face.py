"""Renders a fsw_r.FaceSymbol as a schematic 2D face, using matplotlib, so
an authored facial expression can be sanity-checked visually.

Like plot_hand for hands, this is a debugging aid, not the final renderer.
The mouth/tongue (Group 25/26) and brows + eye-openness (Group 23) are
expression-driven; the nose and head outline are neutral reference, and
cheek/nose blend-shapes (Group 24) aren't drawn yet. It takes FaceSymbol
directly (it calls get_expression()). Left/Right ARKit targets are drawn in
the viewer's frame (Left = viewer's left eye), fine for a schematic check.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib

matplotlib.use("Agg")  # headless: save to file instead of opening a window

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Circle, Ellipse

from fsw_r.core.face_symbol import FaceSymbol

from fsw_r_viz.face_geometry import mouth_outline

# side label -> (eye center x, ARKit suffix)
_EYES = (("left", -0.35, "Left"), ("right", 0.35, "Right"))


def _gaze_offset(bs: Mapping[str, float]) -> tuple[float, float]:
    """Screen-space pupil offset (right+, up+) from ARKit eyeLook* targets.
    ARKit is in the person's frame; the viz is viewer-facing, so the
    horizontal component is flipped: the person looking to THEIR right
    (eyeLookInLeft / eyeLookOutRight) shows as pupils shifted to the
    viewer's left."""
    up = (bs.get("eyeLookUpLeft", 0.0) + bs.get("eyeLookUpRight", 0.0)) / 2.0
    down = (bs.get("eyeLookDownLeft", 0.0) + bs.get("eyeLookDownRight", 0.0)) / 2.0
    person_right = (bs.get("eyeLookInLeft", 0.0) + bs.get("eyeLookOutRight", 0.0)) / 2.0
    person_left = (bs.get("eyeLookOutLeft", 0.0) + bs.get("eyeLookInRight", 0.0)) / 2.0
    return person_left - person_right, up - down


def _draw_eye_and_brow(ax: Axes, bs: Mapping[str, float], cx: float, suffix: str) -> None:
    blink = bs.get(f"eyeBlink{suffix}", 0.0)
    wide = bs.get(f"eyeWide{suffix}", 0.0)
    squint = bs.get(f"eyeSquint{suffix}", 0.0)
    openness = max(0.0, 1.0 - blink - 0.4 * squint) + 0.5 * wide

    eye_ry = 0.09 * openness
    eye_rx = 0.11 * (1.0 + 0.15 * wide)
    if eye_ry < 0.02:  # effectively closed -> a lid line
        ax.plot([cx - eye_rx, cx + eye_rx], [0.35, 0.35], color="0.4", linewidth=2)
    else:
        # Eyeball (light) + pupil (dark), the pupil offset by the gaze so
        # eyegaze symbols read as "looking" in a direction.
        ax.add_patch(Ellipse((cx, 0.35), 2 * eye_rx, 2 * eye_ry, facecolor="0.9", edgecolor="0.4"))
        gaze_x, gaze_y = _gaze_offset(bs)
        px = cx + gaze_x * eye_rx * 0.55
        py = 0.35 + gaze_y * eye_ry * 0.55
        ax.add_patch(Circle((px, py), min(eye_rx, eye_ry) * 0.5, color="0.2"))

    # Brow: raised by outer/inner-up, lowered by brow-down.
    brow_up = bs.get(f"browOuterUp{suffix}", 0.0) + 0.6 * bs.get("browInnerUp", 0.0)
    brow_down = bs.get(f"browDown{suffix}", 0.0)
    brow_y = 0.55 + 0.14 * brow_up - 0.12 * brow_down
    inner_lift = 0.06 * bs.get("browInnerUp", 0.0)  # inner end pulled up
    inner_x, outer_x = (cx + 0.15, cx - 0.15) if cx < 0 else (cx - 0.15, cx + 0.15)
    ax.plot([inner_x, outer_x], [brow_y + inner_lift, brow_y], color="0.6", linewidth=2)


def _plot_on(ax: Axes, symbol: FaceSymbol, title: str) -> None:
    blendshapes = symbol.get_expression().blendshapes

    head = Circle((0.0, 0.0), 1.0, fill=False, color="0.6", linewidth=1.5)
    ax.add_patch(head)
    for _side, cx, suffix in _EYES:
        _draw_eye_and_brow(ax, blendshapes, cx, suffix)
    ax.plot([0.0, 0.0], [0.2, -0.1], color="0.7", linewidth=1.5)  # nose (neutral)

    # A protruding tongue hangs below the mouth, length scaled by tongueOut
    # (drawn first so the mouth outline sits on top of it).
    tongue_out = blendshapes.get("tongueOut", 0.0)
    if tongue_out > 0.0:
        length = 0.15 + 0.35 * tongue_out
        tx = [-0.12, 0.12, 0.10, 0.0, -0.10]
        ty = [-0.45, -0.45, -0.45 - length, -0.45 - length * 1.15, -0.45 - length]
        ax.fill(tx, ty, color="tab:pink", edgecolor="tab:red", linewidth=1.5)

    # Expression-driven mouth (centered around y = -0.45).
    xs, ys = mouth_outline(blendshapes)
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
