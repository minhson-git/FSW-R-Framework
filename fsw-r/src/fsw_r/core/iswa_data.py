"""ISWA structure (category/group boundaries) and per-symbol valid
(fill, rotation) combinations -- the two pieces of ISWA domain knowledge
every category needs, kept in one place so ``core/`` stays
category-agnostic (see ``registry.py``'s category dispatch).

Group/category boundaries are taken directly from
``@sutton-signwriting/core``'s own source (``src/fsw/fsw-structure.js``,
fetched the same way ``scripts/gen_valid_combinations.py`` fetches the ISWA
font -- via ``npm pack``, not scraped):

    const category = [0x100, 0x205, 0x2f7, 0x2ff, 0x36d, 0x37f, 0x387];
    // "hand, movement, dynamics, head, trunk & limb, location, and
    // punctuation" -- 7 categories.
    const group = [0x100, 0x10e, 0x11e, 0x144, 0x14c, 0x186, 0x1a4, 0x1ba,
                    0x1cd, 0x1f5, 0x205, 0x216, 0x22a, 0x255, 0x265, 0x288,
                    0x2a6, 0x2b7, 0x2d5, 0x2e3, 0x2f7, 0x2ff, 0x30a, 0x32a,
                    0x33b, 0x359, 0x36d, 0x376, 0x37f, 0x387];  // 30 groups
    ranges.all = [0x100, 0x38b];

IMPORTANT, resolved discrepancy: the official ``category`` array has 7
entries, not 8 -- Trunk and Limb share ONE category boundary (0x36d), per
the source's own comment ("trunk & limb"). An earlier, pre-verification
version of this project's ``ROADMAP.md`` listed 8 category rows (splitting
Trunk and Limb into separate categories); that framing did not come from
this source and is corrected here. ``fsw-structure.js``'s ``ranges`` object
*does* separately expose ``trunk: [0x36d, 0x375]`` and ``limb: [0x376,
0x37e]`` as named sub-ranges for convenience lookups, but they are not
separate top-level categories -- ``category_of()`` below returns 5 for
anything in ``0x36d``-``0x37e``, matching the real 7-category array.

Group numbering (``group_of()``) is global across all of ISWA (1..30), not
reset to 1 at each category boundary -- Category 1 (Hands) happens to BE
the first 10 groups, so this is identical to the old Category-1-only
numbering for every symbol that exists today; it only becomes visible once
a symbol from Category 2+ is decoded.

**``group_of()`` is a framework-internal index, NOT the ISWA standard
Symbol ID's own ``group`` field** ("Sửa symbol_id dùng symidArr chuẩn"
task, kept deliberately unchanged by that task -- see its own docstring
below and PROGRESS.md's entry for why): ISWA's real Symbol ID numbers
groups PER CATEGORY (1-10 within Hands, 1-10 within Movement, ...), while
``group_of()`` numbers them globally 1-30 across all of ISWA.
``movement_paths.py`` and ``finger_articulation.py`` key their own tables
by THIS global numbering (group 12 = Finger Movement), so it stays as-is
-- ``symbol_id_of()`` is the function that returns ISWA's own numbering,
from a different source entirely (see below), not derived from
``group_of()`` at all anymore.
"""

from __future__ import annotations

import bisect
import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

# 30 group-boundary base hex values, spanning all of ISWA.
GROUP_START: tuple[int, ...] = (
    0x100, 0x10E, 0x11E, 0x144, 0x14C, 0x186, 0x1A4, 0x1BA, 0x1CD, 0x1F5,  # 1-10  Hands
    0x205, 0x216, 0x22A, 0x255, 0x265, 0x288, 0x2A6, 0x2B7, 0x2D5, 0x2E3,  # 11-20 Movement
    0x2F7, 0x2FF, 0x30A, 0x32A, 0x33B, 0x359, 0x36D, 0x376, 0x37F, 0x387,  # 21-30 Dynamics..Punctuation
)

# 7 category-boundary base hex values (hand, movement, dynamics, head,
# trunk & limb, location, punctuation) -- see module docstring.
CATEGORY_START: tuple[int, ...] = (
    0x100, 0x205, 0x2F7, 0x2FF, 0x36D, 0x37F, 0x387,
)

