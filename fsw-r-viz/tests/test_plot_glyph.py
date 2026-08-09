from __future__ import annotations

from pathlib import Path

from fsw_r.core.registry import symbol_from_fsw

from fsw_r_viz.plot_glyph import render_glyph, render_glyph_to_file


def test_renders_glyph_for_an_annotation_symbol(tmp_path: Path) -> None:
    # 0x361 Teeth -- an AnnotationSymbol (no 3D model) still has a real glyph.
    symbol = symbol_from_fsw("S36100")
    output_path = tmp_path / "teeth.png"

    render_glyph_to_file(symbol, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_renders_glyph_for_a_face_symbol_too(tmp_path: Path) -> None:
    # Works for any symbol, not just annotations -- 0x33e Mouth Smile.
    symbol = symbol_from_fsw("S33e00")
    glyph = render_glyph(symbol)
    assert glyph.width > 0 and glyph.height > 0


def test_glyph_differs_by_rotation() -> None:
    # Eyegaze 0x321 up vs down -- the real glyph must change with rotation.
    up = render_glyph(symbol_from_fsw("S32100"))
    down = render_glyph(symbol_from_fsw("S32104"))
    assert up.tobytes() != down.tobytes()
