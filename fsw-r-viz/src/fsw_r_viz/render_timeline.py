"""Renders a ``fsw_r.timeline.SignTimeline`` as a numbered PNG sequence --
the first visual evidence that the framework produces MOTION, not just a
static pose. One PNG per sampled frame; stitch into a GIF/video externally
if needed (no GIF-writing dependency is added here, PNGs are enough
evidence on their own -- see the task brief).

Debugging aid, same spirit as ``plot_hand.py`` (which this reuses the hand
geometry from): not the final renderer.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: save to file instead of opening a window

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.axes3d import Axes3D

from fsw_r.core.types import HandSide
from fsw_r.timeline.sample import DEFAULT_FPS, sample
from fsw_r.timeline.types import PoseFrame, SignTimeline, TrackName

from fsw_r_viz.hand_geometry import apply_wrist_orientation, hand_local_points, mirror_for_left_hand

_FINGER_COLORS: dict[str, str] = {
    "thumb": "tab:orange",
    "index": "tab:red",
    "middle": "tab:blue",
    "ring": "tab:green",
    "pinky": "tab:purple",
}

_TRACK_HAND_SIDE: dict[TrackName, HandSide] = {
    TrackName.RIGHT_HAND: HandSide.RIGHT,
    TrackName.LEFT_HAND: HandSide.LEFT,
}

# Display-only scale, NOT a calibrated real-world value (see
# fsw_r.timeline.anchor's own SIGNBOX_TO_BODY_SCALE caveat): body-space
# position (roughly -1..+1) blown up so a moving track's displacement is
# visible next to a hand rig whose own bones span roughly -6..+16 units.
_POSITION_TO_HAND_SCALE = 10.0


def _plot_frame(ax: Axes3D, frame: PoseFrame, title: str) -> None:
    for track_name, pose in frame.tracks.items():
        if pose.joint_pose is None or pose.wrist is None:
            continue
        local_points = hand_local_points(pose.joint_pose)
        if _TRACK_HAND_SIDE.get(track_name) == HandSide.LEFT:
            local_points = mirror_for_left_hand(local_points)
        world_points = apply_wrist_orientation(local_points, pose.wrist)
        offset = pose.position * _POSITION_TO_HAND_SCALE if pose.position is not None else np.zeros(3)

        for finger, points in world_points.items():
            xs = [p[0] + offset[0] for p in points]
            depths = [p[2] + offset[2] for p in points]
            heights = [p[1] + offset[1] for p in points]
            ax.plot(xs, depths, heights, marker="o", color=_FINGER_COLORS[finger], label=finger)

    ax.set_title(title)
    ax.set_xlabel("x (spread)")
    ax.set_ylabel("z (depth)")
    ax.set_zlabel("y (up)")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_zlim(-5, 15)
    ax.view_init(elev=20, azim=-60)


def render_timeline_to_pngs(
    timeline: SignTimeline, output_dir: str, fps: int = DEFAULT_FPS, prefix: str = "frame"
) -> list[str]:
    """Samples ``timeline`` at ``fps`` and writes one numbered PNG per
    frame into ``output_dir``. Returns the written file paths, in order."""
    frames = sample(timeline, fps=fps)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for i, frame in enumerate(frames):
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection="3d")
        _plot_frame(ax, frame, f"{prefix} {i:03d} (t={frame.time_seconds:.2f}s)")
        ax.legend(
            handles=[
                Line2D([0], [0], color=color, marker="o", label=finger)
                for finger, color in _FINGER_COLORS.items()
            ],
            loc="upper left",
            fontsize="small",
        )
        fig.tight_layout()
        path = out_dir / f"{prefix}_{i:03d}.png"
        fig.savefig(str(path), dpi=150)
        plt.close(fig)
        paths.append(str(path))
    return paths
