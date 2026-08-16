"""MVP-3: Category 4 static facial expressions join the timeline as one
FACE track.

Why this scope and not "accept all of Category 4": the Category 4 kinds that
carry a real model but are not wired in yet (``HeadSymbol``'s rigid
orientation, ``FaceMovementSymbol``/``HeadMovementSymbol``'s
expression-over-time) are still REJECTED, because silently ignoring a
head-turn would be exactly the best-effort wrong timeline ``build.py``
refuses to produce. ``AnnotationSymbol`` is carried instead of rejected, and
that is not an inconsistency: an AnnotationSymbol is *defined* as "identified,
no modelled pose", so there is nothing being dropped.
"""

from __future__ import annotations

import pytest

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.errors import UnsupportedSignError
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import TrackName

# One hand (Index) plus one brow expression (0x30a "Eyebrows Straight Up").
HAND_AND_BROWS = "M500x500S10000480x480S30a00500x520"
# Same, plus a mouth expression (0x34c) -- different ARKit channels.
HAND_BROWS_AND_MOUTH = "M500x500S10000480x480S30a00500x520S34c00510x530"
# A hand plus a HeadSymbol (0x2ff) -- has a real orientation model, not wired.
HAND_AND_HEAD = "M500x500S10000480x480S2ff00500x520"
HAND_ONLY = "M500x500S10000480x480"


def _track(timeline: object, name: TrackName) -> object:
    return next(t for t in timeline.tracks if t.name == name)  # type: ignore[attr-defined]


def test_a_face_symbol_adds_a_face_track() -> None:
    timeline = build_timeline(fsw_to_fswr(HAND_AND_BROWS))
    names = [t.name for t in timeline.tracks]
    assert TrackName.RIGHT_HAND in names
    assert TrackName.FACE in names


def test_hand_only_signs_gain_no_face_track() -> None:
    """The face track appears only when the sign actually writes a facial
    expression -- a hand-only sign must be untouched by MVP-3."""
    timeline = build_timeline(fsw_to_fswr(HAND_ONLY))
    assert [t.name for t in timeline.tracks] == [TrackName.RIGHT_HAND]


def test_face_keyframe_carries_an_expression_and_no_hand_pose() -> None:
    timeline = build_timeline(fsw_to_fswr(HAND_AND_BROWS))
    face = _track(timeline, TrackName.FACE)
    (keyframe,) = face.keyframes  # type: ignore[attr-defined]
    assert keyframe.expression is not None
    assert keyframe.joint_pose is None
    assert keyframe.wrist is None
    assert keyframe.position is None


def test_hand_keyframes_carry_no_expression() -> None:
    """The converse: adding the expression field must not leak into hand
    tracks, whose keyframes are built by the unchanged MVP-2 path."""
    timeline = build_timeline(fsw_to_fswr(HAND_AND_BROWS))
    hand = _track(timeline, TrackName.RIGHT_HAND)
    assert all(k.expression is None for k in hand.keyframes)  # type: ignore[attr-defined]


def test_several_face_symbols_merge_into_one_expression() -> None:
    """Brows and mouth describe ONE face at one instant, so they merge rather
    than becoming two competing tracks."""
    timeline = build_timeline(fsw_to_fswr(HAND_BROWS_AND_MOUTH))
    faces = [t for t in timeline.tracks if t.name == TrackName.FACE]
    assert len(faces) == 1
    (keyframe,) = faces[0].keyframes
    assert keyframe.expression is not None
    names = set(keyframe.expression.blendshapes)
    assert any(n.startswith("brow") for n in names)
    assert any(n.startswith("mouth") or n.startswith("jaw") for n in names)


def test_merged_expression_keeps_each_symbols_own_weights() -> None:
    from fsw_r.core.registry import symbol_from_fsw

    brows = symbol_from_fsw("S30a00").get_expression()  # type: ignore[attr-defined]
    timeline = build_timeline(fsw_to_fswr(HAND_BROWS_AND_MOUTH))
    merged = _track(timeline, TrackName.FACE).keyframes[0].expression  # type: ignore[attr-defined]
    for name, weight in brows.blendshapes.items():
        assert merged.blendshapes[name] == weight


