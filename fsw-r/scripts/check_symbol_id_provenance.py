"""Source-provenance audit for the paper's "built from the correct ISWA
sources" claim.

Three bugs of ONE class -- a COARSE source was used where the EXACT
per-symbol source was already available and free to read:

    #1  movement path_type / plane / is_hit  <-  the GROUP's name
        (every symbol in a group gets the same value, e.g. all 43 symbols
        of group 13 "Straight Wall Plane" are path_type=straight -- the
        Zigzag and Box ones included).
        EXACT SOURCE, available: each base symbol's OWN ISWA name and its
        own Symbol ID base/variation field (signbank.org's ISWA 2010 HTML
        reference; the same source gen_body_poses.py/gen_face_poses.py
        already use for Categories 4/5).

    #2  movement amplitude = 10.0, a single constant for all 242 symbols.
        EXACT SOURCE, available: the ISWA font glyph's own size. ISWA
        writes movement magnitude INTO the glyph -- "... Small / Medium /
        Large / Largest" are four separate base symbols drawn at four
        sizes -- and the project already downloads that font in
        scripts/gen_valid_combinations.py.

    #3  symbol_id  <-  core/iswa_data.py's own reconstructed GROUP_START
        table, which numbers groups GLOBALLY (1-30) and has no variation
        field.
        EXACT SOURCE, available: @sutton-signwriting/core's ``symidArr``.

This script only produces EVIDENCE; it changes no data. What it can and
cannot show is stated per section -- in particular it does NOT claim to
know the correct path_type for all 242 movement symbols. It shows that
the stored value CONTRADICTS the symbol's own ISWA name, and that a
finer-grained source exists and is already a project dependency.

Run:
    python scripts/check_symbol_id_provenance.py            # all three
    python scripts/check_symbol_id_provenance.py --bug 1    # just one

Needs network: ``npm pack`` (@sutton-signwriting/core, @sutton-signwriting/
font-ttf) and signbank.org -- same reproducible-source approach as
scripts/gen_valid_combinations.py.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import statistics
import subprocess
import tarfile
import tempfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from fontTools.ttLib import TTFont

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of, valid_combinations_for

_CATEGORY_NAME = {
    1: "Hands",
    2: "Movement",
    3: "Dynamics",
    4: "Head & Face",
    5: "Trunk & Limb",
    6: "Location",
    7: "Punctuation",
}

# Category 2 spans global groups 11-20 (GROUP_START indices 10-19).
_CAT2_FIRST_GROUP = 11
_CAT2_LAST_GROUP = 20

_MOVEMENT_PATHS = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "movement_paths.json"

_FONT_PACKAGE = "@sutton-signwriting/font-ttf"
_FONT_RELATIVE_PATH = "package/font/SuttonSignWritingLine.ttf"
_LINE_FONT_CODEPOINT_OFFSET = 0xF0000

_SIGNBANK_GROUP_URL = "https://www.signbank.org/iswa/{start:x}_sg.html"
# One row of signbank's "BaseSymbol Table": the base hex (in the link to
# that symbol's own page), the real per-symbol NAME, and the canonical
# Symbol ID "CC-GG-BBB-VV".
_BASESYMBOL_ROW = re.compile(
    r"<td><a href=\"([0-9a-f]+)/\1_bs\.html\">\s*BaseSymbol_\d+</a></td>"
    r"<td>([^<]*)</td><td>(\d\d)-(\d\d)-(\d\d\d)-(\d\d)</td>",
    re.S,
)


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------
def _npm_pack(package: str, member: str, dest: Path) -> Path:
    """Fetch ``package`` via ``npm pack`` (a real package download, not a
    web scrape) and extract one member. Same mechanism as
    scripts/gen_valid_combinations.py."""
    npm = shutil.which("npm")
    if npm is None:
        raise SystemExit(f"npm not found on PATH -- cannot fetch {package}")
    subprocess.run([npm, "pack", package], cwd=dest, check=True, capture_output=True)
    tarballs = list(dest.glob("*.tgz"))
    if len(tarballs) != 1:
        raise SystemExit(f"expected exactly 1 tarball from `npm pack {package}`, found {tarballs}")
    with tarfile.open(tarballs[0]) as tar:
        tar.extract(member, path=dest)  # noqa: S202 -- trusted npm package
    extracted = dest / member
    if not extracted.exists():
        raise SystemExit(f"{member} missing after extracting {package}")
    return extracted


def fetch_symid_arr() -> list[str]:
    """The canonical 652-entry ``symidArr`` from ``@sutton-signwriting/core``.

    ``symidArr[i]`` (i = base_hex - 0x100) is a 6-char code ``C GG BB V``:
    category, PER-CATEGORY group (restarts at 01 each category), base
    number, and VARIATION."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        convert_path = _npm_pack("@sutton-signwriting/core", "package/convert/convert.cjs", tmp_path)
        convert = convert_path.read_text(encoding="utf-8")
    match = re.search(r"const symidArr = (\[.*?\]);", convert, re.S)
    if match is None:
        raise SystemExit("could not locate symidArr in @sutton-signwriting/core")
    symid_arr: list[str] = json.loads(match.group(1))
    return symid_arr


