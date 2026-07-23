"""Real parsing of ISWA/FSW hand-symbol keys -- no invented ranges here.

An FSW symbol key is 6 ASCII characters: ``S`` + 3 hex digits (base code) +
1 hex digit fill (0-5) + 1 hex digit rotation (0-f), e.g. ``"S10011"``. This
is the same key format the ``signwriting`` PyPI package (the Python port of
sutton-signwriting/core) extracts via
``signwriting.formats.fsw_to_sign.fsw_to_sign`` and consumes in
``signwriting.utils.mirror.mirror_symbol`` (``base, fill = symbol[:4],
symbol[4]; rotation = int(symbol[5], 16)``).

The category/group ranges below are taken directly from
sutton-signwriting/core's own source
(``src/fsw/fsw-structure.js``, https://github.com/sutton-signwriting/core):

- ``ranges.hand = [0x100, 0x204]`` -- ISWA Category 1 (Hands).
- the ``group`` boundary array's first 10 entries (the rest cover
  movement/head/trunk/etc, outside this prototype's scope):
  ``0x100, 0x10e, 0x11e, 0x144, 0x14c, 0x186, 0x1a4, 0x1ba, 0x1cd, 0x1f5``,
  followed by ``0x205`` (the start of the next section, "movement"), used
  here as the closing edge of group 10.

Group 1 (0x100-0x10d) is exactly 14 base codes, matching the 14 named base
symbols listed at https://www.signwriting.org/lessons/iswa/group01/ (Index
through Index Hinge on Circle), whose page links confirm base_symbol_number
1 = "Index" and 7 = "Index Bent" (e.g. the image/link path
``01-01-001-01.png`` / ``.html`` for Index). ``0x100 + (1 - 1) = 0x100`` and
``0x100 + (7 - 1) = 0x106`` are therefore "Index" and "Index Bent".
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SYMBOL_KEY_RE = re.compile(r"^S([0-9a-fA-F]{3})([0-5])([0-9a-fA-F])$")

# First 10 entries of sutton-signwriting/core's `group` boundary array --
# the 10 ASL-counting hand groups within ISWA Category 1 (Hands).
_HAND_GROUP_START: tuple[int, ...] = (
    0x100, 0x10E, 0x11E, 0x144, 0x14C, 0x186, 0x1A4, 0x1BA, 0x1CD, 0x1F5,
)
_HAND_RANGE_END = 0x205  # exclusive; first base code of the next section ("movement")


@dataclass(frozen=True)
class ParsedFSWSymbol:
    category: int
    group: int
    base_symbol_number: int
    fill: int
    rotation: int


def parse_fsw_symbol_key(key: str) -> ParsedFSWSymbol:
    """Parse a single FSW symbol key (e.g. ``"S10011"``) into
    category/group/base_symbol_number/fill/rotation.

    Raises ``ValueError`` for anything that isn't a well-formed key, or that
    falls outside ISWA Category 1 (Hands, 0x100-0x204) -- the only category
    this prototype's ``groups/`` classes model.
    """
    match = _SYMBOL_KEY_RE.match(key)
    if match is None:
        raise ValueError(f"not a valid FSW symbol key: {key!r}")
    base_hex, fill_hex, rotation_hex = match.groups()
    base_value = int(base_hex, 16)

    if not (_HAND_GROUP_START[0] <= base_value < _HAND_RANGE_END):
        raise ValueError(
            f"symbol base 0x{base_hex} is outside ISWA Category 1 (Hands, "
            f"0x100-0x204) -- only Hands is modeled by this prototype"
        )

    boundaries = (*_HAND_GROUP_START, _HAND_RANGE_END)
    group_index = next(
        i
        for i in range(len(_HAND_GROUP_START))
        if boundaries[i] <= base_value < boundaries[i + 1]
    )

    return ParsedFSWSymbol(
        category=1,
        group=group_index + 1,
        base_symbol_number=base_value - _HAND_GROUP_START[group_index] + 1,
        fill=int(fill_hex, 16),
        rotation=int(rotation_hex, 16),
    )
