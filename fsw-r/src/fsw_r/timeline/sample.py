"""D5: samples a ``SignTimeline`` into a fixed-FPS sequence of
``PoseFrame``. One interpolation method per kind of quantity:

    wrist orientation (quaternion) -> SLERP
    joint angle (scalar)           -> linear
    position                       -> linear between build.py's keyframes

Position is linear here, same mechanism as joint angles -- the trajectory
SHAPE itself is not re-derived by this module. It's already baked into how
many keyframes ``build.py`` generated (one per ``sample_trajectory()``
point for a moving track, see its docstring) -- so linearly interpolating
between adjacent, already-dense keyframes closely follows the real
curve/circle instead of flattening it. This module never calls
``sample_trajectory()`` itself.

**Quaternion double-cover:** ``q`` and ``-q`` represent the identical
rotation. If two consecutive keyframes' quaternions have a negative dot
product, naive SLERP takes the long way around (350 degrees instead of
10). Checked directly, empirically, whether
``scipy.spatial.transform.Slerp`` (scipy 1.15.3, the version this project
runs) already handles this -- constructed two rotations 10 degrees apart,
deliberately negated one's quaternion (forcing dot < 0), and fed both into
``Slerp``: the interpolated path still went the short way (0 -> 10 degrees
in a straight line, not through 350). So it IS already handled internally
-- no manual sign-flip is added here (that would be redundant, dead code).
This is pinned by ``tests/test_sample.py``'s
``test_slerp_takes_the_short_path`` as a regression guard, in case a
future scipy version changes that internal behavior.
"""

from __future__ import annotations

from scipy.spatial.transform import Rotation, Slerp

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose
from fsw_r.timeline.types import Keyframe, PoseFrame, SignTimeline, Track, TrackPose

DEFAULT_FPS = 25


def _lerp_joint_angle(a: JointAngle, b: JointAngle, t: float) -> JointAngle:
    return JointAngle(
        flexion=a.flexion + (b.flexion - a.flexion) * t,
        abduction=a.abduction + (b.abduction - a.abduction) * t,
    )


def _lerp_finger(a: FingerPose, b: FingerPose, t: float) -> FingerPose:
    return FingerPose(
        mcp=_lerp_joint_angle(a.mcp, b.mcp, t),
        pip=_lerp_joint_angle(a.pip, b.pip, t),
        dip=_lerp_joint_angle(a.dip, b.dip, t),
    )


def _lerp_thumb(a: ThumbPose, b: ThumbPose, t: float) -> ThumbPose:
    return ThumbPose(
        cmc=_lerp_joint_angle(a.cmc, b.cmc, t),
        mcp=_lerp_joint_angle(a.mcp, b.mcp, t),
        ip=_lerp_joint_angle(a.ip, b.ip, t),
    )


def _lerp_joint_pose(a: HandJointPose, b: HandJointPose, t: float) -> HandJointPose:
    return HandJointPose(
        thumb=_lerp_thumb(a.thumb, b.thumb, t),
        index=_lerp_finger(a.index, b.index, t),
        middle=_lerp_finger(a.middle, b.middle, t),
        ring=_lerp_finger(a.ring, b.ring, t),
        pinky=_lerp_finger(a.pinky, b.pinky, t),
    )


def _slerp_wrist(a: Rotation, b: Rotation, t: float) -> Rotation:
    """See module docstring for why this doesn't need a manual
    double-cover fix -- scipy's Slerp already handles it."""
    if t <= 0.0:
        return a
    if t >= 1.0:
        return b
    slerp = Slerp([0.0, 1.0], Rotation.concatenate([a, b]))
    result: Rotation = slerp([t])[0]
    return result


def _find_bracket(keyframes: tuple[Keyframe, ...], t: float) -> tuple[Keyframe, Keyframe, float]:
    if t <= keyframes[0].time:
        return keyframes[0], keyframes[0], 0.0
    if t >= keyframes[-1].time:
        return keyframes[-1], keyframes[-1], 0.0
    for left, right in zip(keyframes, keyframes[1:]):
        if left.time <= t <= right.time:
            span = right.time - left.time
            local_t = (t - left.time) / span if span > 0 else 0.0
            return left, right, local_t
    raise AssertionError("unreachable: t is within [keyframes[0].time, keyframes[-1].time]")  # pragma: no cover


def _interpolate_track_at(track: Track, t: float) -> TrackPose:
    left, right, local_t = _find_bracket(track.keyframes, t)

    joint_pose = None
    if left.joint_pose is not None and right.joint_pose is not None:
        joint_pose = _lerp_joint_pose(left.joint_pose, right.joint_pose, local_t)

    wrist = None
    if left.wrist is not None and right.wrist is not None:
        wrist = _slerp_wrist(left.wrist, right.wrist, local_t)

    position = None
    if left.position is not None and right.position is not None:
        position = left.position + (right.position - left.position) * local_t

    return TrackPose(joint_pose=joint_pose, wrist=wrist, position=position)


def sample(timeline: SignTimeline, fps: int = DEFAULT_FPS) -> tuple[PoseFrame, ...]:
    """Samples every track at ``fps`` frames per second across the
    timeline's full ``duration_seconds``. 25 fps by default, matching the
    target rendering system."""
    frame_count = round(timeline.duration_seconds * fps)
    frames = []
    for i in range(frame_count):
        time_seconds = i / fps
        t_norm = time_seconds / timeline.duration_seconds if timeline.duration_seconds > 0 else 0.0
        t_norm = min(t_norm, 1.0)
        tracks = {track.name: _interpolate_track_at(track, t_norm) for track in timeline.tracks}
        frames.append(PoseFrame(time_seconds=time_seconds, tracks=tracks))
    return tuple(frames)
