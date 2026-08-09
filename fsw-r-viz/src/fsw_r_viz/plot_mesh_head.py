"""A procedural 3D head mesh (matplotlib surfaces, no external assets) that
is driven by ARKit-52 blend-shapes and carries the anatomical features the
2D schematic can't show -- ears, hair, a neck, and teeth inside an open
mouth. So the Category-4 symbols that reference those features (teeth, ears,
hair, neck) become recognisable as a real head, and every FaceSymbol /
FaceMovementSymbol gets a fuller 3D render than the flat schematic.

** Honest scope. ** This is a hand-built approximation, NOT a research face
model. For research-grade realism the target is a parametric mesh -- the
free, ARKit-52-native MediaPipe canonical face mesh, or FLAME/SMPL-X (fine
under their non-commercial research licences) with hair/teeth added as
separate assets. The whole framework already outputs ARKit-52, so that
pipeline is ready to drive such a mesh -- see LEVEL3_MESH.md. This module is
the no-dependency stand-in until one of those assets is integrated.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib

matplotlib.use("Agg")

import numpy as np
from numpy.typing import NDArray

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

_SKIN = "#e8b48c"
_HAIR = "#3a2a1a"
_Grid = tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]


def _ellipsoid(cx: float, cy: float, cz: float, rx: float, ry: float, rz: float, n: int = 24) -> _Grid:
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, np.pi, n)
    x = cx + rx * np.outer(np.cos(u), np.sin(v))
    y = cy + ry * np.outer(np.sin(u), np.sin(v))
    z = cz + rz * np.outer(np.ones_like(u), np.cos(v))
    return x, y, z


def _surf(ax: Axes3D, grid: _Grid, color: str, alpha: float = 1.0) -> None:
    # Display swap (x, z, y): our y is up, matplotlib draws the 3rd arg up.
    x, y, z = grid
    ax.plot_surface(x, z, y, color=color, alpha=alpha, linewidth=0, shade=True)


def draw_mesh_head(ax: Axes3D, blendshapes: Mapping[str, float], highlight: str | None = None) -> None:
    """Draw the procedural head for one ARKit-52 blend-shape vector.
    ``highlight`` optionally emphasises a feature ('ears'/'hair'/'neck'/
    'teeth') for a symbol that references it."""
    def bs(name: str) -> float:
        return blendshapes.get(name, 0.0)

    # Head kept semi-transparent: matplotlib 3D does not depth-sort separate
    # surfaces, so an opaque head hides the front features -- see the module
    # note on why a real mesh renderer is the production path.
    _surf(ax, _ellipsoid(0, 0, 0, 0.75, 0.95, 0.85), _SKIN, alpha=0.45)  # head
    _surf(ax, _ellipsoid(0, -1.15, -0.1, 0.28, 0.35, 0.28), _SKIN)  # neck
    # Hair: a cap over the top/back.
    hx, hy, hz = _ellipsoid(0, 0.28, -0.12, 0.78, 0.72, 0.9, 20)
    mask = hy >= 0.28
    _surf(ax, (np.where(mask, hx, np.nan), hy, np.where(mask, hz, np.nan)),
          "#a03030" if highlight == "hair" else _HAIR)
    for ex in (-0.78, 0.78):  # ears
        _surf(ax, _ellipsoid(ex, -0.05, -0.05, 0.1, 0.18, 0.14),
              "#a03030" if highlight == "ears" else _SKIN)

    # Eyes (blink closes them), sitting just proud of the front (+z) surface.
    for side, cx in (("Left", -0.28), ("Right", 0.28)):
        blink = bs(f"eyeBlink{side}")
        wide = bs(f"eyeWide{side}")
        ry = max(0.02, 0.1 * (1 - blink) + 0.04 * wide)
        _surf(ax, _ellipsoid(cx, 0.18, 0.82, 0.14, ry, 0.06), "white")
        if blink < 0.5:
            gx, gy = _gaze_shift(blendshapes)
            ax.scatter([cx + gx * 0.06], [0.9], [0.18 + gy * 0.05], color="#20140a", s=25)

    # Brows.
    for side, cx in (("Left", -0.28), ("Right", 0.28)):
        up = bs(f"browOuterUp{side}") + 0.6 * bs("browInnerUp") - bs(f"browDown{side}")
        by = 0.4 + 0.08 * up
        ax.plot([cx - 0.14, cx + 0.14], [0.88, 0.88], [by, by], color="#3a2a1a", linewidth=3)

    ax.plot([0, 0], [0.95, 1.0], [0.12, -0.12], color="#c99", linewidth=3)  # nose

    _draw_mouth(ax, blendshapes, highlight == "teeth")

    ax.set_title("", fontsize="small")
    for setter in (ax.set_xlim, ax.set_zlim):
        setter(-1.2, 1.2)
    ax.set_ylim(-1.4, 1.2)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=6, azim=-90)  # look at the face (front = +z)


def _gaze_shift(bs: Mapping[str, float]) -> tuple[float, float]:
    pr = (bs.get("eyeLookInLeft", 0) + bs.get("eyeLookOutRight", 0)) / 2
    pl = (bs.get("eyeLookOutLeft", 0) + bs.get("eyeLookInRight", 0)) / 2
    up = (bs.get("eyeLookUpLeft", 0) + bs.get("eyeLookUpRight", 0)) / 2
    dn = (bs.get("eyeLookDownLeft", 0) + bs.get("eyeLookDownRight", 0)) / 2
    return pl - pr, up - dn


def _draw_mouth(ax: Axes3D, bs: Mapping[str, float], show_teeth: bool) -> None:
    jaw = bs.get("jawOpen", 0.0)
    smile = (bs.get("mouthSmileLeft", 0) + bs.get("mouthSmileRight", 0)) / 2
    frown = (bs.get("mouthFrownLeft", 0) + bs.get("mouthFrownRight", 0)) / 2
    open_h = 0.28 * jaw + (0.12 if show_teeth else 0.0)
    cy = -0.5 + 0.12 * smile - 0.12 * frown
    xs = np.linspace(-0.28, 0.28, 20)
    arch = 1 - (xs / 0.28) ** 2
    top = cy + open_h * arch * 0.5 + 0.06 * (smile - frown) * (1 - arch)
    bot = cy - open_h * arch * 0.5 - 0.06 * (smile - frown) * (1 - arch)
    if open_h > 0.06:  # open mouth: dark interior + a white teeth band on top
        ax.plot(np.r_[xs, xs[::-1]], np.full(40, 0.9), np.r_[top, bot[::-1]], color="#7a1f1f")
        ax.plot(xs, np.full(20, 0.92), top - 0.02, color="white", linewidth=4)
    ax.plot(xs, np.full(20, 0.93), top, color="#a02020", linewidth=2)
    ax.plot(xs, np.full(20, 0.93), bot, color="#a02020", linewidth=2)


def render_mesh_head_to_file(
    ax_source: Sequence[tuple[Mapping[str, float], str, str | None]], output_path: str
) -> None:
    """Render a row of procedural heads: each item is
    (blendshapes, title, highlight-feature-or-None)."""
    fig = plt.figure(figsize=(4 * len(ax_source), 4))
    for i, (blendshapes, title, highlight) in enumerate(ax_source):
        ax = fig.add_subplot(1, len(ax_source), i + 1, projection="3d")
        assert isinstance(ax, Axes3D)
        draw_mesh_head(ax, blendshapes, highlight)
        ax.set_title(title, fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=130)
    plt.close(fig)
