from __future__ import annotations

from pathlib import Path

from fsw_r.core.head_movement import HeadMovementSymbol

from fsw_r_viz.animate_head import animate_head_movement_to_gif, render_head_movement_filmstrip


def test_filmstrip_writes_png(tmp_path: Path) -> None:
    symbol = HeadMovementSymbol(0x301, fill=0, rotation=0)  # Straight Wall = nod
    output_path = tmp_path / "nod_filmstrip.png"

    render_head_movement_filmstrip(symbol, str(output_path), frames=5)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_gif_writes_animated_file(tmp_path: Path) -> None:
    symbol = HeadMovementSymbol(0x306, fill=0, rotation=0)  # Circles
    output_path = tmp_path / "circle.gif"

    animate_head_movement_to_gif(symbol, str(output_path), samples=10, fps=8)

    assert output_path.exists()
    assert output_path.read_bytes()[:4] == b"GIF8"
