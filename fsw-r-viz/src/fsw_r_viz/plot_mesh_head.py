"""A real 3D head, rendered offscreen with pyvista/VTK (proper depth
sorting, unlike matplotlib), driven by ARKit-52 blend-shapes. Carries the
anatomical features the 2D schematic can't: ears, hair, a neck, and teeth in
an open mouth -- so the Category-4 symbols that reference those features
(teeth/ears/hair/neck) are recognisable, and every FaceSymbol /
FaceMovementSymbol gets a solid 3D render.

Still a hand-built approximation, not a research face model -- for
research-grade realism the target is a parametric mesh (MediaPipe canonical
mesh, or FLAME/SMPL-X) driven by the ARKit-52 the framework already emits;
see LEVEL3_MESH.md. This is the no-face-asset stand-in, now on a proper 3D
renderer.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

_SKIN = (0.91, 0.72, 0.56)
_HAIR = (0.24, 0.16, 0.10)
_LIP = (0.72, 0.16, 0.16)
_HL = (0.80, 0.12, 0.12)  # highlight
_DARK = (0.20, 0.05, 0.05)
_PUPIL = (0.12, 0.08, 0.05)


def _ellipsoid(rx: float, ry: float, rz: float, center: tuple[float, float, float]) -> pv.PolyData:
    mesh = pv.ParametricEllipsoid(rx, ry, rz)
    mesh.translate(center, inplace=True)
    return mesh


def _gaze_shift(bs: Mapping[str, float]) -> tuple[float, float]:
    pr = (bs.get("eyeLookInLeft", 0.0) + bs.get("eyeLookOutRight", 0.0)) / 2
    pl = (bs.get("eyeLookOutLeft", 0.0) + bs.get("eyeLookInRight", 0.0)) / 2
    up = (bs.get("eyeLookUpLeft", 0.0) + bs.get("eyeLookUpRight", 0.0)) / 2
    dn = (bs.get("eyeLookDownLeft", 0.0) + bs.get("eyeLookDownRight", 0.0)) / 2
    return pl - pr, up - dn


def _lip_curve(cy: float, curve: float, z: float) -> pv.PolyData:
    xs = np.linspace(-0.3, 0.3, 20)
    ys = cy + curve * (xs / 0.3) ** 2  # corners raised (smile) / lowered (frown)
    pts = np.column_stack([xs, ys, np.full_like(xs, z)])
    return pv.Spline(pts, 40).tube(radius=0.028)


def add_head(pl: pv.Plotter, bs: Mapping[str, float], highlight: str | None = None) -> None:
    """Add the head meshes for one ARKit-52 blend-shape vector to ``pl``."""
    pl.add_mesh(_ellipsoid(0.75, 0.95, 0.82, (0, 0, 0)), color=_SKIN, smooth_shading=True)
    pl.add_mesh(
        pv.Cylinder(center=(0, -1.05, -0.05), direction=(0, 1, 0), radius=0.3, height=0.5),
        color=_HL if highlight == "neck" else _SKIN, smooth_shading=True,
    )
    # Hair: a slightly larger skull clipped to a cap above the brow line, so
    # it sits on top/back and never covers the face.
    hair = _ellipsoid(0.8, 1.0, 0.86, (0, 0.06, -0.05)).clip("y", origin=(0, 0.42, 0), invert=False)
    pl.add_mesh(hair, color=_HL if highlight == "hair" else _HAIR, smooth_shading=True)
    for ex in (-0.76, 0.76):  # ears
        pl.add_mesh(_ellipsoid(0.12, 0.2, 0.15, (ex, -0.05, -0.05)),
                    color=_HL if highlight == "ears" else _SKIN, smooth_shading=True)

    gx, gy = _gaze_shift(bs)
    for side, cx in (("Left", -0.28), ("Right", 0.28)):
        blink = bs.get(f"eyeBlink{side}", 0.0)
        wide = bs.get(f"eyeWide{side}", 0.0)
        ry = 0.12 * (1.0 - blink) + 0.05 * wide
        pl.add_mesh(_ellipsoid(0.15, max(0.02, ry), 0.08, (cx, 0.2, 0.78)), color="white", smooth_shading=True)
        if blink < 0.5:
            pl.add_mesh(pv.Sphere(0.05, center=(cx + gx * 0.06, 0.2 + gy * 0.05, 0.9)), color=_PUPIL)
        # brow
        up = bs.get(f"browOuterUp{side}", 0.0) + 0.6 * bs.get("browInnerUp", 0.0) - bs.get(f"browDown{side}", 0.0)
        pl.add_mesh(pv.Cylinder(center=(cx, 0.42 + 0.08 * up, 0.82), direction=(1, 0, 0), radius=0.02, height=0.28),
                    color=_HAIR)

    pl.add_mesh(_ellipsoid(0.08, 0.14, 0.12, (0, 0.0, 0.88)), color=_SKIN, smooth_shading=True)  # nose

    _add_mouth(pl, bs, highlight == "teeth")
    if bs.get("tongueOut", 0.0) > 0.0:
        length = bs["tongueOut"]
        pl.add_mesh(_ellipsoid(0.1, 0.06, 0.14 * length, (0, -0.62, 0.85)), color=(0.85, 0.4, 0.45))


def _add_mouth(pl: pv.Plotter, bs: Mapping[str, float], show_teeth: bool) -> None:
    jaw = bs.get("jawOpen", 0.0)
    smile = (bs.get("mouthSmileLeft", 0.0) + bs.get("mouthSmileRight", 0.0)) / 2
    frown = (bs.get("mouthFrownLeft", 0.0) + bs.get("mouthFrownRight", 0.0)) / 2
    curve = 0.22 * smile - 0.22 * frown
    open_h = 0.3 * jaw + (0.14 if show_teeth else 0.0)
    cy = -0.5
    if open_h > 0.06:  # open: dark cavity + white teeth, framed by the lips
        pl.add_mesh(_ellipsoid(0.26, open_h / 2 + 0.02, 0.06, (0, cy, 0.8)), color=_DARK)
        pl.add_mesh(_ellipsoid(0.24, 0.03, 0.05, (0, cy + open_h / 2 - 0.02, 0.83)), color="white")
        pl.add_mesh(_lip_curve(cy + open_h / 2, curve, 0.84), color=_LIP)
        pl.add_mesh(_lip_curve(cy - open_h / 2, curve, 0.84), color=_LIP)
    else:
        pl.add_mesh(_lip_curve(cy, curve, 0.84), color=_LIP)


def render_mesh_head_to_file(
    heads: Sequence[tuple[Mapping[str, float], str, str | None]], output_path: str
) -> None:
    """Render a row of 3D heads: each item is (blendshapes, title,
    highlight-feature-or-None)."""
    pl = pv.Plotter(shape=(1, len(heads)), off_screen=True, window_size=[420 * len(heads), 480], border=False)
    for i, (blendshapes, title, highlight) in enumerate(heads):
        pl.subplot(0, i)
        add_head(pl, blendshapes, highlight)
        pl.add_text(title, position="upper_edge", font_size=9, color="black")
        pl.set_background("white")
        pl.camera_position = [(0.0, 0.0, 4.2), (0.0, -0.1, 0.0), (0.0, 1.0, 0.0)]
    pl.screenshot(output_path)
    pl.close()
