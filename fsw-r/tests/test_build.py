from __future__ import annotations

from unittest.mock import Mock

import pytest

from fsw_r.core.fswr_converter import PositionedSymbol, fsw_to_fswr
from fsw_r.timeline.build import DEFAULT_SIGN_DURATION, build_timeline
from fsw_r.timeline.errors import UnsupportedSignError
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import TrackName


def test_two_hand_symbols_build_two_tracks() -> None:
    # MVP-2: a RIGHT + LEFT sign (was UnsupportedSignError at MVP-1) now
    # builds one track per hand. S10010 rotation=0 -> RIGHT; S1061a
    # rotation=a -> LEFT.
    positioned = fsw_to_fswr("M500x500S10010480x480S1061a520x520")
    timeline = build_timeline(positioned)
    assert {t.name for t in timeline.tracks} == {TrackName.RIGHT_HAND, TrackName.LEFT_HAND}
    assert len(timeline.tracks) == 2


def test_two_same_side_hand_symbols_is_unsupported() -> None:
    # MVP-2: two RIGHT postures ("one hand, two postures") is still ambiguous.
    positioned = fsw_to_fswr("M500x500S10010480x480S10010520x520")
    with pytest.raises(UnsupportedSignError, match="at most one posture per hand"):
        build_timeline(positioned)


def test_three_hand_symbols_is_unsupported() -> None:
    positioned = fsw_to_fswr("M500x500S10010480x480S1001a500x500S10010520x520")
    with pytest.raises(UnsupportedSignError, match="1 or 2 hand"):
        build_timeline(positioned)


def test_two_movements_on_the_same_hand_is_unsupported() -> None:
    # MVP-2: one hand, two movements ("one hand, two moments") stays out of
    # scope -- both movements route to the single RIGHT track.
    positioned = fsw_to_fswr("M500x500S10010480x480S22a10500x500S26510520x520")
    with pytest.raises(UnsupportedSignError, match="at most 1 movement"):
        build_timeline(positioned)


def test_category_4_symbol_is_unsupported() -> None:
    # E3 -- Category 4 (Head & Face) isn't implemented in core/ yet (only
    # 1 and 2 are registered, see core/registry.py's _CATEGORY_SYMBOL), so
    # fsw_to_fswr() itself would already reject a real Category 4 key --
    # this exercises MVP-1's OWN scope check in isolation with a stand-in
    # symbol, for when Category 4 does exist. Notably, Category 4 shares
    # SymbolRole.POSTURE with Category 1 (see classify.py's
    # _ROLE_BY_CATEGORY) -- build_timeline() must still reject it, because
    # MVP-1's scope is "Category 1 and 2 only," not "any POSTURE role."
    hand = fsw_to_fswr("M500x500S10010480x480")[0]
    fake_head_symbol = Mock(category=4, symbol_id="04-22-001")
    fake_head = PositionedSymbol(symbol=fake_head_symbol, x=500, y=480)
    with pytest.raises(UnsupportedSignError, match="category 4"):
        build_timeline((hand, fake_head))


def test_category_3_symbol_is_unsupported() -> None:
    # C6 -- Category 3 (Dynamics) is now a real, registered core/ symbol
    # (this project's Category 3/5 task), so this is a REAL FSW key, not a
    # Mock stand-in like test_category_4_symbol_is_unsupported above --
    # fsw_to_fswr() parses it successfully; build_timeline() must still
    # reject it, confirming Category 3 was deliberately NOT wired into
    # SignTimeline in that same task (see PROGRESS.md's Category 3/5 entry
    # -- "làm tầng ký hiệu... không đụng animation").
    positioned = fsw_to_fswr("M500x500S10010480x480S2f710500x500")  # Index + Fast (Dynamics)
    with pytest.raises(UnsupportedSignError, match="category 3"):
        build_timeline(positioned)


def test_category_5_symbol_is_unsupported() -> None:
    # C6 -- same reasoning as test_category_3_symbol_is_unsupported, for
    # Category 5 (Trunk & Limb / Body).
    positioned = fsw_to_fswr("M500x500S10010480x480S36d10500x500")  # Index + Shoulder Hip Spine (Body)
    with pytest.raises(UnsupportedSignError, match="category 5"):
        build_timeline(positioned)


def test_zero_hand_symbols_is_unsupported() -> None:
    # E3 -- a movement symbol with no hand at all.
    positioned = fsw_to_fswr("M500x500S22a10500x500")
    with pytest.raises(UnsupportedSignError, match="1 or 2 hand"):
        build_timeline(positioned)


def test_valid_mvp1_sign_does_not_raise() -> None:
    # E3
    positioned = fsw_to_fswr("M500x500S10010480x480")
    build_timeline(positioned)  # must not raise


