from __future__ import annotations

import numpy as np
import pytest

from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.types import MotionPath, MovementPlane, PathType


def _path(
    path_type: PathType,
    plane: MovementPlane | None,
    curvature: float = 0.0,
    amplitude: float = 10.0,
    repeat: int = 1,
) -> MotionPath:
    return MotionPath(
        path_type=path_type,
        plane=plane,
        curvature=curvature,
        amplitude=amplitude,
        repeat=repeat,
        is_hit=False,
    )


def test_straight_in_wall_plane_stays_in_xy() -> None:
    """D2 requirement: STRAIGHT in WALL lies in the XY plane (Z ~ 0)."""
    path = _path(PathType.STRAIGHT, MovementPlane.WALL)
    points = sample_trajectory(path, rotation=0)
    assert points[:, 2] == pytest.approx(0.0, abs=1e-9)


def test_straight_in_floor_plane_stays_in_xz() -> None:
    """D2 requirement: STRAIGHT in FLOOR lies in the XZ plane (Y ~ 0)."""
    path = _path(PathType.STRAIGHT, MovementPlane.FLOOR)
    points = sample_trajectory(path, rotation=0)
    assert points[:, 1] == pytest.approx(0.0, abs=1e-9)


def test_contact_is_a_single_repeated_point() -> None:
    path = _path(PathType.CONTACT, None)
    points = sample_trajectory(path, rotation=0, samples=8)
    assert len(points) == 8
    assert np.allclose(points, points[0])


def test_repeat_multiplies_sample_count() -> None:
    path = _path(PathType.STRAIGHT, MovementPlane.WALL, repeat=3)
    points = sample_trajectory(path, rotation=0, samples=10)
    assert len(points) == 30


def test_curvature_zero_gives_a_straight_line() -> None:
    path = _path(PathType.CURVED, MovementPlane.WALL, curvature=0.0)
    points = sample_trajectory(path, rotation=0)
    assert points[:, 0] == pytest.approx(0.0, abs=1e-9)


def test_curvature_nonzero_bows_the_path() -> None:
    path = _path(PathType.CURVED, MovementPlane.WALL, curvature=0.5)
    points = sample_trajectory(path, rotation=0)
    assert np.abs(points[:, 0]).max() > 0.1


def test_rotation_changes_the_compass_direction() -> None:
    path = _path(PathType.STRAIGHT, MovementPlane.WALL)
    at_rest = sample_trajectory(path, rotation=0)
    rotated = sample_trajectory(path, rotation=2)
    assert not np.allclose(at_rest, rotated)


def test_amplitude_scales_the_trajectory_extent() -> None:
    small = sample_trajectory(_path(PathType.STRAIGHT, MovementPlane.WALL, amplitude=5.0), rotation=0)
    large = sample_trajectory(_path(PathType.STRAIGHT, MovementPlane.WALL, amplitude=20.0), rotation=0)
    assert np.abs(large).max() > np.abs(small).max()
