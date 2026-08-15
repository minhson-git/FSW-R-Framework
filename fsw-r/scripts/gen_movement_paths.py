"""Generates ``src/fsw_r/data/movement_paths.json`` for all 242 Category 2
(Movement) base symbols.

**``path_type`` comes from each base symbol's own real ISWA NAME**
(``data/iswa_base_symbol_names.json``, ``scripts/fetch_base_symbol_names.py``
-- the "`path_type` từ tên BASE SYMBOL" task), via the ordered keyword table
``_PATH_TYPE_RULES`` below. ``plane``/``is_hit`` are still derived from the
10-row (group -> plane/is_hit) table this script used to derive
``path_type`` from too -- Part 0 of that task's brief found only
``path_type`` wrong (a group name states the *plane*, not the *shape*);
``plane``/``is_hit`` were not shown to be wrong, so they're untouched here.

Why this was broken before: group 02-03 ("Straight Wall Plane") alone has
43 base symbols named Single Straight, Bend, Corner, Check, Box, Zigzag,
Peaks, Travel Rotation, ... -- every one of them was getting
``path_type = "straight"`` because the OLD version of this script assigned
path_type per GROUP, not per base symbol. See PROGRESS.md's entry for this
task for the full corpus-impact table and the before/after path_type counts.

**Fail-loud contract (this task's brief, Part B2):** ``_path_type_for_name()``
raises (not silently falls back to STRAIGHT or anything else) if a base
symbol's real name doesn't match any rule in ``_PATH_TYPE_RULES`` --
verified empirically against all 242 real names before this table was
written (every one matches exactly one rule; see PROGRESS.md).

** UNVERIFIED ASSUMPTIONS ** -- also recorded in the generated JSON's own
``_meta`` and in PROGRESS.md's entry for this task, not silently treated as
fact:
- ``plane`` for groups 11 (Contact), 12 (Finger Movement), and 20
  (Circles) isn't stated by their group names the way groups 13-19's are
  -- left as ``None`` here; ``core/movement_paths.py`` decides what to do
  with that at render time (currently: fall back to WALL).
- ``is_hit`` is still a per-GROUP flag (True for groups 17/18 only), even
  though the real names show "Hits Wall/Floor/Ceiling/Chest" varies WITHIN
  some groups too (e.g. group 20's "Arm Circle Wall" vs "Arm Circle Hits
  Wall") -- discovered while fetching real names for this task, but fixing
  ``is_hit`` is out of THIS task's scope (only ``path_type`` was in the
  brief) -- flagged here for a future task, not fixed.
- ``curvature``/``amplitude``/``repeat`` are still constant per path_type
  across all symbols that share it -- the real names literally spell out
  Small/Medium/Large/Largest (amplitude, task 3's job) and
  Single/Double/Triple/Alternating (repeat -- not in scope for either this
  task or task 3, since the brief's Part 0 only diagnosed path_type and
  amplitude as wrong) that this script still does not use.
"""

from __future__ import annotations

import json
import sys
from importlib import resources
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of  # noqa: E402
from fsw_r.core.types import PathType  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "movement_paths.json"
NAMES_RESOURCE = "iswa_base_symbol_names.json"

EXPECTED_TOTAL = 242

# Global group number (11-20, from core/iswa_data.py's GROUP_START indices
# 10-19) -> (real name, plane, is_hit). Names from ISWA Manual Chapter 2;
# plane/is_hit are this project's own reading of what each GROUP name
# implies -- unaffected by this task (path_type no longer comes from here).
_GROUP_TABLE: dict[int, tuple[str, str | None, bool]] = {
    11: ("Contact", None, False),
    12: ("Finger Movement", None, False),
    13: ("Straight Wall Plane", "wall", False),
    14: ("Straight Diagonal Plane", "diagonal", False),
    15: ("Straight Floor Plane", "floor", False),
    16: ("Curves Wall Plane", "wall", False),
    17: ("Curves Hit Wall Plane", "wall", True),
    18: ("Curves Hit Floor Plane", "floor", True),
    19: ("Curves Floor Plane", "floor", False),
    20: ("Circles", None, False),
}

