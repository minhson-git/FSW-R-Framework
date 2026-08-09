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

_SKIN = (0.95, 0.80, 0.68)
_HAIR = (0.28, 0.20, 0.13)
_LIP = (0.80, 0.42, 0.42)
_HL = (0.82, 0.20, 0.20)  # highlight
_DARK = (0.30, 0.12, 0.12)
_PUPIL = (0.15, 0.10, 0.07)


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
    xs = np.linspace(-0.24, 0.24, 20)
    ys = cy + curve * (xs / 0.24) ** 2  # corners raised (smile) / lowered (frown)
    pts = np.column_stack([xs, ys, np.full_like(xs, z)])
    return pv.Spline(pts, 40).tube(radius=0.024)


def add_head(pl: pv.Plotter, bs: Mapping[str, float], highlight: str | None = None) -> None:
    """Add the head meshes for one ARKit-52 blend-shape vector to ``pl``."""
    pl.add_mesh(_ellipsoid(0.7, 0.86, 0.78, (0, 0, 0)), color=_SKIN, smooth_shading=True)
    pl.add_mesh(
        pv.Cylinder(center=(0, -0.98, -0.05), direction=(0, 1, 0), radius=0.27, height=0.4),
        color=_HL if highlight == "neck" else _SKIN, smooth_shading=True,
    )
    # Hair: a slightly larger skull clipped to a cap above the brow line, so
    # it sits on top/back and never covers the face.
    hair = _ellipsoid(0.74, 0.92, 0.82, (0, 0.05, -0.04)).clip("y", origin=(0, 0.42, 0), invert=False)
    pl.add_mesh(hair, color=_HL if highlight == "hair" else _HAIR, smooth_shading=True)
    for ex in (-0.68, 0.68):  # ears
        pl.add_mesh(_ellipsoid(0.1, 0.17, 0.13, (ex, 0.04, -0.02)),
                    color=_HL if highlight == "ears" else _SKIN, smooth_shading=True)

    gx, gy = _gaze_shift(bs)
    for side, cx in (("Left", -0.24), ("Right", 0.24)):
        blink = bs.get(f"eyeBlink{side}", 0.0)
        wide = bs.get(f"eyeWide{side}", 0.0)
        ry = 0.1 * (1.0 - blink) + 0.04 * wide
        pl.add_mesh(_ellipsoid(0.13, max(0.015, ry), 0.07, (cx, 0.16, 0.72)), color="white", smooth_shading=True)
        if blink < 0.5:
            pl.add_mesh(pv.Sphere(0.045, center=(cx + gx * 0.05, 0.16 + gy * 0.05, 0.82)), color=_PUPIL)
        # brow
        up = bs.get(f"browOuterUp{side}", 0.0) + 0.6 * bs.get("browInnerUp", 0.0) - bs.get(f"browDown{side}", 0.0)
        pl.add_mesh(pv.Cylinder(center=(cx, 0.33 + 0.07 * up, 0.76), direction=(1, 0, 0), radius=0.018, height=0.26),
                    color=_HAIR)

    pl.add_mesh(_ellipsoid(0.07, 0.16, 0.11, (0, -0.03, 0.8)), color=_SKIN, smooth_shading=True)  # nose

    _add_mouth(pl, bs, highlight == "teeth")
    if bs.get("tongueOut", 0.0) > 0.0:
        length = bs["tongueOut"]
        pl.add_mesh(_ellipsoid(0.09, 0.05, 0.12 * length, (0, -0.42, 0.8)), color=(0.86, 0.45, 0.5))


def _add_mouth(pl: pv.Plotter, bs: Mapping[str, float], show_teeth: bool) -> None:
    jaw = bs.get("jawOpen", 0.0)
    smile = (bs.get("mouthSmileLeft", 0.0) + bs.get("mouthSmileRight", 0.0)) / 2
    frown = (bs.get("mouthFrownLeft", 0.0) + bs.get("mouthFrownRight", 0.0)) / 2
    curve = 0.18 * smile - 0.18 * frown
    open_h = 0.28 * jaw + (0.16 if show_teeth else 0.0)
    cy = -0.36
    if open_h > 0.06:  # open: an oval dark cavity + a white teeth strip, framed by the lips
        pl.add_mesh(_ellipsoid(0.17, open_h / 2 + 0.04, 0.05, (0, cy, 0.78)), color=_DARK)
        pl.add_mesh(_ellipsoid(0.15, 0.028, 0.045, (0, cy + open_h / 2 - 0.01, 0.81)), color="white")
        pl.add_mesh(_lip_curve(cy + open_h / 2 + 0.01, curve, 0.82), color=_LIP)
        pl.add_mesh(_lip_curve(cy - open_h / 2 - 0.01, curve, 0.82), color=_LIP)
    else:  # closed: an upper and lower lip that meet
        pl.add_mesh(_lip_curve(cy + 0.02, curve, 0.82), color=_LIP)
        pl.add_mesh(_lip_curve(cy - 0.02, curve, 0.82), color=_LIP)


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
