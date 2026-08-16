"""Builds a ``SignTimeline`` from ``core/fswr_converter.py``'s
``tuple[PositionedSymbol, ...]`` -- MVP-3 scope.

**MVP-3 scope:** a sign with 1 OR 2 hand (Category 1) symbols, at most 1
movement (Category 2) symbol PER hand, and any number of Category 4 STATIC
facial expressions, which merge into one FACE track.

**Coverage, measured -- run scripts/eval_corpus_coverage.py to reproduce.**
Over all 257,801 SignBank+ signs, MVP-2 (hands and movement only) built a
timeline for 14.0%. Earlier revisions of this docstring cited "~20.9%" for
MVP-2; that figure was measured ad hoc during development and does NOT
reproduce -- see reports/corpus_coverage.md, whose scope funnel shows 23.0%
surviving every MVP-2 constraint EXCEPT "at most 1 movement per hand", which
is the likeliest thing the old number actually measured. Quote the report,
never this docstring.

Why Category 4 was the right thing to add next, rather than Category 3 or 5:
measured per-category, accepting Category 4 alone raises coverage by about
+13pp, against +2.5pp for Category 3 and +3.2pp for Category 5 -- facial
expression appears in 52.9% of all real signs, so it is not a garnish.

**What is deliberately still rejected**, because each has a real model that
this scope does not consume yet, and accepting the sign while ignoring the
symbol would misrepresent what was written:
  - ``HeadSymbol`` / ``HeadMovementSymbol`` (rigid head orientation, and
    orientation over time) -- the next unlock, ~11.3k corpus occurrences.
  - ``FaceMovementSymbol`` (expression over time).
  - Categories 3 (Dynamics) and 5 (Trunk & Limb).
``AnnotationSymbol`` is the one Category 4 kind carried WITHOUT contributing,
and that is not an exception to the rule: an AnnotationSymbol is defined as
"identified, no modelled pose", so there is no pose being dropped.

**What MVP-2 added over MVP-1, and why it stays deterministic:** MVP-1
allowed exactly one hand precisely so there was no "which hand does this
movement belong to" question. MVP-2 answers that question from a *cited*
rule rather than a guess -- SignWriting encodes the performing hand in the
movement arrowhead's fill (dark = right, light = left, superposed = both;
see ``classify.tracks_for_movement`` for the citation). So:
  - Two postures -> two tracks, one per hand side. Two postures on the SAME
    side ("one hand, two postures") stays unsupported -- that ambiguity is
    real and unresolved.
  - Each movement is routed to its hand track(s) by that fill rule. A
    ONE-handed sign keeps MVP-1's behaviour exactly: its single movement
    goes to the single track and the fill is not consulted (with one hand
    there is nothing to disambiguate).
  - At most one movement PER hand -- two movements on one hand ("one hand,
    two moments" vs. a sequence) is still the ambiguity MVP-1 avoided.

Every stage is still a deterministic lookup, never inference: given the
symbols, the tracks and their keyframes are fully determined. A sign outside
this scope raises ``UnsupportedSignError`` naming exactly why -- never a
best-effort wrong timeline. That rule is why two Category 4 symbols
disagreeing on the same ARKit channel raise instead of one silently winning.
"""

from __future__ import annotations

import numpy as np

from fsw_r.core.annotation_symbol import AnnotationSymbol
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.finger_articulation import articulate_joint_pose
from fsw_r.core.fswr_converter import PositionedSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.timeline.anchor import SIGNBOX_TO_BODY_SCALE, anchor
from fsw_r.timeline.classify import role_of, track_for_posture, tracks_for_movement
from fsw_r.timeline.errors import UnsupportedSignError
from fsw_r.timeline.types import Keyframe, SignTimeline, SymbolRole, Track, TrackName

# UNVERIFIED ASSUMPTION: no data source yet gives a real sign's duration.
# Category 3 (Dynamics) is expected to eventually supply this (see
# ROADMAP.md) -- until then, every timeline gets the same constant. Not
# measured, not calibrated -- a placeholder with a name, not a bare number
# scattered through the code.
DEFAULT_SIGN_DURATION = 0.8