# Ordered (keyword, PathType) rules -- checked in order, first
# case-insensitive substring match wins. Order matters: more specific
# phrases (e.g. "travel rotation") MUST come before shorter ones they
# contain ("rotation") or this would misclassify them. Verified empirically
# against all 242 real names in data/iswa_base_symbol_names.json before
# being committed here -- 0 unmatched, 0 accidental early-match collisions
# (see PROGRESS.md's entry for this task for the verification method).
#
# Deliberately does NOT distinguish Small/Medium/Large/Largest (amplitude)
# or Single/Double/Triple/Alternating (repeat) -- see this task's brief's
# own principle, quoted in PathType's docstring.
_PATH_TYPE_RULES: list[tuple[str, PathType]] = [
    ("curve then straight", PathType.CURVE_THEN_STRAIGHT),
    ("curved cross", PathType.CURVED_CROSS),
    ("travel rotation", PathType.TRAVEL_ROTATION),
    ("travel arm spiral", PathType.SPIRAL),
    ("travel shaking", PathType.SHAKE),
    ("shaking", PathType.SHAKE),
    ("wrist flex", PathType.FLEX),
    ("cross movement", PathType.CROSS),
    ("bend", PathType.BEND),
    ("corner", PathType.CORNER),
    ("check", PathType.CHECK),
    ("box", PathType.BOX),
    ("zigzag", PathType.ZIGZAG),
    ("peaks", PathType.PEAKS),
    ("arrowhead", PathType.ARROWHEAD),
    ("hump", PathType.HUMP),
    ("loop", PathType.LOOP),
    ("wave", PathType.WAVE),
    ("curve", PathType.CURVED),
    ("straight movement", PathType.STRAIGHT),
    ("alternating movement", PathType.STRAIGHT),
    ("diagonal away movement", PathType.STRAIGHT),
    ("diagonal towards movement", PathType.STRAIGHT),
    ("diagonal between away", PathType.STRAIGHT),
    ("diagonal between towards", PathType.STRAIGHT),
    ("rotation", PathType.CIRCLE),
    ("circle", PathType.CIRCLE),
    ("touch", PathType.CONTACT),
    ("grasp", PathType.CONTACT),
    ("strike", PathType.CONTACT),
    ("brush", PathType.CONTACT),
    ("rub", PathType.CONTACT),
    ("surface", PathType.CONTACT),
    ("contact movement", PathType.FINGER),
    ("squeeze", PathType.FINGER),
    ("flick", PathType.FINGER),
    ("hinge movement", PathType.FINGER),
]

# Constant per path_type -- see the module docstring's "unverified
# assumptions" note. Every PathType value must have an entry (checked by
# main() before writing anything).
_DEFAULT_CURVATURE_BY_PATH_TYPE: dict[PathType, float] = {
    PathType.CONTACT: 0.0,
    PathType.FINGER: 0.0,
    PathType.STRAIGHT: 0.0,
    PathType.CURVED: 0.3,
    PathType.CIRCLE: 0.0,
    PathType.FLEX: 0.3,
    PathType.CROSS: 0.3,
    PathType.BEND: 0.3,
    PathType.CORNER: 0.3,
    PathType.CHECK: 0.3,
    PathType.BOX: 0.3,
    PathType.ZIGZAG: 0.3,
    PathType.PEAKS: 0.3,
    PathType.TRAVEL_ROTATION: 0.3,
    PathType.SHAKE: 0.3,
    PathType.SPIRAL: 0.3,
    PathType.HUMP: 0.3,
    PathType.LOOP: 0.3,
    PathType.WAVE: 0.3,
    PathType.CURVE_THEN_STRAIGHT: 0.3,
    PathType.CURVED_CROSS: 0.3,
    PathType.ARROWHEAD: 0.3,
}
_DEFAULT_AMPLITUDE = 10.0
_DEFAULT_REPEAT = 1


def _load_names() -> dict[int, dict[str, str]]:
    raw_text = resources.files("fsw_r.data").joinpath(NAMES_RESOURCE).read_text(encoding="utf-8")
    raw = json.loads(raw_text)
    names: dict[int, dict[str, str]] = {}
    for key, entry in raw.items():
        if key == "_meta":
            continue
        names[int(key, 16)] = entry
    return names


def path_type_for_name(name: str, base_hex: int) -> PathType:
    """Fail-loud (this task's brief, Part B2): raises, never silently
    falls back to STRAIGHT or any other default, if ``name`` matches no
    rule in ``_PATH_TYPE_RULES``."""
    lowered = name.lower()
    for keyword, path_type in _PATH_TYPE_RULES:
        if keyword in lowered:
            return path_type
    raise ValueError(
        f"base 0x{base_hex:x} ({name!r}): no _PATH_TYPE_RULES keyword matched -- "
        "add a rule for this name family rather than guessing a default (see this "
        "task's brief's Part B2: no silent fallback)."
    )


