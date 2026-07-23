from __future__ import annotations

from pathlib import Path

from fsw_r.groups.group_01_index_finger import BaseSymbol01_01_001_Index

from fsw_r_viz.plot_hand import render_symbol_to_file, render_symbols_grid


def test_render_symbol_to_file_writes_png(tmp_path: Path) -> None:
    symbol = BaseSymbol01_01_001_Index(fill=1, rotation=0)
    output_path = tmp_path / "index.png"

    render_symbol_to_file(symbol, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_symbols_grid_writes_png(tmp_path: Path) -> None:
    symbols = [
        (BaseSymbol01_01_001_Index(fill=1, rotation=0), "rotation=0 (RIGHT)"),
        (BaseSymbol01_01_001_Index(fill=1, rotation=2), "rotation=2 (RIGHT)"),
        (BaseSymbol01_01_001_Index(fill=1, rotation=10), "rotation=10 (LEFT)"),
    ]
    output_path = tmp_path / "grid.png"

    render_symbols_grid(symbols, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
