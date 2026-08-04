"""Which (base, fill, rotation) ISWA symbol combinations actually exist.

ISWA defines valid fill/rotation sets **per base symbol**, not globally: of
the 652 base x 6 fill x 16 rotation = 62,592 combinations the key format
allows syntactically, only 37,811 (60.4%) are real symbols. The table this
module loads (``data/iswa_valid_combinations.json``) is the authoritative
list, generated from the official ISWA font's cmap by
``scripts/gen_valid_combinations.py`` (see that script's docstring for the
full derivation) -- not invented or approximated here.

For a base symbol's entry, ``fills`` and ``rotations`` are independent sets
whose full cross product is valid (verified: summing
``len(fills) * len(rotations)`` across every base reproduces the font's
total glyph count of 37,811 exactly, so there is no sparser, non-rectangular
subset hiding within a base symbol's own combinations).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

# First 10 entries of sutton-signwriting/core's `group` boundary array -- the
# 10 ASL-counting hand groups within ISWA Category 1 (Hands). The single
# source of truth for this boundary table; fsw_symbol_key.py imports it from
# here rather than redefining it.
HAND_GROUP_START: tuple[int, ...] = (
    0x100, 0x10E, 0x11E, 0x144, 0x14C, 0x186, 0x1A4, 0x1BA, 0x1CD, 0x1F5,
)
HAND_RANGE_END = 0x205  # exclusive; first base code of the next section ("movement")


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
    """Raises ``ValueError`` if ``base_hex`` isn't a real ISWA base symbol at
    all (outside the font's cmap), as opposed to being a real base symbol
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