def _build_keyframes(posture: PositionedSymbol, movement: MovementSymbol | None) -> tuple[Keyframe, ...]:
    """One hand track's keyframes, from its posture and its (optional)
    movement. Identical to MVP-1's single-track construction -- extracted so
    MVP-2 can call it once per hand."""
    hand_symbol = posture.symbol
    assert isinstance(hand_symbol, HandSymbol)  # role_of() already guarantees Category 1
    base_position = anchor(posture.x, posture.y)
    joint_pose = hand_symbol.get_joint_pose()
    wrist = hand_symbol.get_wrist_orientation()

    if movement is None:
        # A single static keyframe.
        return (Keyframe(time=0.0, joint_pose=joint_pose, wrist=wrist, position=base_position),)

    path = movement.get_motion_path()
    trajectory = sample_trajectory(path, movement.rotation)
    # A Group 12 (Finger Movement) symbol carries a FingerArticulation --
    # None for every other Category 2 symbol (see MovementSymbol.
    # get_finger_articulation()). When present, EACH keyframe's joint_pose is
    # re-derived at that keyframe's own time instead of reusing one static
    # pose; position is still the trajectory's own points (a fixed point for
    # PathType.FINGER -- the wrist does not move), exactly as for any other
    # Category 2 symbol.
    articulation = movement.get_finger_articulation()
    # One keyframe PER trajectory point (not just the 2 endpoints): with only
    # 2 keyframes, a CURVED/CIRCLE path would be linearly interpolated
    # straight from start to end in sample.py, flattening the arc -- exactly
    # what the "don't let interpolation override the arrow-defined
    # trajectory" rule exists to prevent. For STRAIGHT the intermediate
    # points are collinear, so this is identical to the 2-keyframe case; it
    # only matters for CURVED/CIRCLE. The same dense-keyframes reasoning is
    # why a FINGER articulation's oscillation (evaluated once per keyframe)
    # survives sample.py's linear interpolation as a smooth wiggle.
    times = np.linspace(0.0, 1.0, len(trajectory))
    return tuple(
        Keyframe(
            time=float(t),
            joint_pose=(
                articulate_joint_pose(joint_pose, articulation, float(t)) if articulation is not None else joint_pose
            ),
            wrist=wrist,
            position=base_position + point * SIGNBOX_TO_BODY_SCALE,
        )
        for t, point in zip(times, trajectory)
    )


def _merge_face_expressions(faces: list[PositionedSymbol]) -> FaceExpressionPose:
    """Several Category 4 expression symbols in one sign describe ONE face at
    ONE instant -- brows, mouth and eyes are different ARKit channels of the
    same head -- so they merge into a single expression rather than becoming
    competing tracks. Measured on SignBank+: of the signs this scope accepts,
    21.9% carry more than one FaceSymbol, so merging is the common case, not
    an edge case.

    Two symbols writing the SAME ARKit channel with DIFFERENT weights is a
    genuine ambiguity (which one is the face actually doing?), so it raises
    rather than picking one -- the same "never a best-effort wrong timeline"
    rule the hand scope follows. Measured cost: 115 of 10,931 such signs
    (1.05%). Identical weights are not a conflict; that is just two symbols
    agreeing."""
    merged: dict[str, float] = {}
    source_of: dict[str, str] = {}
    for positioned in faces:
        face = positioned.symbol
        assert isinstance(face, FaceSymbol)  # caller filtered on this
        for name, weight in face.get_expression().blendshapes.items():
            previous = merged.get(name)
            if previous is not None and previous != weight:
                raise UnsupportedSignError(
                    f"two Category 4 symbols disagree on ARKit channel {name!r}: "
                    f"{source_of[name]} sets {previous}, {face.symbol_id} sets {weight}"
                )
            merged[name] = weight
            source_of[name] = face.symbol_id
    return FaceExpressionPose(blendshapes=merged)


