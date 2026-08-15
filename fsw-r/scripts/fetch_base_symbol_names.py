"""Generates ``src/fsw_r/data/iswa_base_symbol_names.json`` -- the real ISWA
base-symbol NAME for each of Category 2 (Movement)'s 242 base symbols,
keyed by ``base_hex``.

Why this exists (see this task's brief, "`path_type` từ tên BASE SYMBOL",
Part 0): ``scripts/gen_movement_paths.py`` used to derive ``path_type`` from
the GROUP name (e.g. group 02-03 = "Straight Wall Plane"), but a group name
only states the *plane*, not the *trajectory shape* -- group 02-03 alone
holds 43 base symbols named Single Straight, Bend, Corner, Check, Box,
Zigzag, Peaks, Travel Rotation, ... and every one of them was silently
getting ``path_type = "straight"``. Fixing that needs each base symbol's own
NAME, which lives on signbank.org, not in any file already in this repo.

Source: ``https://www.signbank.org/iswa/<group_hex>_sg.html`` -- the 10
Category 2 group pages (see ``GROUP_PAGES`` below), each with a "BaseSymbol
Table" listing every base symbol in that group: Name, Symbol ID (the
4-part ``category-group-base-variation`` this project's own
``symbol_id_of()`` now also produces -- see the "Sửa symbol_id" task),
Symbol Key (``S<hex>``, i.e. ``base_hex``), valid fills, valid rotations.
Fetched via plain HTTP GET (``urllib.request``, stdlib -- same tool
``fetch_ground_truth.py`` already uses for a different source; signbank.org
is a live webpage, not an npm package, so ``npm pack`` doesn't apply here).

**Bẫy khi đọc file này (parsing trap, verified by hand before writing this
script, not assumed) -- same shape as Task 1's JSDoc-example trap:** each
page has a page-wide footer ``<table>`` (credits/copyright, e.g. "ISWA 2010
symbols designed by Valerie Sutton...") that sits textually AFTER the
"BaseSymbol Table" heading. A naive ``re.findall(r"<tr>(.*?)</tr>", ...)``
run on everything from that heading to end-of-file matches the footer's own
``<tr>`` too, inflating every group's row count by exactly 1 (e.g. group
02-03: 44 "rows" instead of the real 43). This script locates the specific
``<table>...</table>`` that immediately follows the "BaseSymbol Table"
heading and parses ONLY inside that span -- never to end-of-document.

If signbank.org is unreachable, this script stops and reports rather than
guessing names from glyph shapes (explicit constraint in this task's brief).
"""

from __future__ import annotations

import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of  # noqa: E402

BASE_URL = "https://www.signbank.org/iswa/{hex}_sg.html"
TABLE_HEADING = "BaseSymbol Table"

# The 10 Category 2 (Movement) groups (this task's brief, Part A2) -- global
# group numbers 11-20, i.e. GROUP_START[10:20]. Verified equal to the
# brief's own table before use, not just assumed.
_EXPECTED_GROUP_HEXES = (0x205, 0x216, 0x22A, 0x255, 0x265, 0x288, 0x2A6, 0x2B7, 0x2D5, 0x2E3)
GROUP_HEXES = GROUP_START[10:20]
if GROUP_HEXES != _EXPECTED_GROUP_HEXES:
    raise RuntimeError(
        f"GROUP_START[10:20] = {[hex(g) for g in GROUP_HEXES]} does not match this task brief's "
        f"own Part A2 table {[hex(g) for g in _EXPECTED_GROUP_HEXES]} -- GROUP_START may have "
        "changed since this script was written; stop and report rather than fetching the wrong pages."
    )

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "iswa_base_symbol_names.json"

EXPECTED_TOTAL = 242
_ROW_CELL_COUNT = 9  # Symbol, BaseSymbol, Name, Symbol ID, Symbol Key, Unicode PUA, UTF-8, Valid Fills, Valid Rotations

_ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
_CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
_TAG_RE = re.compile(r"<.*?>", re.S)


def fetch_group_page(group_hex: int) -> str:
    url = BASE_URL.format(hex=format(group_hex, "x"))
    try:
        with urllib.request.urlopen(url, timeout=20) as response:  # noqa: S310 -- fixed https:// URL, not user input
            body: bytes = response.read()
            return body.decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"could not fetch {url} ({exc}) -- signbank.org is required for this script (see its "
            "module docstring's constraint: never guess names from glyph shapes). Stopping."
        ) from exc


