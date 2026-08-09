from __future__ import annotations

from unittest.mock import Mock

import pytest

from fsw_r.core.fswr_converter import PositionedSymbol, fsw_to_fswr
from fsw_r.timeline.build import DEFAULT_SIGN_DURATION, build_timeline
from fsw_r.timeline.errors import UnsupportedSignError
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import TrackName


def test_two_hand_symbols_is_unsupported() -> None:
    # E3
    positioned = fsw_to_fswr("M500x500S10010480x480S1061a520x520")
    with pytest.raises(UnsupportedSignError, match="exactly 1 hand"):
        build_timeline(positioned)


def test_two_movement_symbols_is_unsupported() -> None:
    # E3
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


def test_zero_hand_symbols_is_unsupported() -> None:
    # E3 -- a movement symbol with no hand at all.
    positioned = fsw_to_fswr("M500x500S22a10500x500")
    with pytest.raises(UnsupportedSignError, match="exactly 1 hand"):
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
