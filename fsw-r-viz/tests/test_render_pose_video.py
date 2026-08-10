from __future__ import annotations

from pathlib import Path

import pytest

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.export.pose_export import frames_to_pose
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from fsw_r_viz.render_pose_video import fsw_to_video, render_pose_to_video

# A real MVP-1-scoped sign: Index (fill=0, rotation=0) + Straight Wall
# Plane movement -- same sign fsw-r's own test_pose_export.py uses for its
# end-to-end test, exercised here through fsw-r-viz's own video/GIF layer.
_MVP1_MOVING_SIGN = "M508x515S10000493x485S22a04500x500"


def test_e8_end_to_end_fsw_string_to_video_or_gif_file(tmp_path: Path) -> None:
    out_path = tmp_path / "sign.mp4"
    written = fsw_to_video(_MVP1_MOVING_SIGN, out_path)
    assert written.exists()
    assert written.stat().st_size > 0
    # This environment has neither vidgear nor a real ffmpeg binary, so the
    # documented fallback path is exercised here, not just assumed to work.
    assert written.suffix in (".mp4", ".gif")


def test_fallback_to_gif_does_not_raise_and_reports_clearly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    positioned = fsw_to_fswr(_MVP1_MOVING_SIGN)
    timeline = build_timeline(positioned)
    frames = sample(timeline)
    pose = frames_to_pose(frames)

    out_path = tmp_path / "sign.mp4"
    written = render_pose_to_video(pose, out_path)

    captured = capsys.readouterr()
    if written.suffix == ".gif":
        # Fell back -- must have printed a clear, non-silent explanation.
        assert "WARNING" in captured.out
        assert "save_gif" in captured.out
