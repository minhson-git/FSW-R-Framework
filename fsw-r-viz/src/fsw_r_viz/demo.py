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

from fsw_r.core.registry import symbol_from_fsw
from fsw_r_viz.plot_hand import render_symbols_grid


def _render_rotation_sweep(output_dir: Path) -> None:
    symbols = [
        (symbol_from_fsw("S10b03"), "01-01-012 rotation=3 (RIGHT, finger up)"),  # Index Hinge
        (symbol_from_fsw("S1bb02"), "01-08-002 rotation=2 (RIGHT, finger sideways)"),  # Index Ring Baby on Circle
        (symbol_from_fsw("S10102"), "01-01-002 rotation=2 (RIGHT, finger down)"),  # Index on Circle
        (symbol_from_fsw("S1cd0c"), "01-09-001 rotation=12 (LEFT, mirrored)"),  # Middle Ring Baby
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
        (symbol_from_fsw(f"S100{fill}0"), f"01-01-001 fill={fill} ({label})")  # Index
        for fill, label in fill_titles
    ]
    output_path = output_dir / "index_finger_fills.png"
    render_symbols_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    _render_rotation_sweep(output_dir)
    _render_fill_sweep(output_dir)


if __name__ == "__main__":
    main()
