from __future__ import annotations

import numpy as np

from fsw_r.core.hand_symbol import HandSymbol

from fsw_r_viz.hand_geometry import hand_local_points, mirror_for_left_hand


def test_mirror_for_left_hand_flips_only_x() -> None:
    symbol = HandSymbol(category=1, group=1, base_symbol_number=1, fill=1, rotation=0)
    original = hand_local_points(symbol.get_joint_pose())
    mirrored = mirror_for_left_hand(original)

    for finger in original:
        for original_point, mirrored_point in zip(original[finger], mirrored[finger]):
            assert mirrored_point[0] == -original_point[0]
            assert mirrored_point[1] == original_point[1]
            assert mirrored_point[2] == original_point[2]


def test_mirror_for_left_hand_is_its_own_inverse() -> None:
    symbol = HandSymbol(category=1, group=1, base_symbol_number=1, fill=1, rotation=0)
    original = hand_local_points(symbol.get_joint_pose())
    twice_mirrored = mirror_for_left_hand(mirror_for_left_hand(original))

    for finger in original:
        for original_point, twice_point in zip(original[finger], twice_mirrored[finger]):
            assert np.allclose(original_point, twice_point)
