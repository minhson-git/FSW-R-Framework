"""Builds a ``SignTimeline`` from ``core/fswr_converter.py``'s
``tuple[PositionedSymbol, ...]`` -- MVP-2 scope.

**MVP-2 scope:** a sign with 1 OR 2 hand (Category 1) symbols, at most 1
movement (Category 2) symbol PER hand, and no symbol from any other
category. Measured on SignBank+ (257,800 signs): two-hand signs raise the
coverage from MVP-1's 6.2% (one hand) toward ~20.9% of real signs.

**What MVP-2 adds over MVP-1, and why it stays deterministic:** MVP-1
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
symbols, the tracks and their keyframes are fully determined. A sign
outside this scope raises ``UnsupportedSignError`` naming exactly why --
never a best-effort wrong timeline.
"""

from __future__ import annotations

import numpy as np

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


def build_timeline(positioned_symbols: tuple[PositionedSymbol, ...]) -> SignTimeline:
    """Raises ``UnsupportedSignError`` for anything outside MVP-2's scope
    (see module docstring)."""
    postures = []
    transitions = []
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
        else:
            raise UnsupportedSignError(
                f"MVP-2 only supports Category 1 (hand posture) and Category 2 "
                f"(movement) symbols; found a category {category} ({role.value}) "
                f"symbol ({positioned.symbol.symbol_id})"
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

    tracks = tuple(
        Track(name=track_name, keyframes=_build_keyframes(posture, movement_by_track.get(track_name)))
        for track_name, posture in sorted(posture_by_track.items(), key=lambda item: item[0].value)
    )
    return SignTimeline(tracks=tracks, duration_seconds=DEFAULT_SIGN_DURATION)
