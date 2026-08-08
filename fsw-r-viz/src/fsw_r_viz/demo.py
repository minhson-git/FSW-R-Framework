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

3. timeline/frame_NNN.png -- a numbered PNG sequence sampling a moving
   MVP-1 SignTimeline (one real Category 1 hand symbol + one real
   Category 2 movement symbol) at 25 fps -- the first visual evidence the
   framework produces MOTION, not just a static pose.

Run with: python -m fsw_r_viz.demo
"""

from __future__ import annotations

from pathlib import Path

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.timeline.build import build_timeline
from fsw_r_viz.plot_hand import render_symbols_grid
from fsw_r_viz.render_timeline import render_timeline_to_pngs


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


def _render_timeline_demo(output_dir: Path) -> None:
    # A real, MVP-1-scoped FSW sign: Index (01-01-001, base 0x100) at
    # signbox (480, 480), plus a real Category 2 movement symbol --
    # Straight Wall Plane (02-13-002, base 0x22a) -- fill=0, rotation=0.
    fsw = "M500x500S10010480x480S22a10500x500"
    positioned_symbols = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned_symbols)

    timeline_dir = output_dir / "timeline"
    paths = render_timeline_to_pngs(timeline, str(timeline_dir))
    print(f"Saved {len(paths)} frames to {timeline_dir} (from FSW {fsw!r})")


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    _render_rotation_sweep(output_dir)
    _render_fill_sweep(output_dir)
    _render_timeline_demo(output_dir)


if __name__ == "__main__":
    main()
