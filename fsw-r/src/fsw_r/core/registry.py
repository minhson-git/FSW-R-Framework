"""Builds an actual, correctly-typed ``FSWRenderableSymbol`` from an
already-decoded FSW symbol -- e.g. a decoded "Index, fill=1, rotation=1"
becomes a real ``HandSymbol`` instance, not a bag of raw ints.

Dispatch is by **category**, not by per-symbol registration: ``_CATEGORY_SYMBOL``
maps a category number to the one class (or factory) that handles every base
symbol in it. All seven ISWA categories are covered, so every one of the 652
real base symbols builds; Categories 6 (Location) and 7 (Punctuation) build
as ``AnnotationSymbol`` -- see that entry's comment for why that is the
accurate answer for them rather than a placeholder. ``build_symbol()`` returns the ``FSWBaseSymbol`` marker, not
``FSWRenderableSymbol`` -- Category 3 (Dynamics) symbols are deliberately NOT
``FSWRenderableSymbol`` (a Dynamics symbol renders nothing of its own, see
``core/modifier_symbol.py``), so a single return type covering every dispatched
category has to be the common ancestor of both trees. Every existing caller
already narrows to the concrete class it needs via ``isinstance`` before calling
anything renderable-specific, so this is a widening, not a behavior change --
verified by reading every call site (``fswr_converter.py``, ``timeline/``,
``fsw-r-viz``) before making it, see PROGRESS.md's Category 3/5 entry.
Adding a new category (once its own ``PoseTable`` + symbol class exist, see
``core/pose_table.py``) is exactly one more entry here -- nothing else in
``core/`` needs to change. This is the whole point of keying everything by
``base_hex`` through the pipeline (``fsw_symbol_key.py``,
``fsw_base_symbol.py``): a category dispatch this simple wouldn't be possible
if base_hex had already been decomposed into category/group/
base_symbol_number and thrown away, the way it used to be.

``_OVERRIDES`` is an explicit, currently-empty escape hatch for a future
*individual* base symbol that needs genuinely distinct behavior (e.g. a
wrist-orientation formula that turns out not to be generic) rather than
just distinct joint angles -- keyed by ``base_hex``, checked before the
category dispatch. See PROGRESS.md's "Refactor tang Group sang
data-driven" entry for why the previous one-class-per-base-symbol design
(and its ``@register_symbol`` decorator) was replaced.

This is the "converter" half of the FSW -> AST -> FSWR pipeline (see
``fsw_ast.py`` for the AST half, ``fswr_converter.py`` for the version that
converts a whole parsed sign at once). ``symbol_from_fsw`` is kept here as a
convenience for the common single-key case.
"""

from __future__ import annotations

from typing import Callable

from fsw_r.core.annotation_symbol import AnnotationSymbol
from fsw_r.core.body_symbol import BodySymbol
from fsw_r.core.dynamics_symbol import DynamicsSymbol
from fsw_r.core.face_movement import FACE_MOVEMENT_BASES, FaceMovementSymbol
from fsw_r.core.face_pose_table import FACE_POSE_TABLE
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.fsw_base_symbol import FSWBaseSymbol
from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol, parse_fsw_symbol_key
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.head_movement import HEAD_MOVEMENT_BASES, HeadMovementSymbol
from fsw_r.core.head_symbol import HEAD_ORIENTATION_BASES, HeadSymbol
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol

# A concrete symbol's constructor -- (base_hex, fill, rotation) ->
# FSWBaseSymbol. Every category built through _CATEGORY_SYMBOL today
# actually returns a narrower FSWRenderableSymbol subtype EXCEPT Category 3
# (DynamicsSymbol, an FSWModifierSymbol) -- see build_symbol()'s docstring.
_Constructor = Callable[..., FSWBaseSymbol]


def _make_category4_symbol(base_hex: int, fill: int, rotation: int) -> FSWRenderableSymbol:
    """Category 4 (Head & Face) dispatch. Every base builds: a ``FaceSymbol``
    (ARKit-52 blend-shapes) for the authored facial expressions and eyegaze,
    a ``HeadSymbol`` (rigid 3D orientation) for the head-orientation bases,
    and an ``AnnotationSymbol`` (a labelled marker, no modelled pose) for the
    rest -- the non-facial marks (teeth/ears/hair/neck/airflow), the facial
    *movements* that need an expression-over-time model, and the angled
    "dreamy" brows. A family graduates from AnnotationSymbol to its own class
    once its convention is verified -- eyegaze and head already did."""
    if base_hex in FACE_POSE_TABLE:
        return FaceSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    if base_hex in FACE_MOVEMENT_BASES:
        return FaceMovementSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    if base_hex in HEAD_ORIENTATION_BASES:
        return HeadSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    if base_hex in HEAD_MOVEMENT_BASES:
        return HeadMovementSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    return AnnotationSymbol(base_hex=base_hex, fill=fill, rotation=rotation)


