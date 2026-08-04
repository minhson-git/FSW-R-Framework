"""Generate ``src/fsw_r/data/iswa_valid_combinations.json`` -- the ground
truth for which (base, fill, rotation) ISWA symbol combinations actually
exist.

Why a font, not a scrape: the official ISWA TrueType fonts published by
sutton-signwriting contain exactly one glyph per symbol that actually
exists. Their cmap (codepoint -> glyph) is therefore the authoritative list
of valid symbol ids -- reading it is equivalent to asking the same font
renderer every SignWriting tool already trusts "does this symbol exist?".

Source: the npm package ``@sutton-signwriting/font-ttf``, file
``font/SuttonSignWritingLine.ttf``. This script fetches it via ``npm pack``
(a real package download, not a web scrape) into a temp directory, so it can
be re-run to reproduce ``iswa_valid_combinations.json`` byte-for-byte.

Codepoint offset (``font/font.js``, ``symbolLine``): line-font codepoint =
id + 0xF0000. (The fill font uses +0x100000 and was verified separately to
cover the exact same id set -- see PROGRESS.md -- so only the line font is
read here.)

id <-> (base, fill, rotation) (inverse of ``convert.key2id`` in
``@sutton-signwriting/core``, ``src/convert/index.js``):

    id = 1 + (base - 0x100) * 96 + fill * 16 + rotation

    code = id - 1
    base = code // 96 + 0x100
    fill = (code % 96) // 16
    rotation = code % 16

``id == 0`` is the special blank symbol ``S00000`` (not a real ISWA base
symbol) and is excluded.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import defaultdict
from pathlib import Path

from fontTools.ttLib import TTFont

FONT_PACKAGE = "@sutton-signwriting/font-ttf"
FONT_RELATIVE_PATH = "package/font/SuttonSignWritingLine.ttf"
LINE_FONT_CODEPOINT_OFFSET = 0xF0000

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "iswa_valid_combinations.json"

# Independently-verified expected results (see PROGRESS.md) -- the script
# checks its own output against these and fails loudly on any mismatch,
# rather than silently producing a different table.
EXPECTED_TOTAL_SYMBOLS = 37811
EXPECTED_TOTAL_BASE_SYMBOLS = 652
EXPECTED_CAT1_FULL_BASES = 253  # of 261, with all 6 fills x 16 rotations
EXPECTED_CAT1_EXCEPTIONS: dict[str, list[int]] = {
    "14d": [1],
    "14f": [1],
    "151": [1],
    "15b": [0, 1, 2, 3],
    "15c": [1],
    "15e": [1],
    "1f6": [1],
    "204": [1],
}
CAT1_BASE_START = 0x100
CAT1_BASE_END = 0x205  # exclusive


def fetch_font(tmp_dir: Path) -> Path:
    """Download the font package via ``npm pack`` (a real package fetch,
    not a scrape) and extract just the line font."""
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm not found on PATH -- required to fetch @sutton-signwriting/font-ttf")
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


def decode_symbol_ids(font_path: Path) -> tuple[list[int], str | None]:
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    ids = sorted(
        codepoint - LINE_FONT_CODEPOINT_OFFSET
        for codepoint in cmap
        if codepoint >= LINE_FONT_CODEPOINT_OFFSET
    )
    version = None
    if "name" in font:
        version = font["name"].getDebugName(5)  # nameID 5 = version string
    return ids, version


def id_to_base_fill_rotation(symbol_id: int) -> tuple[int, int, int]:
    code = symbol_id - 1
    base = code // 96 + 0x100
    fill = (code % 96) // 16
    rotation = code % 16
    return base, fill, rotation


def build_table(symbol_ids: list[int]) -> dict[str, dict[str, list[int]]]:
    fills_by_base: dict[int, set[int]] = defaultdict(set)
    rotations_by_base: dict[int, set[int]] = defaultdict(set)
    for symbol_id in symbol_ids:
        if symbol_id == 0:
            continue  # S00000, the blank symbol -- not a real base symbol
        base, fill, rotation = id_to_base_fill_rotation(symbol_id)
        fills_by_base[base].add(fill)
        rotations_by_base[base].add(rotation)

    table: dict[str, dict[str, list[int]]] = {}
    for base in sorted(fills_by_base):
        table[format(base, "x")] = {
            "fills": sorted(fills_by_base[base]),
            "rotations": sorted(rotations_by_base[base]),
        }
    return table


def verify(table: dict[str, dict[str, list[int]]], font_version: str | None) -> None:
    total_symbols = sum(
        len(entry["fills"]) * len(entry["rotations"]) for entry in table.values()
    )
    total_bases = len(table)

    errors = []
    if total_symbols != EXPECTED_TOTAL_SYMBOLS:
        errors.append(f"total_symbols = {total_symbols}, expected {EXPECTED_TOTAL_SYMBOLS}")
    if total_bases != EXPECTED_TOTAL_BASE_SYMBOLS:
        errors.append(f"total_base_symbols = {total_bases}, expected {EXPECTED_TOTAL_BASE_SYMBOLS}")

    cat1_full = 0
    cat1_exceptions: dict[str, list[int]] = {}
    for base in range(CAT1_BASE_START, CAT1_BASE_END):
        key = format(base, "x")
        entry = table.get(key)
        if entry is None:
            errors.append(f"Category 1 base {key!r} missing from table entirely")
            continue
        if len(entry["rotations"]) != 16:
            errors.append(f"Category 1 base {key!r} has {len(entry['rotations'])} rotations, expected 16")
        if len(entry["fills"]) == 6:
            cat1_full += 1
        else:
            cat1_exceptions[key] = entry["fills"]

    if cat1_full != EXPECTED_CAT1_FULL_BASES:
        errors.append(f"Category 1 full-combination bases = {cat1_full}, expected {EXPECTED_CAT1_FULL_BASES}")
    if cat1_exceptions != EXPECTED_CAT1_EXCEPTIONS:
        errors.append(
            f"Category 1 exceptions = {cat1_exceptions}, expected {EXPECTED_CAT1_EXCEPTIONS}"
        )

    ratio = total_symbols / (EXPECTED_TOTAL_BASE_SYMBOLS * 6 * 16)
    print(f"total_symbols = {total_symbols} (expected {EXPECTED_TOTAL_SYMBOLS})")
    print(f"total_base_symbols = {total_bases} (expected {EXPECTED_TOTAL_BASE_SYMBOLS})")
    print(f"valid ratio = {ratio:.1%} (expected 60.4%)")
    print(f"Category 1 full-combination bases = {cat1_full}/261 (expected {EXPECTED_CAT1_FULL_BASES}/261)")
    print(f"Category 1 exceptions = {cat1_exceptions}")
    print(f"font version (name id 5) = {font_version!r}")

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
        symbol_ids, font_version = decode_symbol_ids(font_path)

    table = build_table(symbol_ids)
    verify(table, font_version)

    output = {
        "_meta": {
            "source": f"{FONT_PACKAGE} SuttonSignWritingLine.ttf",
            "font_version": font_version,
            "total_symbols": sum(
                len(entry["fills"]) * len(entry["rotations"]) for entry in table.values()
            ),
            "total_base_symbols": len(table),
            "generated_by": "scripts/gen_valid_combinations.py",
        },
        **table,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
