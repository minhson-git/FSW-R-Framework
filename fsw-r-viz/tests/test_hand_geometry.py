from __future__ import annotations

import numpy as np

from fsw_r.core.hand_symbol import HandSymbol

from fsw_r_viz.hand_geometry import hand_local_points, mirror_for_left_hand


def test_mirror_for_left_hand_flips_only_x() -> None:
    symbol = HandSymbol(base_hex=0x100, fill=1, rotation=0)
    original = hand_local_points(symbol.get_joint_pose())
    mirrored = mirror_for_left_hand(original)

    for finger in original:
        for original_point, mirrored_point in zip(original[finger], mirrored[finger]):
            assert mirrored_point[0] == -original_point[0]
            assert mirrored_point[1] == original_point[1]
            assert mirrored_point[2] == original_point[2]


def test_mirror_for_left_hand_is_its_own_inverse() -> None:
    symbol = HandSymbol(base_hex=0x100, fill=1, rotation=0)
    original = hand_local_points(symbol.get_joint_pose())
    twice_mirrored = mirror_for_left_hand(mirror_for_left_hand(original))

    for finger in original:
        for original_point, twice_point in zip(original[finger], twice_mirrored[finger]):
            assert np.allclose(original_point, twice_point)


def test_right_hand_thumb_is_on_the_viewers_left() -> None:
    """Regression test: a real right hand held up palm-out, fingers up
    (e.g. an oath-taking photo) shows the thumb on the VIEWER'S LEFT and
    the pinky on the viewer's right -- the earlier version of this rig had
    this backwards (thumb authored at +x, which rendered unmirrored/RIGHT
    put the thumb on the viewer's right instead). x here is the local
    spread axis, before any wrist rotation is applied, so this checks the
    base authoring directly, not a specific fill/rotation's rendering."""
    symbol = HandSymbol(base_hex=0x100, fill=1, rotation=0)
    points = hand_local_points(symbol.get_joint_pose())

    thumb_base_x = points["thumb"][1][0]  # index 0 is the wrist (x=0)
    pinky_base_x = points["pinky"][1][0]
    assert thumb_base_x < 0
    assert pinky_base_x > 0
    assert thumb_base_x < pinky_base_x
