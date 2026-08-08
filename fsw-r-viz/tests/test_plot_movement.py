from __future__ import annotations

from pathlib import Path

from fsw_r.core.movement_symbol import MovementSymbol

from fsw_r_viz.plot_movement import render_movement_to_file, render_movements_grid


def test_render_movement_to_file_writes_png(tmp_path: Path) -> None:
    symbol = MovementSymbol(0x22A, fill=0, rotation=0)  # 02-13-001 Straight
    output_path = tmp_path / "straight.png"

    render_movement_to_file(symbol, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_movements_grid_writes_png(tmp_path: Path) -> None:
    symbols = [
        (MovementSymbol(0x22A, fill=0, rotation=0), "Straight"),
        (MovementSymbol(0x288, fill=0, rotation=0), "Curved"),
        (MovementSymbol(0x2E3, fill=0, rotation=0), "Circle"),
    ]
    output_path = tmp_path / "grid.png"

    render_movements_grid(symbols, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
