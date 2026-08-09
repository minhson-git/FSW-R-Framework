from __future__ import annotations

from pathlib import Path

from fsw_r_viz.plot_mesh_head import render_mesh_head_to_file


def test_renders_expression_and_features(tmp_path: Path) -> None:
    items = [
        ({"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8}, "smile", None),
        ({"jawOpen": 0.6}, "teeth", "teeth"),
        ({}, "ears", "ears"),
    ]
    output_path = tmp_path / "heads.png"

    render_mesh_head_to_file(items, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
