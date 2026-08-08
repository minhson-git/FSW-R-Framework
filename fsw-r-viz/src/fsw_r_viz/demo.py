"""Renders two comparison grids as 3D stick-figure hands:

1. index_finger_rotations.png -- Base Symbol 1 ("Index", 01-01-001) at a
   fixed fill (0 = Palm of Hand, Wall Plane) across four rotations -- three
   in the RIGHT-hand half (0-7) and one in the LEFT-hand half (8-15) -- so
   both the finger-pointing sweep and the RIGHT/LEFT mirroring can be
   checked visually.

2. index_finger_fills.png -- the same base symbol at a fixed rotation (0)
   across all 6 fill values -- the "Six Palm Facings"
   (https://www.signwriting.org/lessons/iswa/group01/01-01-001-01.html) --
   so fill's effect (which side of the hand shows, which plane the arm
   reaches in) can be checked visually, distinct from rotation's effect.

Run with: python -m fsw_r_viz.demo
"""

from __future__ import annotations

from pathlib import Path

from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r_viz.plot_face import render_faces_grid
from fsw_r_viz.plot_hand import render_symbols_grid


def _render_rotation_sweep(output_dir: Path) -> None:
    symbols = [
        # base_hex, fill, rotation
        (HandSymbol(0x107, fill=0, rotation=0), "01-01-012 rotation=3 (RIGHT, finger up)"),  # Index Hinge
        (HandSymbol(0x107, fill=0, rotation=5), "01-08-002 rotation=2 (RIGHT, finger sideways)"),  # Index Ring Baby on Circle
        (HandSymbol(0x101, fill=0, rotation=2), "01-01-002 rotation=2 (RIGHT, finger down)"),  # Index on Circle
        (HandSymbol(0x1CD, fill=0, rotation=12), "01-09-001 rotation=12 (LEFT, mirrored)"),  # Middle Ring Baby
    ]
    output_path = output_dir / "index_finger_rotations.png"
    render_symbols_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_fill_sweep(output_dir: Path) -> None:
    fill_titles = [
        (0, "Palm, Wall"),
        (1, "Side, Wall"),
        (2, "Back, Wall"),
        (3, "Palm, Floor"),
        (4, "Side, Floor"),
        (5, "Back, Floor"),
    ]
    symbols = [
        (HandSymbol(0x100, fill=fill, rotation=0), f"01-01-001 fill={fill} ({label})")  # Index
        for fill, label in fill_titles
    ]
    output_path = output_dir / "index_finger_fills.png"
    render_symbols_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_mouth_expressions(output_dir: Path) -> None:
    # Category 4 Group 25 (Mouth/Lips): a few distinct authored expressions,
    # rendered as schematic faces so the blend-shapes are visible.
    symbols = [
        (FaceSymbol(0x33B, fill=0, rotation=0), "04-25-001 Mouth Closed Neutral"),
        (FaceSymbol(0x33E, fill=0, rotation=0), "04-25-004 Mouth Smile"),
        (FaceSymbol(0x341, fill=0, rotation=0), "04-25-007 Mouth Frown"),
        (FaceSymbol(0x344, fill=0, rotation=0), "04-25-010 Mouth Open Circle"),
        (FaceSymbol(0x34D, fill=0, rotation=0), "04-25-019 Mouth Kiss"),
    ]
    output_path = output_dir / "mouth_expressions.png"
    render_faces_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    _render_rotation_sweep(output_dir)
    _render_fill_sweep(output_dir)
    _render_mouth_expressions(output_dir)


if __name__ == "__main__":
    main()
