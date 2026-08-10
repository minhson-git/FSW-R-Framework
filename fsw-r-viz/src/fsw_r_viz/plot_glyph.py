"""Renders the real 2D ISWA glyph for ANY fsw_r symbol, via the reference
``signwriting`` renderer (the same font/engine the notation is defined by).

This is the universal, no-guess coverage: whatever a symbol is -- a hand, a
movement, a facial expression, an ``AnnotationSymbol`` we haven't modelled
in 3D (teeth, ears, hair, neck, airflow...), or a Category 3 (Dynamics)
symbol that renders nothing of its own at all -- its authoritative
appearance is its ISWA glyph, and that we can always draw. So every one of
the 110 Category-4 bases (and every other category, rendering contract or
not) is at minimum displayable faithfully here, with nothing invented.
Takes the ``FSWBaseSymbol`` marker, not ``FSWRenderableSymbol`` -- this is
the one place in ``fsw-r-viz`` that deliberately wants the widest type,
matching its own "ANY symbol" claim (contrast ``plot_hand.py``, which wants
``FSWHandRenderable`` specifically, the narrowest type, for the opposite
reason).

The 3D renderers (plot_hand / plot_face / plot_movement) are the richer,
modelled views; this glyph view is the honest fallback and cross-check.
"""

from __future__ import annotations

import os
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

# signwriting.visualizer calls os.register_at_fork at import time, which only
# exists on POSIX -- shim it so the reference renderer imports on Windows too.
# TEMPORARY, restored right after: the real CPython concurrent.futures.thread
# (imported by pose_format/mediapipe elsewhere in this process, see
# export/pose_export.py) relies on the REAL os.register_at_fork actually
# registering fork-safety hooks on locks (a threading.Lock ends up missing
# _at_fork_reinit otherwise) -- leaving a fake permanent no-op in place after
# this import corrupts concurrent.futures for every later import in the same
# process (concurrent.futures.thread's own import fails with AttributeError,
# and whatever swallows that leaves ThreadPoolExecutor unbound in
# sys.modules['concurrent.futures'] for the rest of the process -- found by
# tests/test_render_pose_video.py failing only when run after this module).
# Windows genuinely has no os.register_at_fork, so restoring "doesn't exist"
# after this one import is the honest state, not a regression.
_had_register_at_fork = hasattr(os, "register_at_fork")
if not _had_register_at_fork:
    setattr(os, "register_at_fork", lambda **kwargs: None)

from signwriting.visualizer.visualize import visualize_sign  # noqa: E402

if not _had_register_at_fork:
    delattr(os, "register_at_fork")

from fsw_r.core.fsw_base_symbol import FSWBaseSymbol  # noqa: E402


def _label_font(size: int = 18) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """A readable label font, falling back to PIL's bitmap default if no
    TrueType font is available on the machine."""
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fsw_key(symbol: FSWBaseSymbol) -> str:
    return f"S{symbol.base_hex:03x}{symbol.fill:x}{symbol.rotation:x}"


def render_glyph(symbol: FSWBaseSymbol, height: int = 220) -> Image.Image:
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


def render_glyph_to_file(symbol: FSWBaseSymbol, output_path: str, title: str | None = None) -> None:
    render_glyphs_grid([(symbol, title or f"{symbol.symbol_id}")], output_path)


def render_glyphs_grid(symbols: Sequence[tuple[FSWBaseSymbol, str]], output_path: str, height: int = 200) -> None:
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
