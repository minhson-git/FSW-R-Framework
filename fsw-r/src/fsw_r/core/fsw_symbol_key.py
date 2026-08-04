"""Real parsing of ISWA/FSW symbol keys -- no invented ranges here.

An FSW symbol key is 6 ASCII characters: ``S`` + 3 hex digits (base code) +
1 hex digit fill (0-5) + 1 hex digit rotation (0-f), e.g. ``"S10011"``. This
is the same key format the ``signwriting`` PyPI package (the Python port of
sutton-signwriting/core) extracts via
``signwriting.formats.fsw_to_sign.fsw_to_sign`` and consumes in
``signwriting.utils.mirror.mirror_symbol`` (``base, fill = symbol[:4],
symbol[4]; rotation = int(symbol[5], 16)``).

This module only knows the FSW key *grammar* -- it validates ``base_hex``
against the full ISWA range (``core/iswa_data.py``'s ``GROUP_START[0]`` to
``ISWA_LAST_BASE``, i.e. 0x100-0x38b, all 8 categories), not just Category 1
(Hands). It does NOT know or care which categories are actually
implemented -- ``S22b03`` (Category 2, Movement) parses successfully here;
whether an object can actually be *built* for it is ``registry.py``'s
concern (``build_symbol()`` raises there if the category isn't supported
yet), not this module's. Keeping that check out of the parser is what lets
adding a new category be "register one more entry in registry.py" instead
of "also touch the parser."

``base_hex`` flows through unchanged from the key -- category, group, and
base_symbol_number are derived on demand (``core/iswa_data.py``), not
computed and stored here, so there is exactly one place that turns a
base_hex into those numbers.

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

from fsw_r.core.iswa_data import (
    GROUP_START,
    ISWA_LAST_BASE,
    base_symbol_number_of,
    category_of,
    group_of,
    symbol_id_of,
)

_SYMBOL_KEY_RE = re.compile(r"^S([0-9a-fA-F]{3})([0-5])([0-9a-fA-F])$")


@dataclass(frozen=True)
class ParsedFSWSymbol:
    base_hex: int
    fill: int
    rotation: int

    @property
    def category(self) -> int:
        return category_of(self.base_hex)

    @property
    def group(self) -> int:
        return group_of(self.base_hex)

    @property
    def base_symbol_number(self) -> int:
        return base_symbol_number_of(self.base_hex)

    @property
    def symbol_id(self) -> str:
        """Display-only ``"01-05-002"``-style id -- never used as a lookup
        key, see ``core/iswa_data.py``'s ``symbol_id_of()``."""
        return symbol_id_of(self.base_hex)


def parse_fsw_symbol_key(key: str) -> ParsedFSWSymbol:
    """Parse a single FSW symbol key (e.g. ``"S10011"``) into
    base_hex/fill/rotation.

    Raises ``ValueError`` for anything that isn't a well-formed key, or
    whose base falls outside the full ISWA range (0x100-0x38b). Does NOT
    raise for a base outside Category 1 -- see the module docstring for why
    that check belongs in ``registry.py`` instead.
    """
    match = _SYMBOL_KEY_RE.match(key)
    if match is None:
        raise ValueError(f"not a valid FSW symbol key: {key!r}")
    base_hex_str, fill_hex, rotation_hex = match.groups()
    base_hex = int(base_hex_str, 16)

    if not (GROUP_START[0] <= base_hex <= ISWA_LAST_BASE):
        raise ValueError(
            f"symbol base 0x{base_hex_str} is outside the ISWA range "
            f"0x{GROUP_START[0]:03x}-0x{ISWA_LAST_BASE:03x}"
        )

    return ParsedFSWSymbol(
        base_hex=base_hex,
        fill=int(fill_hex, 16),
        rotation=int(rotation_hex, 16),
    )
