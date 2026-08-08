from __future__ import annotations

import pytest

from fsw_r.core.face_types import ARKIT_BLENDSHAPES, FaceExpressionPose


def test_arkit_set_has_52_names() -> None:
    assert len(ARKIT_BLENDSHAPES) == 52


def test_empty_pose_is_neutral() -> None:
    pose = FaceExpressionPose()
    assert dict(pose.blendshapes) == {}


def test_valid_pose_round_trips() -> None:
    pose = FaceExpressionPose(blendshapes={"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8})
    assert pose.blendshapes["mouthSmileLeft"] == pytest.approx(0.8)


def test_unknown_blendshape_name_rejected() -> None:
    with pytest.raises(ValueError):
        FaceExpressionPose(blendshapes={"mouthGrinLeft": 0.5})  # not an ARKit name


@pytest.mark.parametrize("weight", [-0.1, 1.1, 2.0])
def test_out_of_range_weight_rejected(weight: float) -> None:
    with pytest.raises(ValueError):
        FaceExpressionPose(blendshapes={"jawOpen": weight})


def test_pose_is_immutable() -> None:
    pose = FaceExpressionPose(blendshapes={"jawOpen": 0.4})
    with pytest.raises(TypeError):
        pose.blendshapes["jawOpen"] = 0.9  # type: ignore[index]
