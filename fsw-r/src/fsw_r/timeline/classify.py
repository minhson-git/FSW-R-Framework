"""D1 (role classification) and D2 (track assignment for a posture) --
both deterministic lookups, no inference. See ``build.py``'s module
docstring for why MVP-1's scope keeps every stage deterministic.
"""

from __future__ import annotations

from fsw_r.core.fswr_converter import PositionedSymbol
from fsw_r.core.movement_symbol import MovementSymbol
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
    ``hand_side``."""
    return TrackName.RIGHT_HAND if hand_side == HandSide.RIGHT else TrackName.LEFT_HAND


def tracks_for_movement(movement: MovementSymbol) -> tuple[TrackName, ...]:
    """D2 for a Category 2 (movement) symbol in a TWO-handed sign: which hand
    track(s) perform the movement, read from its arrowhead-fill code. Used
    only when >1 hand track exists (see ``build.py``); a one-handed sign has
    a single track, so its movement's fill carries no disambiguating signal
    and is not consulted (which is also why ``signbank-plus`` shows left-hand
    one-handed signs still using fill 0 ~72% of the time -- the fill only
    distinguishes hands where there are two to distinguish, i.e. exactly
    here). Returns a tuple so the "both hands" case maps to both tracks
    without needing a ``HandSide.BOTH`` member.

    **Cited rule** -- SignWriting encodes the performing hand in the movement
    arrowhead's STYLE: a dark arrowhead = right hand, a light arrowhead =
    left hand, a "superposed hands" arrowhead = both hands (Sutton, *Lessons
    in SignWriting*; the SignWriter Studio "Arrow Chooser" lists the six
    arrowhead types in the exact ISWA fill order: Right(0), Left(1),
    Superposed(2), Right-Flipped(3), Left-Flipped(4), Superposed-Flipped(5)
    -- "flipped" mirrors the arrow's shape but keeps the hand its name
    states). So ``fill % 3`` collapses the flip variants onto the hand:
    0 -> right, 1 -> left, 2 -> both. This is the rule
    ``MovementSymbol.hand_side``'s docstring flagged as "needs cross-checking
    against Lessons in SignWriting chapter 6 first"; that cross-check is done
    (see PROGRESS.md's MVP-2 entry / ROADMAP.md Pha 2).
    """
    hand_code = movement.fill % 3
    if hand_code == 0:
        return (TrackName.RIGHT_HAND,)
    if hand_code == 1:
        return (TrackName.LEFT_HAND,)
    return (TrackName.RIGHT_HAND, TrackName.LEFT_HAND)
