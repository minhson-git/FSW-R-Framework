"""Generates ``src/fsw_r/data/iswa_symbol_ids.json`` -- the ground truth for
ISWA's own standard Symbol ID (``category-group-base-variation``, e.g.
``"01-01-001-01"``), keyed by ``base_hex``.

Why this exists (see this task's brief, "Sửa symbol_id dùng symidArr chuẩn",
Part 0): ``core/iswa_data.py``'s old ``symbol_id_of()`` SUYED the id from
``GROUP_START`` (a framework-internal, globally-numbered group table) and
never had a variation field at all -- 328/652 base symbols' displayed id
didn't match the real ISWA id, for two independent reasons: (1) ISWA numbers
groups PER CATEGORY (1-10 within each category), not globally 1-30, and (2)
consecutive ``base_hex`` values can be VARIATIONS of the same base symbol
(e.g. 0x216/0x217 are both "02-02-001", variations 01/02) -- something
``GROUP_START``-based counting has no way to know, so it silently drifted
every base symbol after the first multi-variation one in each group.

Source: the npm package ``@sutton-signwriting/core``, file
``src/convert/symidArr.js`` -- a real 652-element array, in ``base_hex``
order starting at ``0x100``, of 6-digit "minimized" symbol ids (e.g.
``"101011"`` decodes to category=1, group=01, base=001, variation=1, i.e.
``symidMax()``'s own format in that same package: ``"01-01-001-01"``).
Fetched via ``npm pack`` (a real package download, not a scrape) into a temp
directory, same method ``gen_valid_combinations.py`` uses for the ISWA font.

**Bẫy khi đọc file này (this task's brief, Part A2) -- verified by hand
before writing this script, not assumed:** the file's own JSDoc comment
gives ``"101011"`` as a *documentation example* directly above the array
literal:

    /**
     * An array of symbol IDs in minimized format such as "101011"
     */
    const symidArr = [
    "101011",
    "101021",
    ...

A naive ``re.findall(r'"(\\d{6})"', full_file_text)`` matches that
documentation example TOO, yielding 653 "elements" with the first two both
``"101011"`` -- which looks exactly like an off-by-one duplicate bug, but
isn't one: it's a parsing artifact from including prose, not data. This
script parses ONLY the text between ``const symidArr = [`` and the array's
closing ``]``, and asserts exactly 652 elements before doing anything else
with the result.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fsw_r.core.iswa_data import GROUP_START, ISWA_LAST_BASE, category_of  # noqa: E402

CORE_PACKAGE = "@sutton-signwriting/core"
SYMID_ARR_RELATIVE_PATH = "package/src/convert/symidArr.js"
ARRAY_START_MARKER = "const symidArr = ["

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "iswa_symbol_ids.json"

EXPECTED_TOTAL = 652  # GROUP_START[0] (0x100) to ISWA_LAST_BASE (0x38b) inclusive
EXPECTED_FIRST_ENTRY = "101011"  # base 0x100 -> category=1, group=01, base=001, variation=1
# Independently measured from the real symidArr (see this task's brief Part
# D3) -- the brief's own text separately states "95 base có nhiều hơn một
# variation"; re-measured here from the actual array and found to be 94, not
# 95 (see PROGRESS.md's entry for this task for the honest discrepancy note
# -- reporting the measured number, not silently matching the brief's).
EXPECTED_UNIQUE_BASE_SYMBOLS = 469
EXPECTED_MULTI_VARIATION_BASES = 94


def fetch_symid_arr_source(tmp_dir: Path) -> Path:
    """Download the package via ``npm pack`` and extract just symidArr.js."""
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError(f"npm not found on PATH -- required to fetch {CORE_PACKAGE}")
    subprocess.run(
        [npm, "pack", CORE_PACKAGE],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    tarballs = list(tmp_dir.glob("sutton-signwriting-core-*.tgz"))
    if len(tarballs) != 1:
        raise RuntimeError(f"expected exactly 1 tarball from npm pack, found {tarballs}")
    with tarfile.open(tarballs[0]) as tar:
        tar.extract(SYMID_ARR_RELATIVE_PATH, path=tmp_dir)
    source_path = tmp_dir / SYMID_ARR_RELATIVE_PATH
    if not source_path.exists():
        raise RuntimeError(f"symidArr.js not found at expected path after extraction: {source_path}")
    return source_path


def parse_symid_arr(source_path: Path) -> list[str]:
    """Parses ONLY the array body (see module docstring's "bẫy" note) --
    never runs a regex over the whole file, which would also match the
    JSDoc example above the array."""
    text = source_path.read_text(encoding="utf-8")
    start = text.find(ARRAY_START_MARKER)
    if start == -1:
        raise RuntimeError(f"could not find {ARRAY_START_MARKER!r} in {source_path}")
    body = text[start + len(ARRAY_START_MARKER):]
    end = body.find("]")
    if end == -1:
        raise RuntimeError(f"could not find the closing ']' of symidArr in {source_path}")
    body = body[:end]
    items = re.findall(r'"(\d{6})"', body)
    return items


def decode_symid_min(symid_min: str) -> tuple[int, int, int, int]:
    """``"101011"`` -> (category=1, group=1, base=1, variation=1) -- the
    same digit layout as ``@sutton-signwriting/core``'s own ``symidMax()``
    (1 digit category + 2 digit group + 2 digit base + 1 digit variation)."""
    category = int(symid_min[0])
    group = int(symid_min[1:3])
    base = int(symid_min[3:5])
    variation = int(symid_min[5])
    return category, group, base, variation


def build_table(items: list[str]) -> dict[str, str]:
    table: dict[str, str] = {}
    for offset, symid_min in enumerate(items):
        base_hex = GROUP_START[0] + offset
        table[format(base_hex, "x")] = symid_min
    return table


def verify(items: list[str], table: dict[str, str]) -> None:
    errors = []

    if len(items) != EXPECTED_TOTAL:
        errors.append(
            f"parsed {len(items)} symidArr elements, expected {EXPECTED_TOTAL} -- "
            f"if this is 653, the JSDoc-example parsing trap (see module docstring) is back"
        )
    if items and items[0] != EXPECTED_FIRST_ENTRY:
        errors.append(f"symidArr[0] = {items[0]!r}, expected {EXPECTED_FIRST_ENTRY!r} (base 0x100)")

    last_base_hex = GROUP_START[0] + len(items) - 1
    if last_base_hex != ISWA_LAST_BASE:
        errors.append(
            f"last base_hex covered = 0x{last_base_hex:03x}, expected 0x{ISWA_LAST_BASE:03x} "
            f"(ISWA_LAST_BASE) -- symidArr's length no longer matches the full ISWA range"
        )

    base_symbol_ids = {symid_min[:5] for symid_min in items}  # category+group+base, no variation
    if len(base_symbol_ids) != EXPECTED_UNIQUE_BASE_SYMBOLS:
        errors.append(
            f"{len(base_symbol_ids)} unique base symbols (ignoring variation), "
            f"expected {EXPECTED_UNIQUE_BASE_SYMBOLS}"
        )
    variation_counts: dict[str, int] = {}
    for symid_min in items:
        key = symid_min[:5]
        variation_counts[key] = variation_counts.get(key, 0) + 1
    multi_variation = sum(1 for count in variation_counts.values() if count > 1)
    if multi_variation != EXPECTED_MULTI_VARIATION_BASES:
        errors.append(f"{multi_variation} base symbols have >1 variation, expected {EXPECTED_MULTI_VARIATION_BASES}")

    # D4 (this task's brief): category_of() -- derived from GROUP_START, the
    # framework's OWN category-boundary table -- must agree with symidArr's
    # own category digit for every single base. If this ever fails, the
    # category-boundary table itself is wrong, not just the group/variation
    # numbering this task fixes -- stop rather than silently building a table
    # that disagrees with the rest of the codebase about what category a
    # base symbol is in.
    category_mismatches = []
    for key, symid_min in table.items():
        base_hex = int(key, 16)
        expected_category, _group, _base, _variation = decode_symid_min(symid_min)
        actual_category = category_of(base_hex)
        if expected_category != actual_category:
            category_mismatches.append((key, expected_category, actual_category))
    if category_mismatches:
        errors.append(
            f"{len(category_mismatches)} base symbols where symidArr's category digit "
            f"disagrees with category_of() (GROUP_START-derived): {category_mismatches[:10]}"
        )

    print(f"total entries = {len(items)} (expected {EXPECTED_TOTAL})")
    print(f"unique base symbols (no variation) = {len(base_symbol_ids)} (expected {EXPECTED_UNIQUE_BASE_SYMBOLS})")
    print(f"base symbols with >1 variation = {multi_variation} (expected {EXPECTED_MULTI_VARIATION_BASES})")
    print(f"category_of() agreement with symidArr = {len(table) - len(category_mismatches)}/{len(table)}")

    if errors:
        print("\nVERIFICATION FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("\nAll checks passed.")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        source_path = fetch_symid_arr_source(tmp_dir)
        items = parse_symid_arr(source_path)

    table = build_table(items)
    verify(items, table)

    base_symbol_ids = {symid_min[:5] for symid_min in items}
    variation_counts: dict[str, int] = {}
    for symid_min in items:
        key = symid_min[:5]
        variation_counts[key] = variation_counts.get(key, 0) + 1
    multi_variation = sum(1 for count in variation_counts.values() if count > 1)

    output = {
        "_meta": {
            "source": f"{CORE_PACKAGE} src/convert/symidArr.js",
            "layer": "derived -- from the real ISWA reference library's own symbol-id "
            "array, not measured/authored by this project (contrast with "
            "iswa_valid_combinations.json, derived from the ISWA font's cmap -- same "
            "'derived from a real external source' tier, different source)",
            "format": "base_hex (3 hex chars) -> 6-digit minimized symid "
            "('cgg bb v': 1-digit category, 2-digit group-within-category, "
            "2-digit base-within-group, 1-digit variation), matching "
            "@sutton-signwriting/core's own symidMax() input format",
            "total_entries": len(table),
            "unique_base_symbols": len(base_symbol_ids),
            "base_symbols_with_multiple_variations": multi_variation,
            "note": (
                "652 base_hex values correspond to only 469 real ISWA base symbols -- "
                f"{multi_variation} base symbols have more than one variation "
                "(consecutive base_hex codes sharing the same category-group-base, "
                "differing only in the variation digit). See PROGRESS.md's entry for "
                "this task for the full before/after comparison."
            ),
            "generated_by": "scripts/gen_symbol_ids.py",
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
