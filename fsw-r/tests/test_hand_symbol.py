"""HandSymbol replaces 261 hardcoded classes with one class that looks
itself up in pose_table.py. Most of what the old test_group_0N.py files
checked per symbol (joint pose invariant across rotation, wrist identity at
fill=0, wrist differs by rotation...) is *symbol-independent* behavior --
the formulas only ever look at fill/rotation, never at which symbol it is
-- so it's tested once, generically, in test_wrist_orientation.py, rather
than 261 times here (that would just be re-asserting the same formula
against itself). What genuinely differs per symbol, and so is worth
checking for all 261, is covered below: see PROGRESS.md's "Refactor tang
Group sang data-driven" entry for the full rationale (this file replaced
~1560 largely-tautological parametrized cases with the ~520 here).
"""

from __future__ import annotations

import pytest

from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.iswa_data import HAND_GROUP_START, valid_combinations_for
from fsw_r.core.pose_table import HAND_NAME_TABLE, HAND_POSE_TABLE
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.types import HandJointPose

GROUP_SIZES = [14, 16, 38, 8, 58, 30, 22, 19, 40, 16]

ALL_SYMBOLS = [
    (group, base_symbol_number)
    for group, size in enumerate(GROUP_SIZES, start=1)
    for base_symbol_number in range(1, size + 1)
]


def _base_hex(group: int, base_symbol_number: int) -> int:
    return HAND_GROUP_START[group - 1] + (base_symbol_number - 1)


@pytest.mark.parametrize("group,base_symbol_number", ALL_SYMBOLS)
def test_symbol_constructs_with_correct_id_and_name(group: int, base_symbol_number: int) -> None:
    base_hex = _base_hex(group, base_symbol_number)
    fill = min(valid_combinations_for(base_hex).fills)
    symbol = HandSymbol(base_hex=base_hex, fill=fill, rotation=0)

    symbol_id = f"01-{group:02d}-{base_symbol_number:03d}"
    assert symbol.symbol_id == symbol_id
    assert symbol.name == HAND_NAME_TABLE[base_hex]
    assert isinstance(symbol.get_joint_pose(), HandJointPose)


@pytest.mark.parametrize("group,base_symbol_number", ALL_SYMBOLS)
def test_symbol_from_fsw_builds_the_right_symbol(group: int, base_symbol_number: int) -> None:
    """Exercises the real FSW-key -> HandSymbol path (regex parsing +
    base-hex arithmetic + registry lookup) for every group boundary --
    unlike the pose/name lookups above, this is genuinely per-symbol
    behavior: an off-by-one in any group's boundary would only show up for
    that group's own symbols."""
    base_hex = _base_hex(group, base_symbol_number)
    fill = min(valid_combinations_for(base_hex).fills)
    rotation = 2
    symbol = symbol_from_fsw(f"S{base_hex:03x}{fill:x}{rotation:x}")
    assert isinstance(symbol, HandSymbol)
    assert symbol.fill == fill
    assert symbol.rotation == rotation
    assert symbol.symbol_id == f"01-{group:02d}-{base_symbol_number:03d}"


def test_joint_pose_is_independent_of_fill_and_rotation() -> None:
    """The one genuinely-shared invariant worth locking down explicitly
    (not 261 times -- HandSymbol's get_joint_pose() ignores fill/rotation
    by construction, so any single example proves it for all of them)."""
    variants = [
        HandSymbol(base_hex=0x100, fill=fill, rotation=rotation)
        for fill in range(6)
        for rotation in (0, 2, 9)
    ]
    poses = [symbol.get_joint_pose() for symbol in variants]
    assert all(pose == HAND_POSE_TABLE[0x100] for pose in poses)
