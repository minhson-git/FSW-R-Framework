from __future__ import annotations

from pathlib import Path

from fsw_r.core.movement_symbol import MovementSymbol

from fsw_r_viz.animate_movement import animate_movement_to_gif, render_movement_filmstrip


def test_filmstrip_writes_png(tmp_path: Path) -> None:
    symbol = MovementSymbol(0x2E3, fill=0, rotation=0)  # Circle
    output_path = tmp_path / "circle_filmstrip.png"

    render_movement_filmstrip(symbol, str(output_path), frames=5, samples=24)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_gif_writes_animated_file(tmp_path: Path) -> None:
    symbol = MovementSymbol(0x22A, fill=0, rotation=0)  # Straight
    output_path = tmp_path / "straight.gif"

    animate_movement_to_gif(symbol, str(output_path), samples=12, fps=8)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    # A GIF starts with the "GIF8" magic bytes -- confirm it's really a GIF.
    assert output_path.read_bytes()[:4] == b"GIF8"
