"""Generates ``src/fsw_r/data/iswa_movement_glyph_sizes.json`` -- the real
ISWA glyph bounding-box size for each of Category 2 (Movement)'s 242 base
symbols, keyed by ``base_hex``. Feeds ``gen_movement_paths.py``'s
``amplitude`` assignment (this task's brief, "`amplitude` từ variation +
kích thước glyph", Part A2's preferred "cách 2").

Why a font, not the name text: ``data/iswa_base_symbol_names.json`` (Task
2) already lets us group a base symbol's own VARIATIONS together (by
``symbol_id``'s ``category-group-base`` prefix) and tells us their real
NAMES -- but this project's own A1 investigation (see PROGRESS.md's entry
for this task) found variation is NOT consistently a clean, monotonic size
label across all 242 base symbols: some variation families encode size
(Small/Medium/Large/Largest, sometimes in a DIFFERENT order than the
variation number), some encode direction (Up/Down), repeat count
(Single/Double/Triple), or an unlabeled outlier ("Combined", "Snake"). The
REAL ISWA glyph -- what SignWriting readers actually see -- sidesteps all of
that ambiguity: it is a size signal that exists whether or not the name
happens to spell it out, and it was independently spot-checked against
several of A1's "hard" cases before being adopted (see PROGRESS.md): a
"Small"/"Large" pair's glyphs really do differ in bounding-box size in the
expected direction, and even a non-size pair like "Up Sequential"/"Down
Sequential" (a direction flip, not a size difference) produces two nearly
IDENTICAL glyph sizes -- i.e. the font naturally does the right thing
(no artificial size difference invented) even where the name text alone
would have been ambiguous.

Source: the npm package ``@sutton-signwriting/font-ttf``, file
``font/SuttonSignWritingLine.ttf`` -- the SAME font
``gen_valid_combinations.py`` already reads (fetched via ``npm pack``, same
method, same id<->(base, fill, rotation) formula, re-derived here rather
than imported to keep this script runnable standalone like its sibling).

For each base symbol, reads the glyph at its OWN first valid fill (from
``valid_combinations_for()``) and rotation=0 -- an arbitrary but consistent
"canonical" glyph per base, matching the convention
``test_iswa_data.py``'s ``test_every_category_1_base_symbol_...`` already
established for Category 1. Records ``width``/``height`` (glyph bounding
box, font units) and ``max_dimension`` = ``max(width, height)`` -- the
single scalar this project uses as "glyph size" (robust to a symbol's
final orientation, which depends on ``rotation``/``plane`` and isn't fixed
per base symbol the way the glyph's own un-rotated shape is).

**Important, and the entire reason Part 0 of this task's brief exists:**
this script does NOT compare sizes ACROSS different base symbols or
different ``path_type``s -- it only records each base's own raw
``max_dimension``. The actual WITHIN-BASE, WITHIN-PATH_TYPE ratio
comparison (the only comparison Part 0 says is safe) happens in
``gen_movement_paths.py``, not here.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fsw_r.core.iswa_data import GROUP_START, valid_combinations_for  # noqa: E402

FONT_PACKAGE = "@sutton-signwriting/font-ttf"
FONT_RELATIVE_PATH = "package/font/SuttonSignWritingLine.ttf"
LINE_FONT_CODEPOINT_OFFSET = 0xF0000

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "iswa_movement_glyph_sizes.json"

EXPECTED_TOTAL = 242
_MOVEMENT_START = GROUP_START[10]
_MOVEMENT_END = GROUP_START[20] - 1

# Independently measured (see PROGRESS.md's entry for this task) -- checked
# again here so a font update or a code regression is caught immediately.
_SPOT_CHECKS: dict[int, int] = {
    0x22A: 147,  # Single Straight Movement, Wall Plane Small
    0x22B: 297,  # ... Medium
    0x22C: 417,  # ... Large
    0x22D: 497,  # ... Largest
}


def fetch_font(tmp_dir: Path) -> Path:
    """Same method as ``gen_valid_combinations.py``'s ``fetch_font()`` --
    ``npm pack`` (a real package download, not a scrape)."""
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError(f"npm not found on PATH -- required to fetch {FONT_PACKAGE}")
    subprocess.run(
        [npm, "pack", FONT_PACKAGE],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    tarballs = list(tmp_dir.glob("sutton-signwriting-font-ttf-*.tgz"))
    if len(tarballs) != 1:
        raise RuntimeError(f"expected exactly 1 tarball from npm pack, found {tarballs}")
    with tarfile.open(tarballs[0]) as tar:
        tar.extract(FONT_RELATIVE_PATH, path=tmp_dir)
    font_path = tmp_dir / FONT_RELATIVE_PATH
    if not font_path.exists():
        raise RuntimeError(f"font not found at expected path after extraction: {font_path}")
    return font_path


def _id_for(base_hex: int, fill: int, rotation: int) -> int:
    return 1 + (base_hex - 0x100) * 96 + fill * 16 + rotation


def measure_glyph(font: TTFont, base_hex: int) -> tuple[int, int, int]:
    """Returns ``(width, height, max_dimension)`` in font units, for
    ``base_hex``'s own first valid fill, rotation=0. Raises if no glyph is
    found for ANY of that base's valid fills -- never silently records a
    made-up size."""
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    fills = sorted(valid_combinations_for(base_hex).fills)
    for fill in fills:
        codepoint = _id_for(base_hex, fill, rotation=0) + LINE_FONT_CODEPOINT_OFFSET
        if codepoint not in cmap:
            continue
        glyph = glyf[cmap[codepoint]]
        if glyph.numberOfContours == 0:
            continue  # blank glyph at this fill -- try the next valid fill
        width = glyph.xMax - glyph.xMin
        height = glyph.yMax - glyph.yMin
        if width <= 0 or height <= 0:
            continue  # degenerate outline -- try the next valid fill
        return width, height, max(width, height)
    raise RuntimeError(
        f"base 0x{base_hex:x}: no non-degenerate glyph found at rotation=0 for any valid fill {fills}"
    )


def verify(sizes: dict[int, tuple[int, int, int]]) -> None:
    errors = []
    if len(sizes) != EXPECTED_TOTAL:
        errors.append(f"measured {len(sizes)} glyphs, expected {EXPECTED_TOTAL}")
    if set(sizes) != set(range(_MOVEMENT_START, _MOVEMENT_END + 1)):
        errors.append("base_hex set does not cover exactly the Category 2 range")
    for base_hex, expected_max in _SPOT_CHECKS.items():
        actual_max = sizes.get(base_hex, (0, 0, 0))[2]
        if actual_max != expected_max:
            errors.append(f"0x{base_hex:x}: max_dimension={actual_max}, expected {expected_max} (spot check)")

    print(f"total measured = {len(sizes)} (expected {EXPECTED_TOTAL})")
    print(f"spot checks: {len(_SPOT_CHECKS) - sum(1 for b in _SPOT_CHECKS if sizes.get(b, (0, 0, 0))[2] != _SPOT_CHECKS[b])}/{len(_SPOT_CHECKS)} match")

    if errors:
        print("\nVERIFICATION FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("\nAll checks passed.")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        font_path = fetch_font(tmp_dir)
        font = TTFont(font_path)
        sizes: dict[int, tuple[int, int, int]] = {}
        for base_hex in range(_MOVEMENT_START, _MOVEMENT_END + 1):
            sizes[base_hex] = measure_glyph(font, base_hex)

    verify(sizes)

    table = {
        format(base_hex, "x"): {"width": w, "height": h, "max_dimension": m} for base_hex, (w, h, m) in sizes.items()
    }
    output = {
        "_meta": {
            "source": f"{FONT_PACKAGE} font/SuttonSignWritingLine.ttf (real ISWA glyph outlines)",
            "layer": "derived -- from the real ISWA reference font, not measured/authored by this "
            "project (same tier as data/iswa_valid_combinations.json, same font)",
            "format": "base_hex (3 hex chars) -> {width, height, max_dimension} in font units, glyph "
            "at that base's own first valid fill, rotation=0",
            "warning": (
                "Raw glyph size here is NOT directly comparable across different base symbols or "
                "path_types (a Zigzag glyph is wide because it zigzags, not because it travels far -- "
                "see this task's brief, Part 0). Only gen_movement_paths.py's WITHIN-(base_symbol_id, "
                "path_type) ratio use of these numbers is valid; do not consume max_dimension directly "
                "as a cross-base amplitude."
            ),
            "count": len(table),
            "generated_by": "scripts/gen_movement_glyph_sizes.py",
        },
        **table,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nWrote {len(table)} entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
