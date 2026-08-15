"""Dedicated C1-C6 tests for this task's brief ("`path_type` từ tên BASE
SYMBOL") -- ``data/iswa_base_symbol_names.json``
(``scripts/fetch_base_symbol_names.py``) and the name->``PathType`` mapping
it feeds (``scripts/gen_movement_paths.py``'s ``_PATH_TYPE_RULES``).

C7 ("regeneration script byte-identical on rerun") and part of C8 are NOT
pytest tests here, for the same reason Task 1's D6 wasn't: both
``fetch_base_symbol_names.py`` and ``gen_movement_paths.py`` (transitively,
via the names file it reads) need live HTTP access to signbank.org, which
would make the whole suite non-offline-runnable. C7 was verified by hand
this session (two runs, diffed byte-for-byte identical) and is recorded in
PROGRESS.md.

C8 ("test nào assert path_type == 'straight' cho base bị đổi sẽ fail"):
verified (not assumed) that BEFORE this task, no existing test asserted any
specific base_hex's ``path_type`` against the real ``MOVEMENT_PATH_TABLE``
data -- ``test_movement_paths.py`` only constructs ``MotionPath`` objects
directly (a fixture helper, not the loaded table), and
``test_movement_path_table.py`` only checks structural properties (count,
range, parses-to-``MotionPath``), never a specific ``path_type`` value. So
0 existing tests needed updating -- the full suite was green (1,496/1,496)
immediately after regenerating ``movement_paths.json``, with no test
changes required. Recorded here so that fact is verifiable, not just
asserted in PROGRESS.md.

C9 (before/after GIF) lives in ``fsw-r-viz``, not here -- see PROGRESS.md's
entry for this task for where the GIF was exported and what it shows.
"""

from __future__ import annotations

import numpy as np
import pytest

import gen_movement_paths
from fsw_r.core.iswa_data import GROUP_START, symbol_id_of
from fsw_r.core.movement_paths import sample_trajectory
from fsw_r.core.pose_table import MOVEMENT_PATH_TABLE
from fsw_r.core.types import MotionPath, MovementPlane, PathType

EXPECTED_TOTAL = 242
_MOVEMENT_START = GROUP_START[10]
_MOVEMENT_END = GROUP_START[20] - 1
# Group 02-03 ("Straight Wall Plane") = global group 13.
_GROUP_02_03_START = GROUP_START[12]
_GROUP_02_03_END = GROUP_START[13] - 1


def test_c1_names_table_has_242_entries_all_in_range() -> None:
    names = gen_movement_paths._load_names()
    assert len(names) == EXPECTED_TOTAL
    assert set(names.keys()) == set(range(_MOVEMENT_START, _MOVEMENT_END + 1))


def test_c2_names_symbol_id_column_matches_symbol_id_of() -> None:
    # Cross-check against Task 1's symbol_id_of() -- two independent
    # sources (signbank's own "Symbol ID" column vs this project's
    # symidArr-derived function) for the same 4-part id must agree.
    names = gen_movement_paths._load_names()
    for base_hex, entry in names.items():
        assert entry["symbol_id"] == symbol_id_of(base_hex), f"0x{base_hex:x}: {entry['symbol_id']!r}"


def test_c3_single_straight_movement_maps_to_straight() -> None:
    names = gen_movement_paths._load_names()
    assert "Single Straight" in names[0x22A]["name"]
    assert MOVEMENT_PATH_TABLE[0x22A].path_type == PathType.STRAIGHT


def test_c4_group_02_03_has_at_least_one_non_straight_base() -> None:
    # If every base in this group still maps to STRAIGHT, the name->PathType
    # mapping isn't doing anything -- this is exactly the bug being fixed
    # (see PROGRESS.md's Part 0 table: 0x245 "Zigzag" is one such base).
    path_types = {MOVEMENT_PATH_TABLE[b].path_type for b in range(_GROUP_02_03_START, _GROUP_02_03_END + 1)}
    assert path_types != {PathType.STRAIGHT}
    assert PathType.ZIGZAG in path_types


def test_c5_every_real_name_matches_a_rule_no_silent_default() -> None:
    # Re-affirms, as a pytest-visible regression guard (not just the
    # generation script's own exit-on-failure), that path_type_for_name()
    # never silently falls back -- every one of the 242 real names must
    # match some rule in _PATH_TYPE_RULES.
    names = gen_movement_paths._load_names()
    for base_hex, entry in names.items():
        path_type = gen_movement_paths.path_type_for_name(entry["name"], base_hex)
        assert isinstance(path_type, PathType)


def test_c5_unmatched_name_raises() -> None:
    with pytest.raises(ValueError):
        gen_movement_paths.path_type_for_name("Not A Real ISWA Name At All", 0x999)


_ALL_PATH_TYPES: list[PathType] = list(PathType)


@pytest.mark.parametrize("path_type", _ALL_PATH_TYPES)
def test_c6_every_path_type_trajectory_differs_measurably_from_straight(path_type: PathType) -> None:
    straight = MotionPath(
        path_type=PathType.STRAIGHT, plane=MovementPlane.WALL, curvature=0.0, amplitude=10.0, repeat=1, is_hit=False
    )
    straight_points = sample_trajectory(straight, rotation=0)

    candidate = MotionPath(
        path_type=path_type, plane=MovementPlane.WALL, curvature=0.3, amplitude=10.0, repeat=1, is_hit=False
    )
    candidate_points = sample_trajectory(candidate, rotation=0)

    distance = float(np.linalg.norm(candidate_points - straight_points))
    if path_type == PathType.STRAIGHT:
        assert distance == 0.0
    else:
        assert distance > 0.1, f"{path_type.value}: only {distance:.4f} from STRAIGHT -- not measurably different"


def test_movement_path_table_still_has_242_entries_after_regeneration() -> None:
    # D5-equivalent regression guard for this task: the count/range
    # invariant test_movement_path_table.py already checks must still hold
    # after path_type is now name-derived instead of group-derived.
    assert len(MOVEMENT_PATH_TABLE.base_hexes()) == EXPECTED_TOTAL
