from __future__ import annotations

import numpy as np
import pytest
from scipy.spatial.transform import Rotation, Slerp

from fsw_r.timeline.sample import DEFAULT_FPS, sample
from fsw_r.timeline.types import Keyframe, SignTimeline, Track, TrackName


def test_slerp_takes_the_short_path() -> None:
    """E4 -- quaternion double-cover. Two rotations 10 degrees apart
    around Z, with the second's quaternion deliberately negated (q and -q
    represent the identical rotation, so this changes nothing physically,
    but forces dot(q1, q2) < 0 -- the exact condition that makes naive
    SLERP take the long way around). The interpolated path must still
    total ~10 degrees, not ~350."""
    r1 = Rotation.from_euler("z", 0, degrees=True)
    r2 = Rotation.from_euler("z", 10, degrees=True)
    r2_negated_quat = Rotation.from_quat(-r2.as_quat())
    assert np.dot(r1.as_quat(), r2_negated_quat.as_quat()) < 0  # confirms the adversarial setup

    timeline = SignTimeline(
        tracks=(
            Track(
                name=TrackName.RIGHT_HAND,
                keyframes=(
                    Keyframe(time=0.0, joint_pose=None, wrist=r1, position=None),
                    Keyframe(time=1.0, joint_pose=None, wrist=r2_negated_quat, position=None),
                ),
            ),
        ),
        duration_seconds=1.0,
    )
    fps = 100
    frames = sample(timeline, fps=fps)
    angles = []
    for frame in frames:
        wrist = frame.tracks[TrackName.RIGHT_HAND].wrist
        assert wrist is not None
        angles.append(wrist.as_euler("zyx", degrees=True)[0])

    total_traversal = sum(abs(angles[i + 1] - angles[i]) for i in range(len(angles) - 1))
    # sample()'s frames run from t=0 up to (frame_count-1)/fps, not all the
    # way to t=1.0 -- expected traversal scales with how much of the 0->10
    # degree sweep was actually covered by the sampled frames.
    max_t_covered = (len(frames) - 1) / fps
    expected_traversal = max_t_covered * 10.0
    assert total_traversal == pytest.approx(expected_traversal, abs=0.2)
    # The real point of this test: nowhere near the ~350-degree long way.
    assert total_traversal < 15.0


def test_scipy_slerp_itself_already_handles_double_cover() -> None:
    """Documents the empirical finding directly (see sample.py's module
    docstring): scipy.spatial.transform.Slerp needs no manual sign-flip
    fix. If a future scipy version regresses this, this test (not just
    the higher-level one above) should be the first to fail."""
    r1 = Rotation.from_euler("z", 0, degrees=True)
    r2 = Rotation.from_euler("z", 10, degrees=True)
    r2_negated = Rotation.from_quat(-r2.as_quat())
    slerp = Slerp([0.0, 1.0], Rotation.concatenate([r1, r2_negated]))
    midpoint = slerp([0.5])[0]
    assert abs(midpoint.as_euler("zyx", degrees=True)[0] - 5.0) < 0.5


def test_frame_count_matches_duration_and_fps() -> None:
    # E5
    timeline = SignTimeline(
        tracks=(
            Track(
                name=TrackName.RIGHT_HAND,
                keyframes=(Keyframe(time=0.0, joint_pose=None, wrist=None, position=None),),
            ),
        ),
        duration_seconds=0.8,
    )
    frames = sample(timeline, fps=25)
    assert len(frames) == 20


def test_default_fps_is_25() -> None:
    assert DEFAULT_FPS == 25