def test_static_sign_has_one_keyframe_and_uses_default_duration() -> None:
    # E6
    positioned = fsw_to_fswr("M500x500S10010480x480")
    timeline = build_timeline(positioned)
    assert timeline.duration_seconds == DEFAULT_SIGN_DURATION
    assert len(timeline.tracks) == 1
    assert len(timeline.tracks[0].keyframes) == 1


def test_moving_sign_first_and_last_keyframe_differ_in_position_only() -> None:
    # E7
    positioned = fsw_to_fswr("M500x500S10010480x480S22a10500x500")
    timeline = build_timeline(positioned)
    keyframes = timeline.tracks[0].keyframes
    assert len(keyframes) > 1
    first, last = keyframes[0], keyframes[-1]
    assert first.joint_pose == last.joint_pose
    assert first.position is not None
    assert last.position is not None
    assert not (first.position == last.position).all()


def test_hand_side_determines_track() -> None:
    right = fsw_to_fswr("M500x500S10010480x480")  # rotation=0 -> RIGHT
    left = fsw_to_fswr("M500x500S1001a480x480")  # rotation=10 -> LEFT
    assert build_timeline(right).tracks[0].name == TrackName.RIGHT_HAND
    assert build_timeline(left).tracks[0].name == TrackName.LEFT_HAND


# E8 -- real FSW strings within MVP-1 scope, run end-to-end as a
# regression fixture. Static signs use real Category 1 base symbols;
# moving signs pair one with a real Category 2 base symbol.
REAL_MVP1_SIGNS = [
    "M500x500S10010480x480",  # Index, static
    "M500x500S14c10480x480",  # Five Fingers Spread, static
    "M500x500S1cd10480x480",  # Middle Ring Baby, static
    "M500x500S1f510480x480",  # Thumb, static
    "M500x500S10010480x480S22a10500x500",  # Index + Straight Wall Plane
    "M500x500S14c10480x480S26510500x500",  # Five Fingers Spread + Straight Floor Plane
    "M500x500S1cd10480x480S2b710500x500",  # Middle Ring Baby + Curves Hit Wall Plane
    "M500x500S1f510480x480S2ea10500x500",  # Thumb + Circles
    "M500x500S1061a480x480S22a10500x500",  # Index Bent (LEFT) + Straight Wall Plane
]


@pytest.mark.parametrize("fsw", REAL_MVP1_SIGNS)
def test_real_fsw_signs_build_end_to_end(fsw: str) -> None:
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    assert len(timeline.tracks) == 1
    assert len(timeline.tracks[0].keyframes) >= 1
    frames = sample(timeline)
    assert len(frames) == round(DEFAULT_SIGN_DURATION * 25)


# --- MVP-2: two hands + fill-based movement routing ---

_TWO_HANDS = "M500x500S10010480x480S1001a500x500"  # RIGHT Index + LEFT Index


def _keyframes_by_track(fsw: str) -> dict[TrackName, int]:
    timeline = build_timeline(fsw_to_fswr(fsw))
    return {track.name: len(track.keyframes) for track in timeline.tracks}


def test_movement_fill0_routes_to_right_hand_only() -> None:
    # Arrowhead fill 0 = dark = RIGHT hand: only the right track gets the
    # movement's dense keyframes; the left stays a single static keyframe.
    counts = _keyframes_by_track(_TWO_HANDS + "S22a00510x510")
    assert counts[TrackName.RIGHT_HAND] > 1
    assert counts[TrackName.LEFT_HAND] == 1


def test_movement_fill1_routes_to_left_hand_only() -> None:
    # Arrowhead fill 1 = light = LEFT hand.
    counts = _keyframes_by_track(_TWO_HANDS + "S22a10510x510")
    assert counts[TrackName.LEFT_HAND] > 1
    assert counts[TrackName.RIGHT_HAND] == 1


def test_movement_fill2_superposed_moves_both_hands() -> None:
    # Arrowhead fill 2 = superposed = BOTH hands: the same movement is
    # applied to both tracks (the "both" case the user chose over a
    # HandSide.BOTH member).
    counts = _keyframes_by_track(_TWO_HANDS + "S22a20510x510")
    assert counts[TrackName.RIGHT_HAND] > 1
    assert counts[TrackName.LEFT_HAND] > 1


def test_two_hand_sign_samples_end_to_end() -> None:
    timeline = build_timeline(fsw_to_fswr(_TWO_HANDS + "S22a20510x510"))
    assert len(timeline.tracks) == 2
    frames = sample(timeline)
    assert len(frames) == round(DEFAULT_SIGN_DURATION * 25)
    # Every sampled frame carries both hand tracks.
    for frame in frames:
        assert set(frame.tracks) == {TrackName.RIGHT_HAND, TrackName.LEFT_HAND}
