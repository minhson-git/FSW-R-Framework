from __future__ import annotations

from pathlib import Path

from fsw_r.core.head_symbol import HeadSymbol

from fsw_r_viz.plot_head import render_head_to_file, render_heads_grid


def test_render_head_to_file_writes_png(tmp_path: Path) -> None:
    symbol = HeadSymbol(0x308, fill=0, rotation=0)  # Nose up
    output_path = tmp_path / "head.png"

    render_head_to_file(symbol, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_heads_grid_writes_png(tmp_path: Path) -> None:
    symbols = [
        (HeadSymbol(0x308, fill=0, rotation=0), "up"),
        (HeadSymbol(0x308, fill=0, rotation=4), "down"),
        (HeadSymbol(0x2FF, fill=0, rotation=0), "neutral"),
    ]
    output_path = tmp_path / "grid.png"

    render_heads_grid(symbols, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