ISWA_LAST_BASE = 0x38B  # ranges.all = [0x100, 0x38b]

# Backward-compatible aliases for the pre-this-refactor Category-1-only
# names, still meaningful since Category 1 is exactly GROUP_START[:10].
HAND_GROUP_START: tuple[int, ...] = GROUP_START[:10]
HAND_RANGE_END = GROUP_START[10]  # 0x205, first base of the next section


def _validate_base_hex(base_hex: int) -> None:
    if not (GROUP_START[0] <= base_hex <= ISWA_LAST_BASE):
        raise ValueError(
            f"base 0x{base_hex:03x} is outside the ISWA range "
            f"0x{GROUP_START[0]:03x}-0x{ISWA_LAST_BASE:03x}"
        )


def category_of(base_hex: int) -> int:
    """1-based category number (1..7). Raises ``ValueError`` if ``base_hex``
    is outside the ISWA range 0x100-0x38b."""
    _validate_base_hex(base_hex)
    return bisect.bisect_right(CATEGORY_START, base_hex)


def group_of(base_hex: int) -> int:
    """1-based, GLOBAL group number (1..30) -- see module docstring for why
    this isn't reset per category."""
    _validate_base_hex(base_hex)
    return bisect.bisect_right(GROUP_START, base_hex)


def base_symbol_number_of(base_hex: int) -> int:
    """1-based position of ``base_hex`` within its own group."""
    group = group_of(base_hex)
    return base_hex - GROUP_START[group - 1] + 1


@lru_cache(maxsize=1)
def _load_symbol_id_table() -> dict[int, str]:
    """``base_hex -> 6-digit minimized symid`` (e.g. ``0x218 -> "202021"``),
    from ``data/iswa_symbol_ids.json`` (``scripts/gen_symbol_ids.py``,
    derived from ``@sutton-signwriting/core``'s own ``symidArr`` -- the
    real ISWA reference library, not this project's own numbering -- see
    that script's module docstring for the full provenance and the
    parsing trap it guards against)."""
    raw_text = resources.files("fsw_r.data").joinpath("iswa_symbol_ids.json").read_text(encoding="utf-8")
    raw = json.loads(raw_text)
    table: dict[int, str] = {}
    for key, value in raw.items():
        if key == "_meta":
            continue
        table[int(key, 16)] = value
    return table


def _symid_min_for(base_hex: int) -> str:
    _validate_base_hex(base_hex)
    table = _load_symbol_id_table()
    symid_min = table.get(base_hex)
    if symid_min is None:
        raise ValueError(f"base 0x{base_hex:03x} has no entry in iswa_symbol_ids.json")
    return symid_min


def variation_of(base_hex: int) -> int:
    """1-based variation number within this base symbol's own
    category-group-base -- the field ``group_of()``/``base_symbol_number_of()``
    have no way to represent (see module docstring). Almost always 1: only
    94 of ISWA's 652 ``base_hex`` values share a category-group-base with
    another (a "sibling" variation) -- see ``data/iswa_symbol_ids.json``'s
    own ``_meta``."""
    return int(_symid_min_for(base_hex)[5])


def _decode_symid_min(symid_min: str) -> tuple[str, str, str, str]:
    """``"202021"`` -> ``("02", "02", "002", "01")`` -- the exact digit
    layout ``@sutton-signwriting/core``'s own ``symidMax()`` builds
    (category zero-padded to 2, group already 2 digits, base zero-padded
    to 3, variation zero-padded to 2), reproduced here rather than
    re-derived, so ``base_symbol_id_of()``/``symbol_id_of()`` can't drift
    apart on the padding."""
    category, group, base, variation = symid_min[0], symid_min[1:3], symid_min[3:5], symid_min[5]
    return f"{int(category):02d}", group, f"0{base}", f"0{variation}"


def base_symbol_id_of(base_hex: int) -> str:
    """``"02-02-001"``-style id -- category, ISWA's own PER-CATEGORY group
    number, and base symbol number, from the real ISWA Symbol ID
    (``data/iswa_symbol_ids.json``) -- WITHOUT the variation suffix, i.e.
    identifying the base symbol two variations (like 0x216/0x217) share.
    See ``symbol_id_of()`` for the full 4-part id including variation."""
    category, group, base, _variation = _decode_symid_min(_symid_min_for(base_hex))
    return f"{category}-{group}-{base}"


