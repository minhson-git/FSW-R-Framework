from __future__ import annotations

from pathlib import Path

from fsw_r.core.face_symbol import FaceSymbol

from fsw_r_viz.plot_face import render_face_to_file, render_faces_grid


def test_render_face_to_file_writes_png(tmp_path: Path) -> None:
    symbol = FaceSymbol(0x33E, fill=0, rotation=0)  # Mouth Smile
    output_path = tmp_path / "smile.png"

    render_face_to_file(symbol, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_tongue_symbol_writes_png(tmp_path: Path) -> None:
    symbol = FaceSymbol(0x359, fill=0, rotation=0)  # Tongue Sticks Out Far
    output_path = tmp_path / "tongue.png"

    render_face_to_file(symbol, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_faces_grid_writes_png(tmp_path: Path) -> None:
    symbols = [
        (FaceSymbol(0x33E, fill=0, rotation=0), "Smile"),
        (FaceSymbol(0x341, fill=0, rotation=0), "Frown"),
        (FaceSymbol(0x344, fill=0, rotation=0), "Open"),
    ]
    output_path = tmp_path / "grid.png"

    render_faces_grid(symbols, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