def fetch_signbank_names(first_group: int, last_group: int) -> dict[int, tuple[str, str]]:
    """base_hex -> (real ISWA name, canonical Symbol ID) for every base
    symbol in the given GLOBAL group range, read from signbank.org's ISWA
    2010 HTML reference.

    Each group's base symbols are listed on ONE page keyed by the group's
    first base hex (``iswa/<start>_sg.html``) -- the same pages
    gen_body_poses.py cites for Category 5's names."""
    names: dict[int, tuple[str, str]] = {}
    for group in range(first_group, last_group + 1):
        start = GROUP_START[group - 1]
        url = _SIGNBANK_GROUP_URL.format(start=start)
        with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 -- fixed https host
            page = response.read().decode("utf-8", "replace")
        rows = _BASESYMBOL_ROW.findall(page)
        if not rows:
            raise SystemExit(f"no BaseSymbol rows parsed from {url} -- page layout changed?")
        for base_key, name, cat, grp, base, variation in rows:
            names[int(base_key, 16)] = (
                html.unescape(name).strip(),
                f"{cat}-{grp}-{base}-{variation}",
            )
    return names


def fetch_glyph_sizes(bases: list[int]) -> tuple[dict[int, float], dict[int, float], str | None]:
    """Per base symbol, the size of its own ISWA glyph, measured from the
    official font's outlines.

    Metric: the diagonal of the glyph's bounding box, in font units
    (unitsPerEm = 300), taken as the MEDIAN over every valid
    (fill, rotation) of that base. Median-over-rotations because rotating a
    non-square arrow changes its bounding box; the spread that leaves is
    reported as a caveat (second return value: per-base coefficient of
    variation, %), not hidden."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        font_path = _npm_pack(_FONT_PACKAGE, _FONT_RELATIVE_PATH, tmp_path)
        font = TTFont(font_path)
        glyf = font["glyf"]
        cmap = font.getBestCmap()
        version = font["name"].getDebugName(5) if "name" in font else None

        sizes: dict[int, float] = {}
        spread: dict[int, float] = {}
        for base in bases:
            combos = valid_combinations_for(base)
            measured: list[float] = []
            for fill in sorted(combos.fills):
                for rotation in sorted(combos.rotations):
                    symbol_id = 1 + (base - 0x100) * 96 + fill * 16 + rotation
                    glyph_name = cmap.get(symbol_id + _LINE_FONT_CODEPOINT_OFFSET)
                    if glyph_name is None:
                        continue
                    glyph = glyf[glyph_name]
                    if glyph.numberOfContours == 0:
                        continue
                    width = glyph.xMax - glyph.xMin
                    height = glyph.yMax - glyph.yMin
                    measured.append((width**2 + height**2) ** 0.5)
            if not measured:
                continue
            sizes[base] = statistics.median(measured)
            mean = statistics.mean(measured)
            spread[base] = (statistics.pstdev(measured) / mean * 100.0) if len(measured) > 1 else 0.0
    return sizes, spread, version


def load_movement_paths() -> dict[int, dict[str, object]]:
    raw = json.loads(_MOVEMENT_PATHS.read_text(encoding="utf-8"))
    return {int(key, 16): value for key, value in raw.items() if key != "_meta"}


# --------------------------------------------------------------------------
# Bug #1 -- path_type / plane / is_hit taken from the GROUP name
# --------------------------------------------------------------------------
# Explicit plane phrases that a symbol's OWN name can state. Only these
# unambiguous phrases are used; a name with no plane phrase is skipped
# rather than guessed at.
_PLANE_PHRASES: tuple[tuple[str, str], ...] = (
    ("wall plane", "wall"),
    ("front wall", "wall"),
    ("floor plane", "floor"),
    ("diagonal", "diagonal"),
)

# Shape words that cannot describe a STRAIGHT trajectory. Deliberately
# conservative: only words naming a visibly non-straight path. Reported as
# "illustrative", since this list IS an interpretation -- unlike the plane
# and is_hit checks below, which compare like-for-like against words the
# ISWA name states outright.
_NOT_STRAIGHT = ("zigzag", "peaks", "curve", "curved", "wave", "loop", "hump", "circle", "spiral")


def _plane_from_name(name: str) -> str | None:
    lowered = name.lower()
    for phrase, plane in _PLANE_PHRASES:
        if phrase in lowered:
            return plane
    return None


def check_bug1(names: dict[int, tuple[str, str]], symid_arr: list[str]) -> None:
    print("=" * 78)
    print("BUG #1 -- movement path_type/plane/is_hit come from the GROUP name")
    print("=" * 78)

    paths = load_movement_paths()
    bases = sorted(paths)
    print(f"\nmovement_paths.json entries: {len(paths)}  "
          f"(0x{bases[0]:03x}-0x{bases[-1]:03x}, Category 2)")

    # Integrity: the names scraped from signbank must line up with the
    # canonical symidArr, or the rest of this section compares the wrong
    # name to the wrong symbol.
    id_mismatch = 0
    for base in bases:
        if base not in names:
            continue
        code = symid_arr[base - 0x100]
        canonical = f"{int(code[0]):02d}-{int(code[1:3]):02d}-{int(code[3:5]):03d}-{int(code[5]):02d}"
        if names[base][1] != canonical:
            id_mismatch += 1
    missing = [b for b in bases if b not in names]
    print(f"signbank names fetched: {len(names)}  |  missing: {len(missing)}  "
          f"|  Symbol ID disagreements with symidArr: {id_mismatch}")
    if missing or id_mismatch:
        print("  ! name<->symbol alignment is not clean; findings below are unreliable")

    # --- [1] The structural collapse, no interpretation needed. ---
    distinct_symbols: set[tuple[int, int]] = set()
    per_group_symbols: dict[int, set[int]] = defaultdict(set)
    for base in bases:
        code = symid_arr[base - 0x100]
        group, symbol = int(code[1:3]), int(code[3:5])
        distinct_symbols.add((group, symbol))
        per_group_symbols[group].add(symbol)

    # Whether path_type is one-per-group is MEASURED, never assumed: this
    # section has to stay truthful after the collapse is fixed, so it can
    # serve as the regression check that it stays fixed.
    path_types = {str(entry["path_type"]) for entry in paths.values()}
    per_group_path_types: dict[int, set[str]] = defaultdict(set)
    for base in bases:
        per_group_path_types[int(symid_arr[base - 0x100][1:3])].add(str(paths[base]["path_type"]))
    collapsed_groups = [g for g, types in per_group_path_types.items() if len(types) == 1]

    print("\n[1] path_type GRANULARITY (structural -- from the Symbol ID, no name reading):")
    print(f"    ISWA distinguishes {len(distinct_symbols)} distinct SYMBOLS "
          f"(Symbol ID's base field) across {len(paths)} base hexes.")
    print(f"    Stored path_type takes {len(path_types)} distinct values; "
          f"{len(collapsed_groups)} of {len(per_group_path_types)} groups carry only ONE.")
    if len(collapsed_groups) == len(per_group_path_types):
        print("    => COLLAPSED: every group's symbols share one path_type, i.e. it is")
        print("       group-derived. This is the bug.")
    else:
        print("    => NOT collapsed: path_type varies WITHIN groups, i.e. it is derived")
        print("       per symbol. Bug #1's path_type half is FIXED; this section is now a")
        print("       regression check. `plane`/`is_hit` below are measured separately.")
    print(f"\n    {'group':>6}{'#bases':>8}{'#ISWA symbols':>16}{'#path_type':>12}  path_types")
    for group in sorted(per_group_symbols):
        group_bases = [b for b in bases if int(symid_arr[b - 0x100][1:3]) == group]
        types = sorted(per_group_path_types[group])
        shown = ", ".join(types[:4]) + (f", +{len(types) - 4} more" if len(types) > 4 else "")
        print(f"    {group:>6}{len(group_bases):>8}{len(per_group_symbols[group]):>16}"
              f"{len(types):>12}  {shown}")

    # --- [2] plane contradicted by the symbol's own name. ---
    plane_contradicts: list[tuple[int, str, str, object]] = []
    plane_missing: list[tuple[int, str, str]] = []
    for base in bases:
        if base not in names:
            continue
        name = names[base][0]
        stated = _plane_from_name(name)
        if stated is None:
            continue
        stored = paths[base]["plane"]
        if stored is None:
            plane_missing.append((base, name, stated))
        elif str(stored) != stated:
            plane_contradicts.append((base, name, stated, stored))

    print(f"\n[2] `plane` vs the plane the symbol's OWN ISWA name states outright:")
    print(f"    CONTRADICTED: {len(plane_contradicts)} symbols  "
          f"|  name states a plane but stored plane is null: {len(plane_missing)}")
    for base, name, stated, stored in plane_contradicts:
        print(f"      0x{base:03x} {name!r}")
        print(f"             name says {stated!r}, stored {str(stored)!r} (from the group name)")
    for base, name, stated in plane_missing:
        print(f"      0x{base:03x} {name!r} -- name says {stated!r}, stored null")

    # --- [3] is_hit contradicted by the symbol's own name. ---
    hit_wrong: list[tuple[int, str, bool]] = []
    for base in bases:
        if base not in names:
            continue
        name = names[base][0]
        name_says_hit = "hit" in name.lower()
        stored_hit = bool(paths[base]["is_hit"])
        if name_says_hit != stored_hit:
            hit_wrong.append((base, name, stored_hit))
    false_negatives = [x for x in hit_wrong if not x[2]]
    false_positives = [x for x in hit_wrong if x[2]]
    print(f"\n[3] `is_hit` vs whether the symbol's own name says \"Hits\":")
    print(f"    DISAGREES on {len(hit_wrong)} of {len(names)} symbols "
          f"({len(false_negatives)} named \"Hits\" but stored False, "
          f"{len(false_positives)} stored True but not named \"Hits\")")
    for base, name, stored_hit in hit_wrong[:12]:
        print(f"      0x{base:03x} {name!r} -- stored is_hit={stored_hit}")
    if len(hit_wrong) > 12:
        print(f"      ... and {len(hit_wrong) - 12} more")

    # --- [4] path_type, illustrative keyword check. ---
    straight_but_not: list[tuple[int, str]] = []
    for base in bases:
        if base not in names:
            continue
        name = names[base][0]
        if str(paths[base]["path_type"]) != "straight":
            continue
        lowered = name.lower()
        if any(word in lowered for word in _NOT_STRAIGHT):
            straight_but_not.append((base, name))
    print(f"\n[4] `path_type` == \"straight\" on symbols whose own name names a "
          f"non-straight shape")
    print(f"    (ILLUSTRATIVE -- this one reads shape words, so it is an "
          f"interpretation, unlike [2]/[3]):")
    print(f"    {len(straight_but_not)} symbols")
    for base, name in straight_but_not[:10]:
        print(f"      0x{base:03x} {name!r} -- stored path_type='straight'")
    if len(straight_but_not) > 10:
        print(f"      ... and {len(straight_but_not) - 10} more")

    print("\nVERDICT (bug #1):")
    if len(collapsed_groups) == len(per_group_path_types):
        print(f"  * path_type: COLLAPSED -- one value per GROUP, while ISWA names")
        print(f"    {len(distinct_symbols)} distinct symbols inside those groups.")
    else:
        print(f"  * path_type: FIXED -- {len(path_types)} values varying WITHIN groups, i.e.")
        print(f"    per symbol. (This audit was the evidence for that fix; the section")
        print(f"    above is now the regression check that it stays fixed.)")
    remaining = len(plane_contradicts) + len(hit_wrong)
    if remaining:
        print(f"  * STILL GROUP-DERIVED: the stored value contradicts the symbol's OWN")
        print(f"    ISWA name on {len(plane_contradicts)} `plane` and {len(hit_wrong)} `is_hit` flags. These are")
        print(f"    like-for-like comparisons against words the name states outright, not")
        print(f"    shape interpretation -- so path_type being fixed does NOT settle them.")
    else:
        print(f"  * plane/is_hit: no contradiction against the symbols' own names.")
    print(f"  * The per-symbol source is signbank.org's ISWA 2010 reference -- already")
    print(f"    the cited source for Categories 4 and 5's names in this same project.")
    print(f"  NOT shown here: what each symbol's path_type SHOULD be. That needs a")
    print(f"  per-symbol geometry decision, which is the actual fix, not this audit.")


# --------------------------------------------------------------------------
# Bug #2 -- amplitude is one constant; the font carries the real size
# --------------------------------------------------------------------------
_SIZE_RANK = {"small": 0, "medium": 1, "large": 2, "largest": 3}


def _size_series_key(name: str) -> tuple[int, tuple[str, ...]] | None:
    """Split an ISWA name into (size rank, everything else), or None if it
    carries no single unambiguous size word.

    Two symbols belong to the same comparable series only when everything
    EXCEPT the size word is identical -- so "Loop Hits Ceiling Small Single"
    and "... Large Single" compare, but neither is compared against
    "... Small Double"."""
    tokens = name.replace(",", " ").split()
    ranks = [(i, _SIZE_RANK[t.lower()]) for i, t in enumerate(tokens) if t.lower() in _SIZE_RANK]
    if len(ranks) != 1:
        return None
    index, rank = ranks[0]
    rest = tuple(t.lower() for i, t in enumerate(tokens) if i != index)
    return rank, rest


def check_bug2(names: dict[int, tuple[str, str]]) -> None:
    print("=" * 78)
    print("BUG #2 -- amplitude is a single constant; the ISWA font has the real size")
    print("=" * 78)

    paths = load_movement_paths()
    bases = sorted(paths)
    stored = Counter(float(str(entry["amplitude"])) for entry in paths.values())
    print(f"\n[1] STORED amplitude across all {len(paths)} Category 2 symbols:")
    for value, count in stored.most_common():
        print(f"      {value} -- {count} symbols ({count / len(paths):.0%})")

    sizes, spread, font_version = fetch_glyph_sizes(bases)
    values = sorted(sizes.values())
    smallest = min(sizes, key=lambda b: sizes[b])
    largest = max(sizes, key=lambda b: sizes[b])
    print(f"\n[2] MEASURED glyph size, {_FONT_PACKAGE} "
          f"SuttonSignWritingLine.ttf (version {font_version!r}):")
    print(f"      bases measured: {len(sizes)}/{len(bases)}")
    print(f"      distinct sizes: {len({round(v, 1) for v in values})}")
    print(f"      min  {values[0]:7.1f} font units -- 0x{smallest:03x} "
          f"{names.get(smallest, ('?', ''))[0]!r}")
    print(f"      max  {values[-1]:7.1f} font units -- 0x{largest:03x} "
          f"{names.get(largest, ('?', ''))[0]!r}")
    print(f"      spread: {values[-1] / values[0]:.2f}x  "
          f"-- erased entirely by storing one constant")
    print(f"      CAVEAT: metric is the median bbox diagonal over a base's valid")
    print(f"      (fill, rotation); rotating a non-square arrow moves its bbox, so")
    print(f"      each base has some internal spread -- median {statistics.median(spread.values()):.1f}%, "
          f"max {max(spread.values()):.1f}%.")

    # --- [3] Cross-validation: does the font agree with the ISWA name? ---
    series: dict[tuple[str, ...], list[tuple[int, int, str]]] = defaultdict(list)
    for base in bases:
        if base not in names or base not in sizes:
            continue
        parsed = _size_series_key(names[base][0])
        if parsed is None:
            continue
        rank, rest = parsed
        series[rest].append((rank, base, names[base][0]))

    comparable = {rest: items for rest, items in series.items() if len(items) >= 2}
    monotonic = 0
    violations: list[tuple[str, ...]] = []
    for rest, items in comparable.items():
        ordered = sorted(items)
        if len({rank for rank, _, _ in ordered}) != len(ordered):
            continue  # a tie in size words -- not an ordering test
        measured = [sizes[base] for _, base, _ in ordered]
        if all(a < b for a, b in zip(measured, measured[1:])):
            monotonic += 1
        else:
            violations.append(rest)

    print(f"\n[3] CROSS-VALIDATION -- two independent sources agree:")
    print(f"    For each set of symbols whose ISWA names are identical except for")
    print(f"    Small/Medium/Large/Largest, does the FONT's glyph get bigger in the")
    print(f"    same order the NAME says?")
    print(f"      comparable series: {len(comparable)}")
    print(f"      strictly increasing with the name's size word: {monotonic}")
    print(f"      violations: {len(violations)}")
    for rest in violations[:5]:
        print(f"        {' '.join(rest)!r}")

    example = max(
        (items for items in comparable.values() if len(items) >= 4),
        key=len,
        default=[],
    )
    if example:
        print(f"\n    Example series (all four currently stored as amplitude=10.0):")
        for rank, base, name in sorted(example):
            print(f"      0x{base:03x} {sizes[base]:7.1f} font units  {name!r}")

    print("\nVERDICT (bug #2):")
    print(f"  * amplitude is ONE number for all {len(paths)} movement symbols, while the")
    print(f"    official ISWA font draws them across a {values[-1] / values[0]:.2f}x size range.")
    print(f"  * That size is not incidental: on {monotonic} of {len(comparable)} name-matched")
    print(f"    series the glyph grows in exactly the order the ISWA name says it")
    print(f"    should. The font geometry and the ISWA naming independently agree,")
    print(f"    which is what makes glyph size a defensible amplitude source.")
    print(f"  * The font is already a project dependency -- gen_valid_combinations.py")
    print(f"    downloads this exact file to build iswa_valid_combinations.json.")
    print(f"  NOT shown here: the font-unit -> amplitude scale factor. Picking that")
    print(f"  (and whether amplitude should be bbox diagonal, height, or path arc")
    print(f"  length) is the fix; this audit only shows the constant is wrong.")


# --------------------------------------------------------------------------
# Bug #3 -- symbol_id built from GROUP_START instead of symidArr
# --------------------------------------------------------------------------
def check_bug3(symid_arr: list[str]) -> None:
    """``symbol_id_of`` builds a ``"CC-GG-NNN"`` string from ``category_of`` /
    ``group_of`` / ``base_symbol_number_of``, all derived from
    ``GROUP_START``. This separates three questions:

        category   -- is the symbol in the right ISWA category?
        group      -- do the 30 group BOUNDARIES match (which base is in
                      which group), independent of how it is NUMBERED?
        id string  -- does fsw_r's "CC-GG-NNN" equal the canonical
                      per-category id?

    A category/boundary match means the underlying data is filed correctly
    (bug #3 is then convention, NOT a wrong-value bug like #1/#2)."""
    bases = [0x100 + i for i in range(len(symid_arr))]
    print("=" * 78)
    print("BUG #3 -- fsw_r symbol_id vs canonical @sutton-signwriting symidArr")
    print("=" * 78)
    print(f"\nCanonical base symbols: {len(symid_arr)}  |  fsw_r bases 0x100..0x{bases[-1]:03x}")

    # --- 1. Group BOUNDARIES: which base is in which group (ignore numbering). ---
    sutton_group_start: list[int] = []
    seen: set[str] = set()
    for i, code in enumerate(symid_arr):
        key = code[0:3]  # category + per-category group
        if key not in seen:
            seen.add(key)
            sutton_group_start.append(0x100 + i)
    boundary_mismatch = [
        (gi + 1, GROUP_START[gi], sutton_group_start[gi])
        for gi in range(min(len(GROUP_START), len(sutton_group_start)))
        if GROUP_START[gi] != sutton_group_start[gi]
    ]
    print("\n[1] GROUP BOUNDARIES (30 groups): "
          + ("ALL MATCH -- GROUP_START is a perfect reconstruction"
             if not boundary_mismatch and len(GROUP_START) == len(sutton_group_start)
             else f"{len(boundary_mismatch)} MISMATCH"))
    for gnum, proj, canon in boundary_mismatch:
        print(f"    group {gnum}: fsw_r 0x{proj:03x} vs canonical 0x{canon:03x}")

    # --- 2/3. Per-symbol: category / id-string comparison. ---
    cat_wrong: Counter[int] = Counter()
    group_num_wrong: Counter[int] = Counter()
    base_num_wrong: Counter[int] = Counter()
    per_cat_total: Counter[int] = Counter()
    for i, code in enumerate(symid_arr):
        base = 0x100 + i
        fsw_cat, fsw_group, fsw_num = (int(x) for x in symbol_id_of(base).split("-"))
        can_cat, can_group, can_base = int(code[0]), int(code[1:3]), int(code[3:5])
        per_cat_total[fsw_cat] += 1
        if fsw_cat != can_cat:
            cat_wrong[fsw_cat] += 1
        if fsw_group != can_group:  # global (1-30) vs per-category (restart)
            group_num_wrong[fsw_cat] += 1
        if fsw_num != can_base:  # fsw_r flat base_hex count vs ISWA base (variations folded)
            base_num_wrong[fsw_cat] += 1

    print("\n[2] CATEGORY assignment: "
          + ("ALL CORRECT (0 misfiled)" if not cat_wrong else f"{sum(cat_wrong.values())} WRONG"))

    print("\n[3] symbol_id STRING vs canonical per-category id:")
    print(f"    {'category':<16}{'#sym':>6}{'group# differs':>16}{'base# differs':>15}")
    for cat in range(1, 8):
        print(f"    {cat} {_CATEGORY_NAME[cat]:<13}{per_cat_total[cat]:>6}"
              f"{group_num_wrong[cat]:>16}{base_num_wrong[cat]:>15}")
    print(f"    {'TOTAL':<16}{sum(per_cat_total.values()):>6}"
          f"{sum(group_num_wrong.values()):>16}{sum(base_num_wrong.values()):>15}")

    boundaries_ok = not boundary_mismatch and not cat_wrong
    print("\nVERDICT (bug #3):")
    if boundaries_ok:
        print("  * The DATA is filed correctly: every category and all 30 group")
        print("    BOUNDARIES match the canonical source exactly. Nothing is misclassified.")
        print("  * The symbol_id STRING is NON-STANDARD, two ways:")
        print("      (a) group is numbered GLOBALLY (1-30); ISWA/sutton numbers it")
        print("          PER-CATEGORY (restart at 01) -- so e.g. fsw_r '04-23-001'")
        print("          should be '04-02-001'. Affects every symbol in categories 2-7.")
        print("      (b) no VARIATION field -- fsw_r counts base_hex flatly, so its")
        print("          base number drifts in any group that has ISWA variations.")
        print("  => bug #3 is a CONVENTION / provenance issue in a display-only id")
        print("     (symbol_id_of's own docstring: 'for readability ONLY, never a lookup")
        print("     key'), NOT a wrong-DATA bug like #1 and #2 above. Fix by deriving the")
        print("     id from symidArr if the paper claims standard ISWA ids; otherwise")
        print("     state the id is a project-internal convention. Either way the")
        print("     underlying category/group/base is correct. See SOURCE_PROVENANCE_AUDIT.md.")
    else:
        print("  Real misclassification found (see [1]/[2]) -- fix GROUP_START.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bug", choices=("1", "2", "3", "all"), default="all",
                        help="which bug to audit (default: all three)")
    args = parser.parse_args()
    wanted = {"1", "2", "3"} if args.bug == "all" else {args.bug}

    names: dict[int, tuple[str, str]] = {}
    if wanted & {"1", "2"}:
        names = fetch_signbank_names(_CAT2_FIRST_GROUP, _CAT2_LAST_GROUP)
    symid_arr: list[str] = []
    if wanted & {"1", "3"}:
        symid_arr = fetch_symid_arr()

    if "1" in wanted:
        check_bug1(names, symid_arr)
        print()
    if "2" in wanted:
        check_bug2(names)
        print()
    if "3" in wanted:
        check_bug3(symid_arr)


if __name__ == "__main__":
    main()