def symbol_id_of(base_hex: int) -> str:
    """``"02-02-001-02"``-style display id -- ISWA's own real, standard
    Symbol ID (category-group-base-variation), from
    ``data/iswa_symbol_ids.json`` (``@sutton-signwriting/core``'s
    ``symidArr``) -- for logging/error messages/test readability ONLY,
    never used as a lookup key (see ``registry.py`` and ``pose_table.py``,
    both keyed by ``base_hex`` directly).

    **Not derived from ``GROUP_START``/``group_of()``/``base_symbol_number_of()``
    anymore** ("Sửa symbol_id dùng symidArr chuẩn" task -- those functions
    stayed unchanged, but no longer feed this one): the old formula
    disagreed with ISWA's own id for 328 of 652 base symbols, from two
    independent causes -- ISWA numbers groups PER CATEGORY, not globally
    1-30, and consecutive ``base_hex`` values can be VARIATIONS of the
    SAME base symbol (which the old formula had no field for at all, so it
    silently drifted every base after the first multi-variation one in a
    group). See PROGRESS.md's entry for this task for the full before/after
    table and the 469-vs-652 distinction this uncovered."""
    category, group, base, variation = _decode_symid_min(_symid_min_for(base_hex))
    return f"{category}-{group}-{base}-{variation}"


def base_hex_of(category: int, group: int, base_symbol_number: int) -> int:
    """Inverse of ``category_of``/``group_of``/``base_symbol_number_of``.
    Exists for backward compatibility and tests, NOT used in the main
    parse/build pipeline (``base_hex`` flows through unchanged from the FSW
    key instead, see ``fsw_symbol_key.py``).

    Validates that ``group`` actually belongs to ``category`` and that the
    resulting ``base_hex`` doesn't spill past the end of ``group`` into the
    next one (a silent-corruption risk with a plain offset computation)."""
    if not (1 <= group <= len(GROUP_START)):
        raise ValueError(f"group must be in 1..{len(GROUP_START)}, got {group}")
    group_start = GROUP_START[group - 1]
    actual_category = category_of(group_start)
    if actual_category != category:
        raise ValueError(f"group {group} belongs to category {actual_category}, not {category}")
    group_end = GROUP_START[group] - 1 if group < len(GROUP_START) else ISWA_LAST_BASE
    base_hex = group_start + (base_symbol_number - 1)
    if not (group_start <= base_hex <= group_end):
        raise ValueError(
            f"base_symbol_number={base_symbol_number} is out of range for group {group} "
            f"(0x{group_start:03x}-0x{group_end:03x})"
        )
    return base_hex


@dataclass(frozen=True)
class ValidCombinations:
    fills: frozenset[int]
    rotations: frozenset[int]


@lru_cache(maxsize=1)
def _load_table() -> dict[int, ValidCombinations]:
    raw_text = resources.files("fsw_r.data").joinpath("iswa_valid_combinations.json").read_text(encoding="utf-8")
    raw = json.loads(raw_text)
    table: dict[int, ValidCombinations] = {}
    for key, entry in raw.items():
        if key == "_meta":
            continue
        table[int(key, 16)] = ValidCombinations(
            fills=frozenset(entry["fills"]),
            rotations=frozenset(entry["rotations"]),
        )
    return table


def valid_combinations_for(base_hex: int) -> ValidCombinations:
    """Which (fill, rotation) combinations actually exist for this base
    symbol -- see ``data/iswa_valid_combinations.json``, generated from the
    real ISWA font's cmap (``scripts/gen_valid_combinations.py``). Raises
    ``ValueError`` if ``base_hex`` isn't a real ISWA base symbol at all (not
    present in the font's cmap), as opposed to being a real base symbol
    with a restricted fill/rotation set."""
    combos = _load_table().get(base_hex)
    if combos is None:
        raise ValueError(
            f"base 0x{base_hex:03x} is not a real ISWA base symbol "
            f"(not present in the font's cmap)"
        )
    return combos


def is_valid_symbol(base_hex: int, fill: int, rotation: int) -> bool:
    combos = valid_combinations_for(base_hex)
    return fill in combos.fills and rotation in combos.rotations
