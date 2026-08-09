"""D1 (role classification) and D2 (track assignment for a posture) --
both deterministic lookups, no inference. See ``build.py``'s module
docstring for why MVP-1's scope keeps every stage deterministic.
"""

from __future__ import annotations

from fsw_r.core.fswr_converter import PositionedSymbol
from fsw_r.core.types import HandSide
from fsw_r.timeline.types import SymbolRole, TrackName

# ISWA category (core/iswa_data.py's category_of()) -> SymbolRole. A plain
# lookup table -- category is already a deterministic fact about a symbol,
# nothing to infer.
_ROLE_BY_CATEGORY: dict[int, SymbolRole] = {
    1: SymbolRole.POSTURE,  # Hands
    2: SymbolRole.TRANSITION,  # Movement
    3: SymbolRole.TIMING,  # Dynamics
    4: SymbolRole.POSTURE,  # Head & Face
    5: SymbolRole.ANCHOR,  # Trunk & Limb
    6: SymbolRole.ANCHOR,  # Location
    7: SymbolRole.BOUNDARY,  # Punctuation
}


def role_of(positioned: PositionedSymbol) -> SymbolRole:
    """D1: ``category_of(base_hex)`` -> ``SymbolRole``, via
    ``positioned.symbol.category`` (already a property on every
    ``FSWBaseSymbol``, see ``core/fsw_base_symbol.py``)."""
    category = positioned.symbol.category
    role = _ROLE_BY_CATEGORY.get(category)
    if role is None:
        # category_of() only ever returns 1-7 (see core/iswa_data.py's
        # CATEGORY_START, 7 entries) -- unreachable in practice, but fail
        # loudly rather than silently misclassifying if that ever changes.
        raise ValueError(f"unrecognized ISWA category: {category}")
    return role


def track_for_posture(hand_side: HandSide) -> TrackName:
    """D2 for a Category 1 (posture) symbol: deterministic, straight from
    ``hand_side``. See ``build.py`` for how a Category 2 (transition)
    symbol's track is decided at MVP-1 -- ``MovementSymbol.hand_side`` is
    ``None`` (no rule exists for it yet), so that decision isn't a plain
    lookup the way this one is."""
    return TrackName.RIGHT_HAND if hand_side == HandSide.RIGHT else TrackName.LEFT_HAND
