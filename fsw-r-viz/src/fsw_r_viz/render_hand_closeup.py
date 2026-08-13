"""Renders a close-up video/GIF of a SINGLE hand, cropped out of a
full-body ``Pose`` and re-centered/magnified -- see this task's brief
("Video cận cảnh bàn tay"), Part 0: at the full-body frame's native
512x512 scale, a hand's own MCP joints sit only ~8.4px apart (measured on
the standard MVP-1 demo sign, ``M508x515S10000493x485S22a04500x500``),
well under ``PoseVisualizer``'s own line thickness at that frame size
(``round(sqrt(w*h)/150)`` = 3px) -- the four fingers render as one solid
blob, unreadable as a handshape. Bumping ``FRAME_WIDTH``/``FRAME_HEIGHT``
does not fix this: that thickness formula scales WITH the frame, so the
line-width-to-finger-gap ratio never improves.

**The full-body video is NOT changed by this module** (it does its own
job -- showing posture/trajectory -- correctly, see
``render_pose_video.py``, untouched by this task). This adds a SECOND
video: a pure DISPLAY-layer transform on an already-computed ``Pose``'s
pixel coordinates (crop to one hand's component, re-center on the wrist,
magnify) -- no new 3D computation, no change to
``fsw_r.export.pose_export`` or any body-space geometry.

**Zoom strategy: anchor the wrist, scale by the hand's OWN size**
(this task's brief, Part A, option (b) -- chosen over option (a), "fit the
whole wrist-trajectory's bounding box"). The purpose of this video is
reading HANDSHAPE, not trajectory (the full-body video already shows
that): for the standard demo sign, the hand's own bounding box relative to
its wrist is a constant 59x115px in every frame (one handshape held for
the whole sign, only the wrist moves along the movement path), while the
wrist-TRAJECTORY's bounding box is inflated to 181px tall by the movement
itself. Anchoring on the hand's own size (not the trajectory) gives a
>50% larger zoom factor (3.6x vs. 2.3x, measured) and clearly-separated
MCP joints (30px vs. 19px, measured -- see PROGRESS.md's own measurement
table for this task) -- at the cost of the wrist appearing to hold still
in frame while the hand's INTERNAL joints still articulate normally,
which is exactly what a handshape-reading close-up needs.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from pose_format import Pose
from pose_format.numpy import NumPyPoseBody
from pose_format.pose_visualizer import PoseVisualizer
from scipy.spatial.transform import Rotation

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.export.pose_export import FRAME_HEIGHT, FRAME_WIDTH, frames_to_pose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import TrackName

# What fraction of the OUTPUT frame's height the hand's own bounding box
# should occupy after zooming in -- the named constant this task's brief
# (Part B3) requires instead of a raw hardcoded zoom factor. Chosen to
# land inside this task's own Part C1 acceptance target (70-90% of frame
# height) with margin on both sides. For the standard demo sign's 114.8px-
# tall hand (see module docstring), this alone works out to a
# 0.8 * 512 / 114.8 = 3.57x zoom -- matches the brief's own independently
# measured ~3.6x almost exactly, confirming this is the right constant to
# name (not the zoom factor itself, which is DERIVED per hand/sign, not
# fixed -- see render_hand_closeup()).
HAND_CLOSEUP_TARGET_FRACTION = 0.8

# PoseVisualizer's own default thickness (round(sqrt(w*h)/150) = 3px at
# 512x512) is sized for a FULL BODY at that scale, not a zoomed-in hand --
# at this task's own ~3.6x zoom, 3px is still noticeably thick relative to
# a single finger segment. MEASURED by rendering both and comparing by eye
# (this task's brief, Part B2 -- not guessed): 2px reads as clearly
# separated, individually-readable finger segments at this zoom; 3px
# starts visually blending adjacent phalanges together on the curled
# fingers (see PROGRESS.md's own note for this task).
HAND_CLOSEUP_THICKNESS = 2

# "Góc nhìn 3/4 cho video cận cảnh bàn tay" task, Part 0/A1: PoseVisualizer
# projects orthogonally onto the XY plane -- Z is used ONLY for painter's-
# algorithm draw order, never for position (see pose_export.py's own
# docstring). A joint that flexes mostly in Z (e.g. MCP flexion swinging a
# fingertip toward the palm, which this project's own Group 12 finger
# articulation does -- measured on the standard demo sign,
# ``M508x515S10000493x485S22100500x500``: the middle fingertip moves
# X=0.000 Y=-0.458 Z=-0.207 body-space units between frames 7 and 13) is
# nearly invisible head-on -- the arc a flexing finger sweeps gets flattened
# into what looks like a straight shortening, not a bend.
#
# MEASURED trade-off (not guessed), rotating the hand about Y before the
# existing wrist-anchor/scale step (see hand_closeup_pose() -- this turns
# part of Z into visible X, revealing the arc):
#
#   angle | visible flex amplitude | finger separation (px)
#   0 deg (current)  | 0.354 | 0.158
#   30 deg           | 0.395 | 0.148
#   45 deg           | 0.430 | 0.137
#   60 deg           | 0.461 | 0.124
#   90 deg (edge-on) | 0.489 | 0.109
#
# 60 was chosen: +30% visible-flex over 0 deg for only -22% finger
# separation: 90 deg buys another +6% flex for another -12% separation --
# a much worse trade past 60. This is a VISUAL judgment call, not a derived
# optimum -- see PROGRESS.md's entry for this task for the actual GIF
# comparison this was chosen from (rendered both 0 and this angle, viewed
# both, not picked from the table alone).
HAND_CLOSEUP_VIEW_ANGLE_DEG = 60.0

_HAND_COMPONENT_BY_TRACK: dict[TrackName, str] = {
    TrackName.RIGHT_HAND: "RIGHT_HAND_LANDMARKS",
    TrackName.LEFT_HAND: "LEFT_HAND_LANDMARKS",
}


def _hand_component_range(pose: Pose, component_name: str) -> tuple[int, int]:
    """(start index, point count) of ``component_name`` within the
    flattened per-frame point array -- computed from the header actually
    on ``pose`` (never assumed), via ``PoseHeader``'s own public
    ``get_point_index``, the same public API ``fsw_r.export.pose_export``
    uses for this (that module's own ``_component_offsets`` is private to
    that package, not reused here across the package boundary)."""
    for component in pose.header.components:
        if component.name == component_name:
            start = pose.header.get_point_index(component_name, component.points[0])
            return start, len(component.points)
    raise ValueError(f"Pose header has no component named {component_name!r}")


def hand_closeup_pose(pose: Pose, hand: TrackName, view_angle_deg: float = 0.0) -> Pose:
    """Pure data transform (no video encoding) -- builds the close-up
    ``Pose`` for ONE hand (``hand`` -- RIGHT or LEFT) cropped out of
    ``pose``. Split out from ``render_hand_closeup`` below so this
    transform is directly testable (see ``tests/
    test_render_hand_closeup.py``'s C1-C3/C5) without needing a real
    ffmpeg/vidgear install or writing a file to disk -- the same reasoning
    ``fsw_r.export.pose_export.frames_to_pose`` is kept separate from
    ``render_pose_video.py``'s video encoding for.

    Every other component (the other hand, POSE_LANDMARKS,
    FACE_LANDMARKS, ...) is forced to confidence 0, so only the target
    hand draws. Within the target hand's own points: each frame is
    re-centered on that frame's WRIST (so the hand holds still in the
    output frame instead of drifting along its body-space movement path --
    the full-body video already shows that path), ROTATED about Y by
    ``view_angle_deg`` (this task's brief, "Góc nhìn 3/4" -- see
    ``HAND_CLOSEUP_VIEW_ANGLE_DEG``'s own comment for why: flexion that
    moves mostly in Z is invisible to PoseVisualizer's orthogonal XY
    projection, and rotating about Y turns part of that Z motion into
    visible X), and magnified by a single scale factor derived from
    ``HAND_CLOSEUP_TARGET_FRACTION`` and the hand's OWN measured bounding
    box (not the trajectory's -- see module docstring's "Zoom strategy").
    ``view_angle_deg`` DEFAULTS TO 0 (a no-op/identity rotation) --
    deliberately, so every caller written before the "Góc nhìn 3/4" task
    (including that task's OWN pre-existing tests and demo.py's
    ``_render_hand_closeup_demo``/``_render_finger_movement_demo``, which
    call this without an angle) keeps reproducing the exact pre-rotation
    output with zero code changes -- see this task's brief B1. Pass
    ``HAND_CLOSEUP_VIEW_ANGLE_DEG`` explicitly to get the 3/4 view.

    ROTATION HAPPENS BEFORE the bounding-box measurement/scale/anchor
    steps below, not after (this task's brief, Part A2, explicit ordering
    requirement) -- computing the zoom factor from the UN-rotated extent
    would size the hand for a bounding box that doesn't match what
    actually gets drawn once rotated.

    The vertical anchor point is NOT fixed at frame center: it is
    computed so the hand's own vertical extent (relative to the wrist,
    measured across every frame the hand is active in, not just frame 0,
    AFTER rotation) is centered in the output frame -- for a handshape
    where the fingers curl/point mostly one way from the wrist (the
    common case), this naturally places the wrist BELOW center, leaving
    the fingers room to extend into the frame without being clipped,
    exactly what the "video cận cảnh bàn tay" task's brief Part B1 asked
    for ("neo WRIST về tâm khung, hoặc điểm thấp hơn tâm") -- computed
    from the real (rotated) content instead of a second guessed constant.
    The horizontal anchor IS fixed at frame center (that task's C3): the
    standard demo sign's hand happens to stay roughly symmetric left-right
    around the wrist even after rotation, so this does not need the same
    data-driven treatment to stay on-frame.

    Raises ``ValueError`` if ``hand`` is never active (confidence 0 in
    every frame) -- there is nothing to zoom into, and silently emitting
    an empty video would hide that rather than reporting it.
    """
    component_name = _HAND_COMPONENT_BY_TRACK[hand]
    start, count = _hand_component_range(pose, component_name)
    wrist_local_index = pose.header.get_point_index(component_name, "WRIST") - start
    view_rotation = Rotation.from_euler("y", view_angle_deg, degrees=True)

    data: NDArray[np.float64] = np.array(pose.body.data, dtype=np.float64, copy=True)
    confidence: NDArray[np.float64] = np.array(pose.body.confidence, dtype=np.float64, copy=True)
    frame_count = data.shape[0]

    active_frames = [f for f in range(frame_count) if confidence[f, 0, start:start + count].sum() > 0]
    if not active_frames:
        raise ValueError(f"{hand} is never active (confidence 0 in every frame) -- nothing to render a close-up of")

    # Rotate each active frame's wrist-relative points FIRST (Part A2's
    # ordering requirement), then reuse these same rotated vectors for
    # both the extent measurement below and the final placement -- one
    # rotation per point, not two.
    rotated_rel_by_frame: dict[int, NDArray[np.float64]] = {}
    for frame_index in active_frames:
        points = data[frame_index, 0, start:start + count, :]
        wrist = points[wrist_local_index]
        rotated_rel_by_frame[frame_index] = view_rotation.apply(points - wrist)

    # MEASURE the hand's own VERTICAL extent relative to its own wrist,
    # across EVERY active frame (not just frame 0 -- this project's own
    # "measure, don't assume" rule, see PROGRESS.md), AFTER rotation, so a
    # hypothetical frame-varying handshape would still be sized/centered
    # to fit every frame, not just the first. Height only, not width:
    # this task's own C1 targets frame HEIGHT, and the standard demo
    # sign's hand stays taller than wide even after rotation -- height is
    # the binding dimension for this sign, and the horizontal anchor is
    # fixed at frame center regardless (see this function's own
    # docstring).
    all_rel_y = np.concatenate([rotated_rel_by_frame[f][:, 1] for f in active_frames])

    height_extent = float(all_rel_y.max() - all_rel_y.min())
    if height_extent <= 0:
        raise ValueError(f"{hand}'s bounding box has zero height -- cannot derive a zoom factor")
    scale = (HAND_CLOSEUP_TARGET_FRACTION * FRAME_HEIGHT) / height_extent

    anchor_x = FRAME_WIDTH / 2.0
    anchor_y = FRAME_HEIGHT / 2.0 - scale * float(all_rel_y.min() + all_rel_y.max()) / 2.0

    # Zero out every point outside the target hand's own slice -- "close-
    # up of ONE hand", not "full body, coincidentally zoomed."
    confidence[:, :, :] = 0.0

    for frame_index in active_frames:
        transformed = rotated_rel_by_frame[frame_index] * scale
        transformed[:, 0] += anchor_x
        transformed[:, 1] += anchor_y
        # z is left anchor-free (relative-depth-only, see PoseVisualizer's
        # painter's-algorithm sort in pose_export.py's own docstring) --
        # only scaled, like x/y, to keep depth ordering consistent.
        data[frame_index, 0, start:start + count, :] = transformed
        confidence[frame_index, 0, start:start + count] = pose.body.confidence[frame_index, 0, start:start + count]

    closeup_body = NumPyPoseBody(fps=pose.body.fps, data=data, confidence=confidence)
    return Pose(header=pose.header, body=closeup_body)


def render_hand_closeup(pose: Pose, path: Path, hand: TrackName, view_angle_deg: float = 0.0) -> Path:
    """Writes a close-up video/GIF of ONE hand (``hand`` -- RIGHT or LEFT)
    cropped out of ``pose`` -- see ``hand_closeup_pose`` above for the
    actual data transform this wraps with video/GIF encoding.
    ``view_angle_deg`` defaults to 0 (the original Pha 12 straight-on
    view, unchanged) for the same backward-compatibility reason as
    ``hand_closeup_pose`` -- pass ``HAND_CLOSEUP_VIEW_ANGLE_DEG``
    explicitly for the 3/4 view (see ``demo.py``'s
    ``_render_finger_movement_3q_demo``)."""
    closeup_pose = hand_closeup_pose(pose, hand, view_angle_deg)
    visualizer = PoseVisualizer(closeup_pose, thickness=HAND_CLOSEUP_THICKNESS)
    try:
        visualizer.save_video(str(path), visualizer.draw())
        return path
    except Exception as e:  # noqa: BLE001 -- same deliberately-broad fallback as render_pose_video.py
        gif_path = path.with_suffix(".gif")
        print(
            f"WARNING: save_video() failed ({type(e).__name__}: {e}) -- "
            f"this environment is missing 'vidgear' and/or a real ffmpeg "
            f"binary. Falling back to save_gif() at {gif_path} instead."
        )
        visualizer.save_gif(str(gif_path), visualizer.draw())
        return gif_path


# Two-hand close-up: each hand gets HALF the output frame, centered in its
# half, so BOTH handshapes are readable at once (the full-body video collapses
# them into overlapping blobs -- see PROGRESS.md's Pha 17/18). The subject's
# RIGHT hand is drawn on the VIEWER's left and the LEFT hand on the viewer's
# right, the same selfie-mirror convention pose_export.py uses (subject right
# -> negative body x -> left of screen). Fraction 0.8 (not 1.0) leaves a margin
# so a wide handshape doesn't touch the frame edge or the centre seam.
TWO_HAND_CLOSEUP_TARGET_FRACTION = 0.8
_TWO_HAND_ANCHOR_X_FRACTION: dict[TrackName, float] = {
    TrackName.RIGHT_HAND: 0.25,  # viewer's left
    TrackName.LEFT_HAND: 0.75,  # viewer's right
}


def two_hand_closeup_pose(pose: Pose, view_angle_deg: float = HAND_CLOSEUP_VIEW_ANGLE_DEG) -> Pose:
    """Like ``hand_closeup_pose`` but shows BOTH hands at once, side by side --
    each cropped out, re-centered on its own wrist, rotated about Y by
    ``view_angle_deg`` (see ``HAND_CLOSEUP_VIEW_ANGLE_DEG``), and magnified so
    it fills its half of the frame. Both hands share ONE scale -- the smaller
    of their two fit factors -- so they're the same size and directly
    comparable (a two-handed sign's two handshapes read at a glance instead of
    overlapping into one blob at full-body scale).

    Only hands that are actually active (non-zero confidence in some frame) are
    drawn; a one-handed sign therefore shows a single hand in its own half.
    Raises ``ValueError`` if NEITHER hand is ever active (nothing to render).

    A pure data transform (no encoding), split out for direct testing, same as
    ``hand_closeup_pose``.
    """
    view_rotation = Rotation.from_euler("y", view_angle_deg, degrees=True)
    data: NDArray[np.float64] = np.array(pose.body.data, dtype=np.float64, copy=True)
    confidence: NDArray[np.float64] = np.array(pose.body.confidence, dtype=np.float64, copy=True)
    frame_count = data.shape[0]

    # Per active hand: its point slice, active frames, and rotated
    # wrist-relative points (rotated FIRST, like hand_closeup_pose, so the fit
    # is measured on what actually gets drawn).
    hands: dict[TrackName, tuple[int, int, list[int], dict[int, NDArray[np.float64]]]] = {}
    for hand, component_name in _HAND_COMPONENT_BY_TRACK.items():
        start, count = _hand_component_range(pose, component_name)
        wrist_local_index = pose.header.get_point_index(component_name, "WRIST") - start
        active_frames = [f for f in range(frame_count) if confidence[f, 0, start : start + count].sum() > 0]
        if not active_frames:
            continue
        rotated_rel = {
            f: view_rotation.apply(data[f, 0, start : start + count, :] - data[f, 0, start + wrist_local_index, :])
            for f in active_frames
        }
        hands[hand] = (start, count, active_frames, rotated_rel)

    if not hands:
        raise ValueError("neither hand is active in any frame -- nothing to render a two-hand close-up of")

    # One shared scale so both hands are the same size: the SMALLEST factor
    # that still fits each hand's own height in TARGET_FRACTION of the frame
    # height AND its width in TARGET_FRACTION of a half-frame width.
    half_width = FRAME_WIDTH / 2.0
    scale = float("inf")
    for _start, _count, active_frames, rotated_rel in hands.values():
        rel_y = np.concatenate([rotated_rel[f][:, 1] for f in active_frames])
        rel_x = np.concatenate([rotated_rel[f][:, 0] for f in active_frames])
        height_extent = float(rel_y.max() - rel_y.min())
        width_extent = float(rel_x.max() - rel_x.min())
        if height_extent > 0:
            scale = min(scale, TWO_HAND_CLOSEUP_TARGET_FRACTION * FRAME_HEIGHT / height_extent)
        if width_extent > 0:
            scale = min(scale, TWO_HAND_CLOSEUP_TARGET_FRACTION * half_width / width_extent)
    if not np.isfinite(scale):
        raise ValueError("both hands have zero extent -- cannot derive a zoom factor")

    confidence[:, :, :] = 0.0
    for hand, (start, count, active_frames, rotated_rel) in hands.items():
        # Center the hand's OWN x/y extent on its half-frame centre (not its
        # wrist -- unlike the single-hand close-up, which fixes the wrist at
        # frame centre): a handshape whose fingers reach mostly to one side of
        # the wrist would otherwise sit lopsided in its half and spill across
        # the centre seam into the other hand. Centering the extent keeps each
        # hand tidily inside its own half (width <= 0.8 x half, so it fits with
        # margin).
        half_center_x = FRAME_WIDTH * _TWO_HAND_ANCHOR_X_FRACTION[hand]
        rel_x = np.concatenate([rotated_rel[f][:, 0] for f in active_frames])
        rel_y = np.concatenate([rotated_rel[f][:, 1] for f in active_frames])
        anchor_x = half_center_x - scale * float(rel_x.min() + rel_x.max()) / 2.0
        anchor_y = FRAME_HEIGHT / 2.0 - scale * float(rel_y.min() + rel_y.max()) / 2.0
        for f in active_frames:
            transformed = rotated_rel[f] * scale
            transformed[:, 0] += anchor_x
            transformed[:, 1] += anchor_y
            data[f, 0, start : start + count, :] = transformed
            confidence[f, 0, start : start + count] = pose.body.confidence[f, 0, start : start + count]

    closeup_body = NumPyPoseBody(fps=pose.body.fps, data=data, confidence=confidence)
    return Pose(header=pose.header, body=closeup_body)


def render_two_hand_closeup(pose: Pose, path: Path, view_angle_deg: float = HAND_CLOSEUP_VIEW_ANGLE_DEG) -> Path:
    """Writes a side-by-side close-up video/GIF of BOTH hands cropped out of
    ``pose`` -- see ``two_hand_closeup_pose`` for the transform. Same
    video/GIF-fallback wrapping as ``render_hand_closeup``."""
    closeup_pose = two_hand_closeup_pose(pose, view_angle_deg)
    visualizer = PoseVisualizer(closeup_pose, thickness=HAND_CLOSEUP_THICKNESS)
    try:
        visualizer.save_video(str(path), visualizer.draw())
        return path
    except Exception as e:  # noqa: BLE001 -- same deliberately-broad fallback as render_pose_video.py
        gif_path = path.with_suffix(".gif")
        print(
            f"WARNING: save_video() failed ({type(e).__name__}: {e}) -- "
            f"this environment is missing 'vidgear' and/or a real ffmpeg "
            f"binary. Falling back to save_gif() at {gif_path} instead."
        )
        visualizer.save_gif(str(gif_path), visualizer.draw())
        return gif_path


def fsw_to_two_hand_closeup_video(fsw: str, path: Path, view_angle_deg: float = HAND_CLOSEUP_VIEW_ANGLE_DEG) -> Path:
    """End-to-end: a real FSW sign straight to a side-by-side two-hand
    close-up video (or GIF fallback). Returns the path actually written."""
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)
    return render_two_hand_closeup(pose, path, view_angle_deg)


def fsw_to_hand_closeup_video(
    fsw: str,
    path: Path,
    hand: TrackName = TrackName.RIGHT_HAND,
    view_angle_deg: float = 0.0,
) -> Path:
    """End-to-end: a real FSW sign string straight to a hand-close-up
    video (or GIF fallback) file. ``hand`` defaults to RIGHT_HAND, matching
    MVP-1's own single-hand scope (``timeline/sample.py``) and
    ``render_pose_video.fsw_to_video``'s implicit convention.
    ``view_angle_deg`` defaults to 0.0 (the original straight-on view,
    unchanged -- same backward-compatibility reason as
    ``hand_closeup_pose``); pass ``HAND_CLOSEUP_VIEW_ANGLE_DEG`` for the
    3/4 view that reveals joint flexion moving mostly in Z, invisible
    head-on. Returns the path actually written."""
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)
    return render_hand_closeup(pose, path, hand, view_angle_deg)
