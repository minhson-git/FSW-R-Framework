from __future__ import annotations

from unittest.mock import Mock

import pytest

from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.renderer import HandMeshRenderer3D
from fsw_r.core.types import HandSide


def _index(fill: int, rotation: int) -> HandSymbol:
    return HandSymbol(base_hex=0x100, fill=fill, rotation=rotation)


@pytest.mark.parametrize("rotation", range(0, 8))
def test_hand_side_right_for_rotation_0_to_7(rotation: int) -> None:
    symbol = _index(fill=1, rotation=rotation)
    assert symbol.hand_side == HandSide.RIGHT


@pytest.mark.parametrize("rotation", range(8, 16))
def test_hand_side_left_for_rotation_8_to_15(rotation: int) -> None:
    symbol = _index(fill=1, rotation=rotation)
    assert symbol.hand_side == HandSide.LEFT


@pytest.mark.parametrize("invalid_fill", [-1, 6, 100])
def test_constructor_rejects_out_of_range_fill(invalid_fill: int) -> None:
    with pytest.raises(ValueError):
        _index(fill=invalid_fill, rotation=0)


@pytest.mark.parametrize("invalid_rotation", [-1, 16, 100])
def test_constructor_rejects_out_of_range_rotation(invalid_rotation: int) -> None:
    with pytest.raises(ValueError):
        _index(fill=1, rotation=invalid_rotation)


def test_renderer_selects_rig_matching_hand_side() -> None:
    right_symbol = _index(fill=1, rotation=1)
    left_symbol = _index(fill=1, rotation=9)

    right_rig = Mock()
    left_rig = Mock()
    rig_provider = Mock()
    rig_provider.get_rig.side_effect = lambda hand_side: (
        right_rig if hand_side == HandSide.RIGHT else left_rig
    )
    renderer = HandMeshRenderer3D(rig_provider)

    renderer.render(right_symbol)
    rig_provider.get_rig.assert_called_once_with(HandSide.RIGHT)
    right_rig.apply_wrist_orientation.assert_called_once()
    right_rig.apply_joint_pose.assert_called_once_with(right_symbol.get_joint_pose())
    left_rig.apply_wrist_orientation.assert_not_called()

    renderer.render(left_symbol)
    rig_provider.get_rig.assert_called_with(HandSide.LEFT)
    left_rig.apply_wrist_orientation.assert_called_once()
    called_rotation = left_rig.apply_wrist_orientation.call_args.args[0]
    assert called_rotation.as_quat() == pytest.approx(left_symbol.get_wrist_orientation().as_quat())
    left_rig.apply_joint_pose.assert_called_once_with(left_symbol.get_joint_pose())


def test_renderer_raises_a_clear_error_for_a_symbol_with_no_hand_side() -> None:
    """hand_side is abstract and per-category now (FSWBaseSymbol.hand_side)
    -- no implemented category actually returns None today, but the
    renderer must fail with a clear message rather than pass None through
    to rig_provider.get_rig() if/when one does."""
    symbol = Mock()
    symbol.hand_side = None
    symbol.symbol_id = "02-11-001"
    symbol.category = 2

    renderer = HandMeshRenderer3D(Mock())
    with pytest.raises(ValueError):
        renderer.render(symbol)
