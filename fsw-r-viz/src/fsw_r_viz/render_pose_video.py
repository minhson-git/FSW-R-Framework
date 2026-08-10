"""Turns a ``fsw_r.export.pose_export`` ``Pose`` into an actual video file,
using ``pose_format``'s own ``PoseVisualizer`` -- see this project's export-
layer task brief, Part 0: no renderer (mesh/skinning/camera) is written
here, only the standard library tool for the standard format.

``.pose`` (data) lives in ``fsw-r`` (``export/pose_export.py``);
video/GIF encoding (needs OpenCV/ffmpeg-adjacent tooling) lives here in
``fsw-r-viz``, same layering reasoning as ``plot_hand.py``/``render_timeline.py``.

``save_video()`` needs the optional ``vidgear`` package (and, at runtime, a
real ffmpeg binary on the system) -- neither is guaranteed to be present.
If it's not, this falls back to ``save_gif()`` (Pillow-only, no ffmpeg)
and prints a clear message explaining why, rather than failing silently or
producing an empty/corrupt file.
"""

from __future__ import annotations

from pathlib import Path

from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.export.pose_export import frames_to_pose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample


def render_pose_to_video(pose: Pose, path: Path) -> Path:
    """Writes ``path`` as an MP4 if ``vidgear``+ffmpeg are available;
    otherwise falls back to a GIF at ``path`` with its suffix replaced by
    ``.gif``, printing why. Returns the path actually written (may differ
    from ``path`` on fallback)."""
    visualizer = PoseVisualizer(pose)
    try:
        visualizer.save_video(str(path), visualizer.draw())
        return path
    except Exception as e:  # noqa: BLE001 -- deliberately broad, see module docstring
        gif_path = path.with_suffix(".gif")
        print(
            f"WARNING: save_video() failed ({type(e).__name__}: {e}) -- "
            f"this environment is missing 'vidgear' and/or a real ffmpeg "
            f"binary. Falling back to save_gif() at {gif_path} instead."
        )
        visualizer.save_gif(str(gif_path), visualizer.draw())
        return gif_path


def fsw_to_video(fsw: str, path: Path) -> Path:
    """End-to-end: a real FSW sign string straight to a video (or GIF
    fallback) file. Returns the path actually written."""
    positioned = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)
    return render_pose_to_video(pose, path)