def main() -> None:
    names = _load_names()
    if len(names) != EXPECTED_TOTAL:
        raise RuntimeError(f"{NAMES_RESOURCE} has {len(names)} entries, expected {EXPECTED_TOTAL}")

    missing_curvature = [pt for pt in PathType if pt not in _DEFAULT_CURVATURE_BY_PATH_TYPE]
    if missing_curvature:
        raise RuntimeError(f"_DEFAULT_CURVATURE_BY_PATH_TYPE is missing entries for: {missing_curvature}")

    entries: dict[str, object] = {}
    path_type_counts: dict[str, int] = {}
    for group in range(11, 21):
        group_name, plane, is_hit = _GROUP_TABLE[group]
        start = GROUP_START[group - 1]
        end = GROUP_START[group] - 1  # inclusive
        for base_hex in range(start, end + 1):
            key = format(base_hex, "x")
            name_entry = names.get(base_hex)
            if name_entry is None:
                raise RuntimeError(f"base 0x{base_hex:x}: no entry in {NAMES_RESOURCE}")
            name = name_entry["name"]
            path_type = path_type_for_name(name, base_hex)
            path_type_counts[path_type.value] = path_type_counts.get(path_type.value, 0) + 1
            entries[key] = {
                "symbol_id": symbol_id_of(base_hex),
                "name": name,
                "group_name": group_name,
                "path_type": path_type.value,
                "plane": plane,
                "curvature": _DEFAULT_CURVATURE_BY_PATH_TYPE[path_type],
                "amplitude": _DEFAULT_AMPLITUDE,
                "repeat": _DEFAULT_REPEAT,
                "is_hit": is_hit,
            }

    if len(entries) != EXPECTED_TOTAL:
        raise RuntimeError(f"expected {EXPECTED_TOTAL} entries, got {len(entries)}")

    # C4/C5 (this task's brief): at least one non-STRAIGHT base in group
    # 02-03 (0x22a-0x24e), and (by construction, via path_type_for_name's
    # fail-loud contract) no base anywhere fell back to a default.
    straight_wall_plane_types = {
        entries[format(b, "x")]["path_type"]  # type: ignore[index]
        for b in range(GROUP_START[12], GROUP_START[13])
    }
    if straight_wall_plane_types == {"straight"}:
        raise RuntimeError(
            "every base in group 02-03 (Straight Wall Plane) still maps to path_type=straight -- "
            "the name->PathType mapping did not do anything; this is exactly the bug being fixed."
        )

    print("path_type distribution:")
    for path_type_value, count in sorted(path_type_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {path_type_value:22s} {count:3d}")

    output = {
        "_meta": {
            "source": (
                "path_type: each base symbol's own real ISWA name "
                "(data/iswa_base_symbol_names.json, signbank.org) via the ordered "
                "keyword table in this script's _PATH_TYPE_RULES -- NOT the group name "
                "anymore (see this task's brief, \"path_type từ tên BASE SYMBOL\", Part 0). "
                "plane/is_hit: still ISWA Manual Chapter 2 group names, unchanged from before."
            ),
            "method": (
                "path_type generated by looking up each base symbol's real name against an "
                "ordered keyword table (fail-loud: raises if no rule matches, never falls back "
                "to a default -- see path_type_for_name()). plane/is_hit/curvature/amplitude/"
                "repeat generated by formula from a 10-row (group -> plane/is_hit) table plus a "
                "constant-per-path_type table, NOT measured from any per-symbol dataset."
            ),
            "unverified_assumptions": [
                "plane for groups 11 (Contact), 12 (Finger Movement), 20 (Circles) is not stated "
                "by the group name; stored as null, core/movement_paths.py falls back to WALL at "
                "render time",
                "is_hit is still a per-GROUP flag (unchanged by this task) even though real names "
                "show 'Hits Wall/Floor/Ceiling/Chest' varies WITHIN some groups too (e.g. group 20's "
                "'Arm Circle Wall' vs 'Arm Circle Hits Wall') -- discovered while fetching real names "
                "for this task, out of THIS task's scope (only path_type was), flagged for later",
                "curvature/amplitude/repeat are constant per path_type, not derived from the real "
                "names' own Small/Medium/Large/Largest (amplitude -- task 3's job) or "
                "Single/Double/Triple/Alternating (repeat -- not yet in scope for any task) qualifiers",
                "the 17 new PathType values' sample() geometry (core/movement_paths.py) is this "
                "project's own approximation of what each name family's shape implies, not derived "
                "from any ISWA glyph measurement -- see PathType's own docstring",
            ],
            "count": EXPECTED_TOTAL,
            "path_type_distribution": dict(sorted(path_type_counts.items(), key=lambda kv: -kv[1])),
            "generated_by": "scripts/gen_movement_paths.py (path_type), scripts/fetch_base_symbol_names.py (names)",
        },
        **entries,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nWrote {len(entries)} entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
