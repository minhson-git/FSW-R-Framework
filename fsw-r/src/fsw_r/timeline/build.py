"""Builds a ``SignTimeline`` from ``core/fswr_converter.py``'s
``tuple[PositionedSymbol, ...]`` -- MVP-1 scope only.

**MVP-1 scope:** a sign with exactly 1 hand (Category 1) symbol, at most 1
movement (Category 2) symbol, and no symbol from any other category.
Measured on SignBank+ (257,800 signs): this scope covers 6.2% of real
signs (~16,000).

**Why exactly this scope -- a design choice, not a convenience cut:**
MVP-1 skips every step that would otherwise require guessing:
  - 1 track only -> no "which hand does this movement belong to" problem.
  - 1 hand symbol -> no "two hands at once" vs. "one hand, two moments"
    ambiguity.
  - Time order comes from the movement symbol's own arrow direction, not
    from using page position (``y``) as a timing proxy.

So every stage in MVP-1 is DETERMINISTIC (see PROGRESS.md's Phase 3
"confidence table"). If MVP-1's output is wrong, the bug is provably in
anchoring or interpolation math -- never in disambiguation logic, because
there isn't any yet. That is the right foundation to validate before
MVP-2 has to start guessing.

A sign outside this scope raises ``UnsupportedSignError`` naming exactly
why (how many hand symbols, how many movement symbols, which other
category showed up) -- never a best-effort wrong timeline.
"""

from __future__ import annotations

import numpy as np

from fsw_r.core.finger_articulation import articulate_joint_pose
from fsw_r.core.fswr_converter import PositionedSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.timeline.anchor import SIGNBOX_TO_BODY_SCALE, anchor
from fsw_r.timeline.classify import role_of, track_for_posture
from fsw_r.timeline.errors import UnsupportedSignError
from fsw_r.timeline.types import Keyframe, SignTimeline, SymbolRole, Track

# UNVERIFIED ASSUMPTION: no data source yet gives a real sign's duration.
# Category 3 (Dynamics) is expected to eventually supply this (see
# ROADMAP.md) -- until then, every MVP-1 timeline gets the same constant.
# Not measured, not calibrated -- a placeholder with a name, not a bare
# number scattered through the code.
DEFAULT_SIGN_DURATION = 0.8


def build_timeline(positioned_symbols: tuple[PositionedSymbol, ...]) -> SignTimeline:
    """Raises ``UnsupportedSignError`` for anything outside MVP-1's scope
    (see module docstring)."""
    postures = []
    transitions = []
    for positioned in positioned_symbols:
        # Gate on the literal ISWA category, not SymbolRole -- Category 4
        # (Head & Face) also classifies as POSTURE (see classify.py's
        # _ROLE_BY_CATEGORY, shared with Category 1), but MVP-1's scope is
        # "Category 1 and Category 2 only," which is narrower than "any
        # POSTURE/TRANSITION symbol." role_of() is still called so its own
        # validation runs and its label can be used in the error message.
        category = positioned.symbol.category
        role = role_of(positioned)
        if category == 1 and role == SymbolRole.POSTURE:
            postures.append(positioned)
        elif category == 2 and role == SymbolRole.TRANSITION:
            transitions.append(positioned)
        else:
            raise UnsupportedSignError(
                f"MVP-1 only supports Category 1 (hand posture) and Category 2 "
                f"(movement) symbols; found a category {category} ({role.value}) "
                f"symbol ({positioned.symbol.symbol_id})"
            )

    if len(postures) != 1:
        raise UnsupportedSignError(
            f"MVP-1 only supports signs with exactly 1 hand (Category 1) symbol; "
            f"found {len(postures)}"
        )
    if len(transitions) > 1:
        raise UnsupportedSignError(
            f"MVP-1 only supports signs with at most 1 movement (Category 2) symbol; "
            f"found {len(transitions)}"
        )

    hand = postures[0]
    hand_symbol = hand.symbol
    assert isinstance(hand_symbol, HandSymbol)  # role_of() already guarantees Category 1
    track_name = track_for_posture(hand_symbol.hand_side)
    base_position = anchor(hand.x, hand.y)
    joint_pose = hand_symbol.get_joint_pose()
    wrist = hand_symbol.get_wrist_orientation()

    keyframes: tuple[Keyframe, ...]
    if not transitions:
        # D3, no movement: a single static keyframe.
        keyframes = (
            Keyframe(time=0.0, joint_pose=joint_pose, wrist=wrist, position=base_position),
        )
    else:
        motion_symbol = transitions[0].symbol
        assert isinstance(motion_symbol, MovementSymbol)  # role_of() guarantees Category 2
        # D2: MovementSymbol.hand_side is None (see its own docstring --
        # no rule for Category 2 hand_side exists yet). MVP-1's scope
        # (at most 1 hand track) means there's only ever one track to
        # assign it to -- unambiguous here, NOT because the general
        # problem is solved. TODO(MVP-2): once >1 track can exist, this
        # needs real inference (spatial distance + fill, see ROADMAP.md).
        path = motion_symbol.get_motion_path()
        trajectory = sample_trajectory(path, motion_symbol.rotation)
        # This task's own addition ("Chuyển động khớp ngón tay"): a Group
        # 12 (Finger Movement) symbol has a FingerArticulation -- None for
        # every other Category 2 symbol (see MovementSymbol.
        # get_finger_articulation()'s own docstring). When present, EACH
        # keyframe's joint_pose is re-derived at that keyframe's own time
        # instead of reusing the same static joint_pose for all of them --
        # this is the ONLY thing that changes: position is still the
        # trajectory's own points (a fixed point for PathType.FINGER, see
        # core/movement_paths.py -- the wrist does not move), computed
        # exactly the same way as any other Category 2 symbol below.
        articulation = motion_symbol.get_finger_articulation()
        # D3/D4: the brief's literal spec is 2 keyframes (repeat+1 when
        # MotionPath.repeat > 1) taken from the trajectory's endpoints.
        # Deliberately generalized here to one keyframe PER point
        # sample_trajectory() returns, not just the endpoints: with only
        # 2 keyframes, a CURVED or CIRCLE path would get linearly
        # interpolated in sample.py straight from start to end, flattening
        # the arc into a straight line -- exactly what the "don't let
        # interpolation override the arrow-defined trajectory" rule (see
        # sample.py) exists to prevent. For PathType.STRAIGHT the
        # intermediate points are collinear, so this is behaviorally
        # identical to the 2-keyframe case; it only matters for
        # CURVED/CIRCLE. Positions are the trajectory's own points (offset
        # by the hand's anchor and scaled), never invented separately. The
        # same dense-keyframes-plus-linear-interpolation reasoning is
        # exactly why a FINGER articulation's sinusoidal oscillation
        # (evaluated once per keyframe here) survives sample.py's linear
        # interpolation as a visibly smooth wiggle instead of a flattened
        # straight ramp between two extremes -- no changes to sample.py
        # needed.
        times = np.linspace(0.0, 1.0, len(trajectory))
        keyframes = tuple(
            Keyframe(
                time=float(t),
                joint_pose=articulate_joint_pose(joint_pose, articulation, float(t)) if articulation is not None else joint_pose,
                wrist=wrist,
                position=base_position + point * SIGNBOX_TO_BODY_SCALE,
            )
            for t, point in zip(times, trajectory)
        )

    track = Track(name=track_name, keyframes=keyframes)
    return SignTimeline(tracks=(track,), duration_seconds=DEFAULT_SIGN_DURATION)
