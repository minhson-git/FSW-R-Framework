"""Renders Base Symbol 1 ("Index", 01-01-001) at four rotations -- three in
the RIGHT-hand half (0-7) and one in the LEFT-hand half (8-15) -- as 3D
stick-figure hands, side by side, so both the wrist angle and the
RIGHT/LEFT mirroring can be checked visually.

Run with: python -m fsw_r_viz.demo
"""

from __future__ import annotations

from pathlib import Path

from fsw_r.groups.group_01_index_finger import BaseSymbol01_01_001_Index
from fsw_r.groups.group_01_index_finger import BaseSymbol01_01_007_IndexBent

from fsw_r_viz.plot_hand import render_symbols_grid


def main() -> None:
    symbols = [
        (BaseSymbol01_01_001_Index(fill=1, rotation=0), "01-01-001 rotation=0 (RIGHT, palm out)"),
        (BaseSymbol01_01_001_Index(fill=1, rotation=5), "01-01-001 rotation=5 (RIGHT, side)"),
        (BaseSymbol01_01_001_Index(fill=1, rotation=7), "01-01-001 rotation=7 (RIGHT, back out)"),
        (BaseSymbol01_01_007_IndexBent(fill=1, rotation=0), "01-01-007 rotation=0 (LEFT, mirrored)"),
    ]

    output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "index_finger_rotations.png"

    render_symbols_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