def build_timeline(positioned_symbols: tuple[PositionedSymbol, ...]) -> SignTimeline:
    """Raises ``UnsupportedSignError`` for anything outside MVP-2's scope
    (see module docstring)."""
    postures = []
    transitions = []
    faces: list[PositionedSymbol] = []
    annotations: list[PositionedSymbol] = []
    for positioned in positioned_symbols:
        # Gate on the literal ISWA category, not SymbolRole -- Category 4
        # (Head & Face) also classifies as POSTURE (see classify.py's
        # _ROLE_BY_CATEGORY, shared with Category 1), but this scope is
        # "Category 1 and Category 2 only," narrower than "any POSTURE/
        # TRANSITION symbol." role_of() is still called so its own validation
        # runs and its label can be used in the error message.
        category = positioned.symbol.category
        role = role_of(positioned)
        if category == 1 and role == SymbolRole.POSTURE:
            postures.append(positioned)
        elif category == 2 and role == SymbolRole.TRANSITION:
            transitions.append(positioned)
        elif category == 4 and isinstance(positioned.symbol, FaceSymbol):
            faces.append(positioned)
        elif category == 4 and isinstance(positioned.symbol, AnnotationSymbol):
            # Carried, contributes nothing -- which is precisely what an
            # AnnotationSymbol MEANS ("identified, no modelled pose", see
            # core/annotation_symbol.py). This is not a silent drop: the
            # symbol has no pose to drop. The Category 4 kinds that DO have a
            # model (HeadSymbol's rigid orientation, FaceMovementSymbol's and
            # HeadMovementSymbol's expression-over-time) fall through to the
            # error below on purpose -- ignoring those would produce exactly
            # the best-effort wrong timeline this module refuses to build.
            annotations.append(positioned)
        else:
            raise UnsupportedSignError(
                f"MVP-3 supports Category 1 (hand posture), Category 2 (movement) "
                f"and Category 4 static facial expressions; found a category "
                f"{category} ({role.value}) symbol ({positioned.symbol.symbol_id}, "
                f"{type(positioned.symbol).__name__})"
            )

    if not 1 <= len(postures) <= 2:
        raise UnsupportedSignError(
            f"MVP-2 supports signs with 1 or 2 hand (Category 1) symbols; found {len(postures)}"
        )

    # Each posture goes to its own hand track. Two postures must be on
    # different sides -- two same-side postures ("one hand, two postures")
    # is an ambiguity MVP-2 still doesn't resolve.
    posture_by_track: dict[TrackName, PositionedSymbol] = {}
    for posture in postures:
        hand_symbol = posture.symbol
        assert isinstance(hand_symbol, HandSymbol)  # role_of() guarantees Category 1
        track_name = track_for_posture(hand_symbol.hand_side)
        if track_name in posture_by_track:
            raise UnsupportedSignError(
                f"MVP-2 supports at most one posture per hand; found two {track_name.value} hand symbols"
            )
        posture_by_track[track_name] = posture

    # Route each movement to the track(s) that perform it:
    #   - one hand   -> the single track gets every movement; the fill is NOT
    #     consulted (nothing to disambiguate), keeping MVP-1 byte-for-byte;
    #   - two hands  -> tracks_for_movement() reads the arrowhead fill (the
    #     cited right/left/both rule).
    # Two postures are guaranteed to be on different sides by the check above,
    # so in the two-hand case both tracks always exist -- every routed target
    # is present, no "movement for a missing hand" case can arise.
    movement_by_track: dict[TrackName, MovementSymbol] = {}
    only_track = next(iter(posture_by_track)) if len(posture_by_track) == 1 else None
    for transition in transitions:
        movement = transition.symbol
        assert isinstance(movement, MovementSymbol)  # role_of() guarantees Category 2
        targets = (only_track,) if only_track is not None else tracks_for_movement(movement)
        for track_name in targets:
            if track_name in movement_by_track:
                raise UnsupportedSignError(
                    f"MVP-2 supports at most 1 movement per hand; the {track_name.value} hand has more than one"
                )
            movement_by_track[track_name] = movement

    tracks = [
        Track(name=track_name, keyframes=_build_keyframes(posture, movement_by_track.get(track_name)))
        for track_name, posture in sorted(posture_by_track.items(), key=lambda item: item[0].value)
    ]

    # The face track is a single static keyframe: ISWA writes a facial
    # expression as a STATE the sign is performed with, not a trajectory.
    # Expressions that genuinely change over time are FaceMovementSymbol,
    # which this scope still rejects rather than approximating.
    if faces:
        tracks.append(
            Track(
                name=TrackName.FACE,
                keyframes=(
                    Keyframe(
                        time=0.0,
                        joint_pose=None,
                        wrist=None,
                        position=None,
                        expression=_merge_face_expressions(faces),
                    ),
                ),
            )
        )
    return SignTimeline(tracks=tuple(tracks), duration_seconds=DEFAULT_SIGN_DURATION)