# category -> the one class (or factory) that covers every base symbol in it.
# Adding a category is one more entry here -- see PROGRESS.md's Phase 2 entry
# for the "extensibility check" that adding {2: MovementSymbol} needed no
# other change in core/; {4: ...}/{5: ...} followed the same pattern, and
# {3: DynamicsSymbol} needed exactly one change beyond this dict -- widening
# build_symbol()'s return type (see its own docstring).
_CATEGORY_SYMBOL: dict[int, _Constructor] = {
    1: HandSymbol,
    2: MovementSymbol,
    3: DynamicsSymbol,
    4: _make_category4_symbol,
    5: BodySymbol,
    # Categories 6 (Location) and 7 (Punctuation) build as AnnotationSymbol
    # -- a labelled marker carrying the symbol's identity and no modelled
    # pose. That is the accurate answer for both, not a placeholder:
    #
    #   Location says WHERE a sign is produced relative to the signer. It is
    #   a spatial anchor, not an articulation, and this framework has no
    #   verified convention mapping an ISWA location glyph onto its own
    #   body-anchor space (timeline/anchor.py positions from the SIGNBOX
    #   coordinates the FSW string already carries). Inventing one would be
    #   exactly the "wrong source when none is available" mistake the
    #   Category 2 source-fidelity work spent four commits undoing.
    #
    #   Punctuation is writing-system notation -- sentence marks between
    #   signs. It is never performed by the body at all, so "no modelled
    #   pose" is not a gap here, it is the correct and final answer.
    #
    # Measured reason this matters: before this entry, these 13 base symbols
    # were the ONLY cause of symbol-mapping failure over the whole SignBank+
    # corpus -- 118,251 Punctuation tokens (3.5%, more than Dynamics) and 367
    # Location tokens (see reports/corpus_coverage.md). A sign containing a
    # full stop could not be processed at all because of the full stop.
    #
    # NOTE for anyone quoting the mapping rate: mapping to an
    # AnnotationSymbol is a successful IDENTIFICATION, not a modelled pose.
    # scripts/eval_corpus_coverage.py reports modelled and annotation-only
    # tokens separately for exactly this reason -- do not read 100% mapping
    # as 100% animated.
    6: AnnotationSymbol,
    7: AnnotationSymbol,
}

# Escape hatch for a future INDIVIDUAL base symbol needing distinct
# behavior, not just distinct numbers -- keyed by base_hex. Empty today:
# 0/261 Category 1 base symbols need this.
_OVERRIDES: dict[int, _Constructor] = {}


def build_symbol(parsed: ParsedFSWSymbol) -> FSWBaseSymbol:
    """Instantiate the symbol matching ``parsed.base_hex`` with the decoded
    fill/rotation.

    Returns the ``FSWBaseSymbol`` marker, not ``FSWRenderableSymbol`` --
    Category 3 (Dynamics) builds a ``DynamicsSymbol``, which is deliberately
    NOT an ``FSWRenderableSymbol`` (see ``core/modifier_symbol.py``), so
    that can't be this function's declared return type any more. Every
    caller that needs the narrower, renderable-specific type already
    ``isinstance``-narrows before calling anything on it (e.g.
    ``timeline/build.py``, ``fsw-r-viz``'s demos) -- confirmed by reading
    every call site before this widening, not assumed; see PROGRESS.md's
    Category 3/5 entry.

    Raises ``ValueError`` if ``parsed``'s category has no entry in
    ``_CATEGORY_SYMBOL`` -- honestly, as "category not supported" rather
    than a parse error. All seven ISWA categories are now covered, so this
    is unreachable for any real base symbol; it stays because
    ``_CATEGORY_SYMBOL`` is the extension point and a future partial entry
    must fail loudly rather than silently build the wrong kind of symbol.
    """
    cls = _OVERRIDES.get(parsed.base_hex)
    if cls is None:
        cls = _CATEGORY_SYMBOL.get(parsed.category)
        if cls is None:
            raise ValueError(
                f"Category {parsed.category} is not supported yet "
                f"(base 0x{parsed.base_hex:03x}, symbol_id {parsed.symbol_id})"
            )
    return cls(base_hex=parsed.base_hex, fill=parsed.fill, rotation=parsed.rotation)


def symbol_from_fsw(key: str) -> FSWBaseSymbol:
    """Decode a single, bare real FSW symbol key (e.g. ``"S10011"``) and
    instantiate the matching base symbol.

    Convenience wrapper around ``parse_fsw_symbol_key`` + ``build_symbol``
    for the common case of a single symbol, not a full multi-symbol sign --
    for that, see ``fswr_converter.fsw_to_fswr``.
    """
    return build_symbol(parse_fsw_symbol_key(key))