def parse_group_page(html: str, group_hex: int) -> list[tuple[int, str, str]]:
    """Returns ``[(base_hex, symbol_id, name), ...]`` for one group page --
    parses ONLY the ``<table>`` immediately after the "BaseSymbol Table"
    heading (see module docstring's "bẫy" note), never to end-of-document."""
    heading = html.find(TABLE_HEADING)
    if heading == -1:
        raise RuntimeError(f"group 0x{group_hex:x}: {TABLE_HEADING!r} heading not found in fetched page")
    table_start = html.find("<table", heading)
    if table_start == -1:
        raise RuntimeError(f"group 0x{group_hex:x}: no <table> found after {TABLE_HEADING!r}")
    table_end = html.find("</table>", table_start)
    if table_end == -1:
        raise RuntimeError(f"group 0x{group_hex:x}: no closing </table> found")
    body = html[table_start:table_end]

    rows = _ROW_RE.findall(body)
    entries: list[tuple[int, str, str]] = []
    for row in rows[1:]:  # rows[0] is the header row (<th>...)
        cells = _CELL_RE.findall(row)
        if len(cells) != _ROW_CELL_COUNT:
            raise RuntimeError(
                f"group 0x{group_hex:x}: row has {len(cells)} cells, expected {_ROW_CELL_COUNT} -- "
                f"table structure may have changed on signbank.org: {cells!r}"
            )
        name = _TAG_RE.sub("", cells[2]).strip()
        symbol_id = _TAG_RE.sub("", cells[3]).strip()
        key = _TAG_RE.sub("", cells[4]).strip()
        if not (key.startswith("S") and len(key) >= 4):
            raise RuntimeError(f"group 0x{group_hex:x}: malformed Symbol Key {key!r}")
        base_hex = int(key[1:], 16)
        entries.append((base_hex, symbol_id, name))
    return entries


def verify(entries: list[tuple[int, str, str]]) -> None:
    errors = []

    if len(entries) != EXPECTED_TOTAL:
        errors.append(f"parsed {len(entries)} entries total, expected {EXPECTED_TOTAL}")

    base_hexes = [e[0] for e in entries]
    if len(set(base_hexes)) != len(base_hexes):
        errors.append("duplicate base_hex values across group pages")
    expected_range = set(range(GROUP_HEXES[0], GROUP_HEXES[0] + EXPECTED_TOTAL))
    if set(base_hexes) != expected_range:
        missing = sorted(expected_range - set(base_hexes))
        extra = sorted(set(base_hexes) - expected_range)
        errors.append(f"base_hex set does not cover exactly 0x{GROUP_HEXES[0]:x}..0x{GROUP_HEXES[0] + EXPECTED_TOTAL - 1:x}: missing={missing[:5]} extra={extra[:5]}")

    # C2 (this task's brief): cross-check each row's own "Symbol ID" column
    # against this project's symbol_id_of() (Task 1, backed by the real
    # symidArr) -- two independent sources for the same 4-part id must agree.
    mismatches = []
    for base_hex, symid_from_page, name in entries:
        expected = symbol_id_of(base_hex)
        if symid_from_page != expected:
            mismatches.append((base_hex, symid_from_page, expected, name))
    if mismatches:
        errors.append(f"{len(mismatches)} base symbols where signbank's own Symbol ID column disagrees with symbol_id_of(): {mismatches[:5]}")

    for base_hex, _symid, name in entries:
        if not name:
            errors.append(f"base 0x{base_hex:x}: empty name")

    print(f"total entries = {len(entries)} (expected {EXPECTED_TOTAL})")
    print(f"symbol_id cross-check agreement = {len(entries) - len(mismatches)}/{len(entries)}")

    if errors:
        print("\nVERIFICATION FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("\nAll checks passed.")


def main() -> None:
    all_entries: list[tuple[int, str, str]] = []
    source_urls = []
    for group_hex in GROUP_HEXES:
        url = BASE_URL.format(hex=format(group_hex, "x"))
        print(f"fetching {url} ...")
        html = fetch_group_page(group_hex)
        entries = parse_group_page(html, group_hex)
        print(f"  parsed {len(entries)} base symbols")
        all_entries.extend(entries)
        source_urls.append(url)

    verify(all_entries)

    table = {format(base_hex, "x"): {"name": name, "symbol_id": symid} for base_hex, symid, name in all_entries}

    output = {
        "_meta": {
            "source": "https://www.signbank.org/iswa/ (per-group BaseSymbol Table pages)",
            "source_urls": source_urls,
            "fetched": datetime.date.today().isoformat(),
            "layer": (
                "derived -- from the real ISWA reference (signbank.org), not measured/authored "
                "by this project (same tier as data/iswa_symbol_ids.json, different source)"
            ),
            "format": "base_hex (3 hex chars) -> {name, symbol_id} -- symbol_id is signbank's own "
            "column, cross-checked against symbol_id_of() at generation time (see verify())",
            "scope": "Category 2 (Movement) only, 242 base symbols -- see this task's brief's Part "
            "A2 for exactly which 10 groups. Reusable for other categories later at similar "
            "cost (same fetch/parse mechanism), not done here to stay in this task's scope.",
            "count": len(table),
            "generated_by": "scripts/fetch_base_symbol_names.py",
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
