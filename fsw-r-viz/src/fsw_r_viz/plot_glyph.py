"""Renders the real 2D ISWA glyph for ANY fsw_r symbol, via the reference
``signwriting`` renderer (the same font/engine the notation is defined by).

This is the universal, no-guess coverage: whatever a symbol is -- a hand, a
movement, a facial expression, or an ``AnnotationSymbol`` we haven't modelled
in 3D (teeth, ears, hair, neck, airflow...) -- its authoritative appearance
is its ISWA glyph, and that we can always draw. So every one of the 110
Category-4 bases (and every other category) is at minimum displayable
faithfully here, with nothing invented.

The 3D renderers (plot_hand / plot_face / plot_movement) are the richer,
modelled views; this glyph view is the honest fallback and cross-check.
"""

from __future__ import annotations

import os
from typing import Sequence

# signwriting.visualizer calls os.register_at_fork at import time, which only
# exists on POSIX -- shim it so the reference renderer imports on Windows too.
if not hasattr(os, "register_at_fork"):
    setattr(os, "register_at_fork", lambda **kwargs: None)

from PIL import Image, ImageDraw, ImageFont

from signwriting.visualizer.visualize import visualize_sign

from fsw_r.core.renderable_symbol import FSWRenderableSymbol


def _label_font(size: int = 18) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """A readable label font, falling back to PIL's bitmap default if no
    TrueType font is available on the machine."""
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fsw_key(symbol: FSWRenderableSymbol) -> str:
    return f"S{symbol.base_hex:03x}{symbol.fill:x}{symbol.rotation:x}"


def render_glyph(symbol: FSWRenderableSymbol, height: int = 220) -> Image.Image:
    """The symbol's real ISWA glyph as a cropped, smoothly-upscaled RGBA
    image (antialiased render + LANCZOS resize, so it reads cleanly rather
    than as blocky pixels)."""
    raw = visualize_sign(f"M500x500{_fsw_key(symbol)}480x480", antialiasing=True).convert("RGBA")
    bbox = raw.getbbox()
    cropped = raw.crop(bbox) if bbox else raw
    scale = height / max(cropped.size)
    out: Image.Image = cropped.resize(
        (max(1, int(cropped.width * scale)), max(1, int(cropped.height * scale))),
        Image.Resampling.LANCZOS,
    )
    return out


def render_glyph_to_file(symbol: FSWRenderableSymbol, output_path: str, title: str | None = None) -> None:
    render_glyphs_grid([(symbol, title or f"{symbol.symbol_id}")], output_path)


def render_glyphs_grid(symbols: Sequence[tuple[FSWRenderableSymbol, str]], output_path: str, height: int = 200) -> None:
    font = _label_font()
    glyphs = [(render_glyph(s, height), title) for s, title in symbols]
    pad, label_h = 16, 30
    cell_w = max(g.width for g, _ in glyphs) + 2 * pad
    cell_h = max(g.height for g, _ in glyphs) + 2 * pad + label_h
    canvas = Image.new("RGB", (cell_w * len(glyphs), cell_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for i, (glyph, title) in enumerate(glyphs):
        gx = i * cell_w + (cell_w - glyph.width) // 2
        canvas.paste(glyph, (gx, pad + label_h), glyph)
        draw.text((i * cell_w + pad, 8), title, fill=(0, 0, 0), font=font)
    canvas.save(output_path)