def test_conflicting_expressions_raise_rather_than_picking_one() -> None:
    """Two symbols writing the same ARKit channel with different weights is a
    real ambiguity about what the face is doing, so it must not be resolved
    by guessing. 0x315 "Eyes Squeezed" and 0x316 "Eyes Closed" genuinely
    disagree on eyeBlinkLeft/Right -- a real pair, not a constructed one, so
    this exercises the branch instead of skipping it. Measured cost of
    raising: 1.05% of the corpus signs this scope otherwise accepts."""
    from fsw_r.core.face_symbol import FaceSymbol
    from fsw_r.core.fswr_converter import PositionedSymbol
    from fsw_r.timeline.build import _merge_face_expressions

    squeezed = FaceSymbol(base_hex=0x315, fill=0, rotation=0)
    closed = FaceSymbol(base_hex=0x316, fill=0, rotation=0)
    shared = set(squeezed.get_expression().blendshapes) & set(closed.get_expression().blendshapes)
    assert any(
        squeezed.get_expression().blendshapes[n] != closed.get_expression().blendshapes[n]
        for n in shared
    ), "fixture no longer conflicts -- pick another pair rather than deleting the test"

    with pytest.raises(UnsupportedSignError, match="disagree on ARKit channel"):
        _merge_face_expressions(
            [
                PositionedSymbol(symbol=squeezed, x=500, y=500),
                PositionedSymbol(symbol=closed, x=510, y=510),
            ]
        )


def test_agreeing_expressions_are_not_treated_as_a_conflict() -> None:
    """Two symbols setting the same channel to the SAME weight are just
    agreeing; raising there would reject valid signs."""
    from fsw_r.core.face_symbol import FaceSymbol
    from fsw_r.core.fswr_converter import PositionedSymbol
    from fsw_r.timeline.build import _merge_face_expressions

    same = FaceSymbol(base_hex=0x30A, fill=0, rotation=0)
    merged = _merge_face_expressions(
        [
            PositionedSymbol(symbol=same, x=500, y=500),
            PositionedSymbol(symbol=FaceSymbol(base_hex=0x30A, fill=1, rotation=0), x=510, y=510),
        ]
    )
    assert merged.blendshapes == same.get_expression().blendshapes


def test_head_symbols_are_still_rejected_not_silently_dropped() -> None:
    """A HeadSymbol has a real orientation model that the timeline does not
    consume yet. Accepting the sign and ignoring the head would misrepresent
    what was written."""
    with pytest.raises(UnsupportedSignError, match="HeadSymbol"):
        build_timeline(fsw_to_fswr(HAND_AND_HEAD))


def test_sampling_yields_the_expression_on_the_face_track() -> None:
    timeline = build_timeline(fsw_to_fswr(HAND_AND_BROWS))
    frames = sample(timeline, fps=30)
    assert frames
    for frame in frames:
        pose = frame.tracks[TrackName.FACE]
        assert pose.expression is not None
        assert all(0.0 <= v <= 1.0 for v in pose.expression.blendshapes.values())


def test_expression_interpolation_treats_a_missing_channel_as_neutral() -> None:
    """A channel only one endpoint mentions must ease from 0, not jump --
    absent means 0 in FaceExpressionPose, so the union of both key sets is
    what gets interpolated."""
    from fsw_r.core.face_types import FaceExpressionPose
    from fsw_r.timeline.sample import _lerp_expression

    a = FaceExpressionPose(blendshapes={"jawOpen": 1.0})
    b = FaceExpressionPose(blendshapes={"browInnerUp": 1.0})
    mid = _lerp_expression(a, b, 0.5)
    assert mid.blendshapes["jawOpen"] == pytest.approx(0.5)
    assert mid.blendshapes["browInnerUp"] == pytest.approx(0.5)
