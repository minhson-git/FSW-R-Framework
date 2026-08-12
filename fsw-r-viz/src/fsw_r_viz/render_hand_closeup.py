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


def hand_closeup_pose(pose: Pose, hand: TrackName) -> Pose:
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
    the full-body video already shows that path) and magnified by a
    single scale factor derived from ``HAND_CLOSEUP_TARGET_FRACTION`` and
    the hand's OWN measured bounding box (not the trajectory's -- see
    module docstring's "Zoom strategy").

    The vertical anchor point is NOT fixed at frame center: it is
    computed so the hand's own vertical extent (relative to the wrist,
    measured across every frame the hand is active in, not just frame 0)
    is centered in the output frame -- for a handshape where the fingers
    curl/point mostly one way from the wrist (the common case), this
    naturally places the wrist BELOW center, leaving the fingers room to
    extend into the frame without being clipped, exactly what this task's
    brief's Part B1 asks for ("neo WRIST về tâm khung, hoặc điểm thấp hơn
    tâm") -- computed from the real content instead of a second guessed
    constant. The horizontal anchor IS fixed at frame center (this task's
    C3): the standard demo sign's hand happens to be roughly symmetric
    left-right around the wrist, so this does not need the same
    data-driven treatment to stay on-frame.

    Raises ``ValueError`` if ``hand`` is never active (confidence 0 in
    every frame) -- there is nothing to zoom into, and silently emitting
    an empty video would hide that rather than reporting it.
    """
    component_name = _HAND_COMPONENT_BY_TRACK[hand]
    start, count = _hand_component_range(pose, component_name)
    wrist_local_index = pose.header.get_point_index(component_name, "WRIST") - start

    data: NDArray[np.float64] = np.array(pose.body.data, dtype=np.float64, copy=True)
    confidence: NDArray[np.float64] = np.array(pose.body.confidence, dtype=np.float64, copy=True)
    frame_count = data.shape[0]

    active_frames = [f for f in range(frame_count) if confidence[f, 0, start:start + count].sum() > 0]
    if not active_frames:
        raise ValueError(f"{hand} is never active (confidence 0 in every frame) -- nothing to render a close-up of")

    # MEASURE the hand's own VERTICAL extent relative to its own wrist,
    # across EVERY active frame (not just frame 0 -- this project's own
    # "measure, don't assume" rule, see PROGRESS.md), so a hypothetical
    # frame-varying handshape would still be sized/centered to fit every
    # frame, not just the first. Height only, not width: this task's own
    # C1 targets frame HEIGHT, and the standard demo sign's hand is
    # noticeably taller than wide (114.8 x 59px) -- height is the binding
    # dimension for this sign, and the horizontal anchor is fixed at frame
    # center regardless (see this function's own docstring).
    all_rel_y = []
    for frame_index in active_frames:
        points = data[frame_index, 0, start:start + count, :2]
        wrist = points[wrist_local_index]
        rel_y_this_frame = points[:, 1] - wrist[1]
        all_rel_y.append(rel_y_this_frame)
    rel_y = np.concatenate(all_rel_y)

    height_extent = float(rel_y.max() - rel_y.min())
    if height_extent <= 0:
        raise ValueError(f"{hand}'s bounding box has zero height -- cannot derive a zoom factor")
    scale = (HAND_CLOSEUP_TARGET_FRACTION * FRAME_HEIGHT) / height_extent

    anchor_x = FRAME_WIDTH / 2.0
    anchor_y = FRAME_HEIGHT / 2.0 - scale * float(rel_y.min() + rel_y.max()) / 2.0

    # Zero out every point outside the target hand's own slice -- "close-
    # up of ONE hand", not "full body, coincidentally zoomed."
    confidence[:, :, :] = 0.0

    for frame_index in active_frames:
        points = data[frame_index, 0, start:start + count, :]
        wrist = points[wrist_local_index]
        rel = points - wrist
        transformed = rel * scale
        transformed[:, 0] += anchor_x
        transformed[:, 1] += anchor_y
        # z is left anchor-free (relative-depth-only, see PoseVisualizer's
        # painter's-algorithm sort in pose_export.py's own docstring) --
        # only scaled, like x/y, to keep depth ordering consistent.
        data[frame_index, 0, start:start + count, :] = transformed
        confidence[frame_index, 0, start:start + count] = pose.body.confidence[frame_index, 0, start:start + count]

    closeup_body = NumPyPoseBody(fps=pose.body.fps, data=data, confidence=confidence)
    return Pose(header=pose.header, body=closeup_body)


def render_hand_closeup(pose: Pose, path: Path, hand: TrackName) -> Path:
    """Writes a close-up video/GIF of ONE hand (``hand`` -- RIGHT or LEFT)
    cropped out of ``pose`` -- see ``hand_closeup_pose`` above for the
    actual data transform this wraps with video/GIF encoding."""
    closeup_pose = hand_closeup_pose(pose, hand)
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


def fsw_to_hand_closeup_video(fsw: str, path: Path, hand: TrackName = TrackName.RIGHT_HAND) -> Path:
    """End-to-end: a real FSW sign string straight to a hand-close-up
    video (or GIF fallback) file. ``hand`` defaults to RIGHT_HAND, matching
    MVP-1's own single-hand scope (``timeline/sample.py``) and
    ``render_pose_video.fsw_to_video``'s implicit convention. Returns the
    path actually written."""
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)
    return render_hand_closeup(pose, path, hand)
