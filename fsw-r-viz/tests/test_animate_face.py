from __future__ import annotations

from pathlib import Path

from fsw_r.core.face_movement import FaceMovementSymbol

from fsw_r_viz.animate_face import animate_face_movement_to_gif, render_face_movement_filmstrip


def test_filmstrip_writes_png(tmp_path: Path) -> None:
    symbol = FaceMovementSymbol(0x317, fill=0, rotation=0)  # Eye Blink Single
    output_path = tmp_path / "blink_filmstrip.png"

    render_face_movement_filmstrip(symbol, str(output_path), frames=5)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_gif_writes_animated_file(tmp_path: Path) -> None:
    symbol = FaceMovementSymbol(0x368, fill=0, rotation=0)  # Jaw Movement
    output_path = tmp_path / "jaw.gif"

    animate_face_movement_to_gif(symbol, str(output_path), samples=10, fps=8)

    assert output_path.exists()
    assert output_path.read_bytes()[:4] == b"GIF8"
