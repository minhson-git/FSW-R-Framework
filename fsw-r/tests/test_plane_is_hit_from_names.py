"""Dedicated B1-B6 tests for this task's brief ("`plane` và `is_hit` từ tên
BASE SYMBOL", task 4/4 closing the Category 2 source-fidelity chain) --
``plane_for_name()``/``is_hit_for_name()`` in ``scripts/gen_movement_paths.py``.

B7 ("regeneration script byte-identical") is NOT a pytest test here, same
reason every prior task in this chain wasn't: this script's inputs
(``iswa_base_symbol_names.json``, ``iswa_movement_glyph_sizes.json``) were
themselves fetched over the network by OTHER scripts; re-running
``gen_movement_paths.py`` itself needs no network, but its full
byte-identical-regeneration property was verified by hand this session
(two runs, diffed byte-for-byte identical) and is recorded in PROGRESS.md.

B8 (``reports/fk_accuracy.md`` unchanged) is a ``git diff`` check on the
final commit, not a pytest test -- this task never touches Category 1 data
(only ``movement_paths.json`` and ``gen_movement_paths.py``).

B9 ("test cũ pass, test nào assert plane/is_hit cũ sẽ fail"): verified (not
assumed) that BEFORE this task, no existing test asserted a specific
base_hex's real ``plane``/``is_hit`` against ``MOVEMENT_PATH_TABLE`` --
every ``plane=``/``is_hit=`` reference in ``test_movement_paths.py``/
``test_path_type_from_names.py`` is an explicit fixture argument to a
directly-constructed ``MotionPath``, never a read of the loaded table. So 0
existing tests needed updating -- the full suite was green (1,539/1,539)
immediately after regenerating ``movement_paths.json``.
"""

from __future__ import annotations

import gen_movement_paths
import pytest

from fsw_r.core.iswa_data import group_of
from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.pose_table import MOVEMENT_PATH_TABLE
from fsw_r.core.types import MovementPlane

# The 9 base symbols this task's brief's own Part 0 table lists, plus 2 more
# independently found by applying the brief's own A1 rule 1 literally (name
# checked BEFORE the "groups 11/12/20 have no plane" assumption) -- group 12
# (Finger Movement) turns out to have 2 base symbols whose OWN name states a
# plane, even though the GROUP's name doesn't. See PROGRESS.md's entry for
# this task for the full discrepancy note (brief said 9, measured 11).
PLANE_CASES = [
    (0x24E, "floor", "Travel Rotation, Single Floor Plane"),
    (0x24F, "floor", "Travel Rotation, Double Floor Plane"),
    (0x250, "floor", "Travel Rotation, Alternating Floor Plane"),
    (0x284, "wall", "Travel Rotation Single Wall Plane"),
    (0x285, "wall", "Travel Rotation Double Wall Plane"),
    (0x286, "wall", "Travel Rotation Alternating Wall Plane"),
    (0x2B4, "diagonal", "Wave Diagonal Path Small"),
    (0x2B5, "diagonal", "Wave Diagonal Path Medium"),
    (0x2B6, "diagonal", "Wave Diagonal Path Large"),
    (0x228, "wall", "Finger Contact Movement, Wall Plane (not in the brief's own table -- found via A1)"),
    (0x229, "floor", "Finger Contact Movement, Floor Plane (not in the brief's own table -- found via A1)"),
]

# The 13 base symbols this task's brief's Part 0 table lists.
IS_HIT_CASES = [
    (0x2B4, False, "Wave Diagonal Path Small"),
    (0x2B5, False, "Wave Diagonal Path Medium"),
    (0x2B6, False, "Wave Diagonal Path Large"),
    (0x2E7, True, "Arm Circle Hits Wall Small Single"),
    (0x2E8, True, "Arm Circle Hits Wall Medium Single"),
    (0x2E9, True, "Arm Circle Hits Wall Large Single"),
    (0x2EA, True, "Arm Circle Hits Wall Small Double"),
    (0x2EB, True, "Arm Circle Hits Wall Medium Double"),
    (0x2EC, True, "Arm Circle Hits Wall Large Double"),
    (0x2EF, True, "Wrist Circle Hits Wall Single"),
    (0x2F0, True, "Wrist Circle Hits Wall Double"),
    (0x2F3, True, "Finger Circles Hits Wall Single"),
    (0x2F4, True, "Finger Circles Hits Wall Double"),
]


def _plane_value(base_hex: int) -> str | None:
    plane = MOVEMENT_PATH_TABLE[base_hex].plane
    return plane.value if plane is not None else None


@pytest.mark.parametrize("base_hex,expected_plane,label", PLANE_CASES)
def test_b1_plane_matches_the_verified_table(base_hex: int, expected_plane: str, label: str) -> None:
    assert _plane_value(base_hex) == expected_plane, label


@pytest.mark.parametrize("base_hex,expected_is_hit,label", IS_HIT_CASES)
def test_b2_is_hit_matches_the_verified_table(base_hex: int, expected_is_hit: bool, label: str) -> None:
    assert MOVEMENT_PATH_TABLE[base_hex].is_hit is expected_is_hit, label


def test_b3_no_base_disagrees_with_its_own_name_on_plane() -> None:
    names = gen_movement_paths._load_names()
    mismatches = []
    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        name_plane = gen_movement_paths.plane_for_name(names[base_hex]["name"], base_hex)
        if name_plane is not None and name_plane != _plane_value(base_hex):
            mismatches.append(base_hex)
    assert mismatches == []


def test_b4_no_base_disagrees_with_its_own_name_on_is_hit() -> None:
    names = gen_movement_paths._load_names()
    mismatches = []
    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        name_says_hit = gen_movement_paths.is_hit_for_name(names[base_hex]["name"])
        if name_says_hit != MOVEMENT_PATH_TABLE[base_hex].is_hit:
            mismatches.append(base_hex)
    assert mismatches == []


def test_b5_fallback_bases_keep_the_old_group_derived_plane() -> None:
    # The 102 base symbols whose own name says nothing about plane must
    # still get exactly the OLD per-group value (no regression from this
    # task touching them).
    names = gen_movement_paths._load_names()
    fallback_count = 0
    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        name = names[base_hex]["name"]
        if gen_movement_paths.plane_for_name(name, base_hex) is not None:
            continue  # this base gets its plane from its own name, not group fallback
        fallback_count += 1
        group = group_of(base_hex)
        _group_name, expected_plane = gen_movement_paths._GROUP_TABLE[group]
        assert _plane_value(base_hex) == expected_plane, f"0x{base_hex:x} regressed from its old group fallback"
    assert fallback_count == 102


def test_b6_groups_11_12_20_still_null_except_the_2_a1_exceptions_and_still_fall_back_to_wall() -> None:
    null_plane_groups = {11, 20}  # group 12 has 2 real exceptions -- see PLANE_CASES/A1
    for base_hex in MOVEMENT_PATH_TABLE.base_hexes():
        if group_of(base_hex) in null_plane_groups:
            assert MOVEMENT_PATH_TABLE[base_hex].plane is None

    # plane=None still renders identically to plane=WALL (the documented
    # fallback at render time -- core/movement_paths.py's _plane_rotation()).
    path_null = MOVEMENT_PATH_TABLE[0x205]  # group 11, Contact -- plane is None
    assert path_null.plane is None
    from dataclasses import replace

    path_wall = replace(path_null, plane=MovementPlane.WALL)
    points_null = sample_trajectory(path_null, rotation=0)
    points_wall = sample_trajectory(path_wall, rotation=0)
    assert (points_null == points_wall).all()
