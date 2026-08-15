"""Generates ``src/fsw_r/data/movement_paths.json`` for all 242 Category 2
(Movement) base symbols.

**``path_type`` comes from each base symbol's own real ISWA NAME**
(``data/iswa_base_symbol_names.json``, ``scripts/fetch_base_symbol_names.py``
-- the "`path_type` từ tên BASE SYMBOL" task), via the ordered keyword table
``_PATH_TYPE_RULES`` below.

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

**``amplitude`` comes from each base symbol's own real ISWA GLYPH size**
(``data/iswa_movement_glyph_sizes.json``, ``scripts/gen_movement_glyph_sizes.py``
-- the "`amplitude` từ variation + kích thước glyph" task), compared ONLY
within the same ``(base_symbol_id, path_type)`` group -- i.e. only against
its own sibling variations, never across different base symbols or
different path_types (see Part 0's own warning: a Zigzag glyph is wide
because it zigzags, not because it travels far -- comparing across shapes
would be exactly that mistake). ``variation_of()`` (Task 1) is what makes a
base's siblings identifiable in the first place; ``path_type_for_name()``
(this same script, Task 2) is what excludes a same-numbered but
differently-shaped "variation" (e.g. 02-03-001's variation 5, "Single
Wrist Flex", is FLEX, not STRAIGHT like variations 1-4) from being averaged
in with a shape it doesn't share. Every group's OWN amplitude values are
normalized so the group's own mean is exactly 10.0 (this project's
established average -- see ``timeline/anchor.py``'s
``SIGNBOX_TO_BODY_SCALE``, unchanged by this task) -- a singleton group
(no siblings, or the only member of its own shape-family within a base)
trivially normalizes to exactly 10.0, which doubles as the answer to this
task's brief's own Part A1 question ("base nào chỉ có một variation dùng
giá trị mặc định nào" -- 10.0, unchanged from before this task).

**``plane`` prefers each base symbol's own real ISWA NAME, falls back to
its GROUP's plane when the name doesn't say** (the "`plane` và `is_hit` từ
tên BASE SYMBOL" task, task 4/4 closing the Category 2 source-fidelity
chain): Task 2 fixed ``path_type`` but left ``plane``/``is_hit`` on the old
group-derived table, which that task's own ``_meta`` flagged as unverified.
Checked against the real names: 11 base symbols had a ``plane`` that
contradicted their own name (6 of them a complete WALL<->FLOOR swap --
group "Travel Rotation...Floor Plane" bases were tagged ``wall`` and vice
versa), and 13 had an ``is_hit`` that contradicted their name (the "Arm/
Wrist/Finger Circle(s) Hits Wall" family in group 20, which has no "Hit" in
its GROUP name so lost the flag entirely). See ``plane_for_name()``/
``is_hit_for_name()`` and PROGRESS.md's entry for this task for the full
tables, the corpus-impact numbers, and the A1 verification that group 12
(Finger Movement) -- assumed group-name-silent-on-plane like groups 11/20
-- actually has 2 base symbols whose OWN names do state a plane, discovered
only by checking A1's rule literally rather than trusting the Part 0 table.

**``is_hit`` comes ENTIRELY from each base symbol's own real ISWA NAME, no
group fallback** (unlike ``plane``): "Hit"/"Hits" appears explicitly in a
base symbol's own name whenever it applies, so there is no unlabeled case
to fall back for (see ``is_hit_for_name()``). Verified before switching:
groups 17/18 ("Curves Hit Wall/Floor Plane") have 46 combined base symbols,
43 of which say "Hit(s)" in their own name; the 3 that don't
(0x2b4-0x2b6, "Wave Diagonal Path") are exactly the ones Part 0 already
identified as mis-flagged (they're Diagonal-plane, non-hit symbols
stranded in a "Hit Wall Plane" group) -- not a sign the naming convention
itself is unreliable, so this did not trigger the brief's "dừng và báo"
guard.

** UNVERIFIED ASSUMPTIONS ** -- also recorded in the generated JSON's own
``_meta`` and in PROGRESS.md's entry for this task, not silently treated as
fact:
- ``plane`` for the 102 base symbols whose name says nothing about plane
  (mostly groups 11/12/20, where the GROUP name doesn't state one either)
  still falls back to the OLD group-derived value (``None`` for most of
  groups 11/12/20, the per-group value for the rest) -- ``core/movement_paths.py``
  still falls back to WALL at render time when ``plane`` is ``None``.
- ``curvature``/``repeat`` are still constant per path_type across all
  symbols that share it -- the real names literally spell out
  Single/Double/Triple/Alternating (repeat) that this script still does
  not use (out of scope for every task in this chain, see PROGRESS.md).
- the glyph-size ratio ``amplitude`` is derived from is a proxy for "how
  far the movement travels", not a direct measurement of it -- this
  project's own reading of what a bigger glyph implies, spot-checked
  against several cases (see PROGRESS.md) but not against any
  biomechanical ground truth.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from importlib import resources
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of  # noqa: E402
from fsw_r.core.types import PathType  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "movement_paths.json"
NAMES_RESOURCE = "iswa_base_symbol_names.json"
GLYPH_SIZES_RESOURCE = "iswa_movement_glyph_sizes.json"

EXPECTED_TOTAL = 242
_AMPLITUDE_GROUP_MEAN = 10.0  # this project's established average -- see timeline/anchor.py

# Global group number (11-20, from core/iswa_data.py's GROUP_START indices
# 10-19) -> (real name, plane fallback). Names from ISWA Manual Chapter 2;
# plane fallback is this project's own reading of what each GROUP name
# implies, used ONLY when a base's own name doesn't state one (see
# plane_for_name()). No is_hit column anymore -- is_hit no longer has a
# group-level fallback at all (see is_hit_for_name()'s own docstring for why
# none is needed).
_GROUP_TABLE: dict[int, tuple[str, str | None]] = {
    11: ("Contact", None),
    12: ("Finger Movement", None),
    13: ("Straight Wall Plane", "wall"),
    14: ("Straight Diagonal Plane", "diagonal"),
    15: ("Straight Floor Plane", "floor"),
    16: ("Curves Wall Plane", "wall"),
    17: ("Curves Hit Wall Plane", "wall"),
    18: ("Curves Hit Floor Plane", "floor"),
    19: ("Curves Floor Plane", "floor"),
    20: ("Circles", None),
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


def _load_glyph_sizes() -> dict[int, int]:
    """``base_hex -> max_dimension`` (see ``gen_movement_glyph_sizes.py``'s
    own docstring for why ``max(width, height)`` is the chosen scalar)."""
    raw_text = resources.files("fsw_r.data").joinpath(GLYPH_SIZES_RESOURCE).read_text(encoding="utf-8")
    raw = json.loads(raw_text)
    sizes: dict[int, int] = {}
    for key, entry in raw.items():
        if key == "_meta":
            continue
        sizes[int(key, 16)] = entry["max_dimension"]
    return sizes


def amplitudes_for_group(base_hexes: list[int], glyph_sizes: dict[int, int]) -> dict[int, float]:
    """Normalizes ``glyph_sizes`` for one ``(base_symbol_id, path_type)``
    sibling group so the GROUP's own mean lands on ``_AMPLITUDE_GROUP_MEAN``
    -- i.e. only the RATIO between siblings' glyph sizes matters, never
    their absolute size relative to a different base/path_type (Part 0's
    trap). A singleton group trivially normalizes to exactly
    ``_AMPLITUDE_GROUP_MEAN`` (own_size / own_size == 1)."""
    sizes = [glyph_sizes[b] for b in base_hexes]
    mean_size = sum(sizes) / len(sizes)
    return {b: _AMPLITUDE_GROUP_MEAN * (glyph_sizes[b] / mean_size) for b in base_hexes}


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


# Verified before use (see module docstring): no real name contains more
# than one of these three phrases, so checking all three and asserting at
# most one match is a real safety check, not defensive dead code.
_PLANE_PHRASES: list[tuple[str, str]] = [
    ("floor plane", "floor"),
    ("wall plane", "wall"),
    ("diagonal", "diagonal"),
]


def plane_for_name(name: str, base_hex: int) -> str | None:
    """``None`` if ``name`` doesn't state a plane -- the caller falls back
    to the base's GROUP plane in that case (this task's brief, Part A1:
    "tên base symbol có plane -> dùng nó; không có -> giữ giá trị group").
    Raises if a name somehow matches more than one plane phrase (would mean
    _PLANE_PHRASES itself is wrong, not a real ISWA name -- see the module
    docstring's note that this was verified never to happen across all 242
    real names before being trusted here)."""
    lowered = name.lower()
    matches = [plane for phrase, plane in _PLANE_PHRASES if phrase in lowered]
    if len(matches) > 1:
        raise RuntimeError(f"base 0x{base_hex:x} ({name!r}): name matches more than one plane phrase: {matches}")
    return matches[0] if matches else None


def is_hit_for_name(name: str) -> bool:
    """No fallback needed (unlike ``plane_for_name()``) -- "Hit"/"Hits"
    appears explicitly in a base symbol's own name whenever ``is_hit``
    applies (verified across all 242 real names before this replaced the
    old per-GROUP flag -- see module docstring and PROGRESS.md)."""
    return re.search(r"\bhits?\b", name.lower()) is not None


def main() -> None:
    names = _load_names()
    if len(names) != EXPECTED_TOTAL:
        raise RuntimeError(f"{NAMES_RESOURCE} has {len(names)} entries, expected {EXPECTED_TOTAL}")
    glyph_sizes = _load_glyph_sizes()
    if len(glyph_sizes) != EXPECTED_TOTAL:
        raise RuntimeError(f"{GLYPH_SIZES_RESOURCE} has {len(glyph_sizes)} entries, expected {EXPECTED_TOTAL}")

    missing_curvature = [pt for pt in PathType if pt not in _DEFAULT_CURVATURE_BY_PATH_TYPE]
    if missing_curvature:
        raise RuntimeError(f"_DEFAULT_CURVATURE_BY_PATH_TYPE is missing entries for: {missing_curvature}")

    # Pass 1: path_type + which (base_symbol_id, path_type) sibling group
    # each base belongs to -- amplitude (pass 2) can only be computed once
    # every base's real path_type is known (Part 0: the whole reason this
    # task waited for Task 2).
    path_type_by_base: dict[int, PathType] = {}
    base_symbol_id_by_base: dict[int, str] = {}
    for group in range(11, 21):
        start = GROUP_START[group - 1]
        end = GROUP_START[group] - 1  # inclusive
        for base_hex in range(start, end + 1):
            name_entry = names.get(base_hex)
            if name_entry is None:
                raise RuntimeError(f"base 0x{base_hex:x}: no entry in {NAMES_RESOURCE}")
            path_type_by_base[base_hex] = path_type_for_name(name_entry["name"], base_hex)
            category, grp, base, _variation = name_entry["symbol_id"].split("-")
            base_symbol_id_by_base[base_hex] = f"{category}-{grp}-{base}"

    sibling_groups: dict[tuple[str, PathType], list[int]] = defaultdict(list)
    for base_hex in path_type_by_base:
        sibling_key = (base_symbol_id_by_base[base_hex], path_type_by_base[base_hex])
        sibling_groups[sibling_key].append(base_hex)

    amplitude_by_base: dict[int, float] = {}
    for base_hexes in sibling_groups.values():
        amplitude_by_base.update(amplitudes_for_group(base_hexes, glyph_sizes))

    # Pass 2: build the full entries, now that path_type/amplitude are known
    # for every base.
    entries: dict[str, object] = {}
    path_type_counts: dict[str, int] = {}
    plane_from_name_count = 0
    plane_from_group_fallback_count = 0
    is_hit_true_count = 0
    for group in range(11, 21):
        group_name, group_plane_fallback = _GROUP_TABLE[group]
        start = GROUP_START[group - 1]
        end = GROUP_START[group] - 1  # inclusive
        for base_hex in range(start, end + 1):
            key = format(base_hex, "x")
            name = names[base_hex]["name"]
            path_type = path_type_by_base[base_hex]
            path_type_counts[path_type.value] = path_type_counts.get(path_type.value, 0) + 1

            plane_from_name = plane_for_name(name, base_hex)
            plane: str | None
            if plane_from_name is not None:
                plane = plane_from_name
                plane_from_name_count += 1
            else:
                plane = group_plane_fallback
                plane_from_group_fallback_count += 1

            is_hit = is_hit_for_name(name)
            if is_hit:
                is_hit_true_count += 1

            entries[key] = {
                "symbol_id": symbol_id_of(base_hex),
                "name": name,
                "group_name": group_name,
                "path_type": path_type.value,
                "plane": plane,
                "curvature": _DEFAULT_CURVATURE_BY_PATH_TYPE[path_type],
                "amplitude": round(amplitude_by_base[base_hex], 4),
                "repeat": _DEFAULT_REPEAT,
                "is_hit": is_hit,
            }

    if len(entries) != EXPECTED_TOTAL:
        raise RuntimeError(f"expected {EXPECTED_TOTAL} entries, got {len(entries)}")
    print(
        f"plane: {plane_from_name_count} from the base's own name, "
        f"{plane_from_group_fallback_count} fell back to the group's plane"
    )
    print(f"is_hit: {is_hit_true_count}/{EXPECTED_TOTAL} True (all from the base's own name, no fallback)")

    # B3/B4 (this task's brief): after the switch, 0 bases may still
    # disagree with their own name -- re-verify with the SAME independent
    # check used to find the original 11/13 mismatches (see PROGRESS.md),
    # not just trust that the code above did the right thing.
    plane_mismatches = []
    is_hit_mismatches = []
    for key, entry in entries.items():
        name = entry["name"]  # type: ignore[index]
        assert isinstance(name, str)
        name_plane = plane_for_name(name, int(key, 16))
        if name_plane is not None and name_plane != entry["plane"]:  # type: ignore[index]
            plane_mismatches.append(key)
        if is_hit_for_name(name) != entry["is_hit"]:  # type: ignore[index]
            is_hit_mismatches.append(key)
    if plane_mismatches:
        raise RuntimeError(f"{len(plane_mismatches)} base symbols still disagree with their own name's plane: {plane_mismatches}")
    if is_hit_mismatches:
        raise RuntimeError(f"{len(is_hit_mismatches)} base symbols still disagree with their own name's is_hit: {is_hit_mismatches}")

    # B4 (this task's brief): overall mean amplitude must stay within +/-20%
    # of 10.0 -- guards against the per-group normalization somehow drifting
    # in aggregate (it shouldn't, by construction, but checked rather than
    # assumed).
    overall_mean = sum(amplitude_by_base.values()) / len(amplitude_by_base)
    if not (0.8 * _AMPLITUDE_GROUP_MEAN <= overall_mean <= 1.2 * _AMPLITUDE_GROUP_MEAN):
        raise RuntimeError(
            f"overall mean amplitude = {overall_mean:.3f}, outside +/-20% of {_AMPLITUDE_GROUP_MEAN} "
            "(this task's brief, A3/B4) -- would shift the global animation scale calibrated in "
            "earlier phases (see timeline/anchor.py's SIGNBOX_TO_BODY_SCALE)."
        )
    print(f"overall mean amplitude = {overall_mean:.4f} (target {_AMPLITUDE_GROUP_MEAN}, +/-20% allowed)")

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
                "anymore (see \"path_type từ tên BASE SYMBOL\" task, Part 0). "
                "amplitude: each base symbol's own real ISWA glyph bounding-box size "
                "(data/iswa_movement_glyph_sizes.json, the real ISWA font), compared ONLY "
                "against its own sibling variations (same base_symbol_id AND path_type) -- "
                "see \"amplitude từ variation + kích thước glyph\" task, Part 0/A2. "
                "plane: each base symbol's own real ISWA name FIRST (floor plane/wall plane/"
                "diagonal), falls back to the base's GROUP plane only when the name doesn't "
                "state one -- see \"plane và is_hit từ tên BASE SYMBOL\" task (task 4/4), "
                "plane_for_name(). is_hit: ENTIRELY from each base symbol's own real ISWA "
                "name (Hit/Hits), no group fallback -- see is_hit_for_name()."
            ),
            "layer": (
                "path_type: derived (real ISWA name, exact keyword match, no numeric estimation). "
                "amplitude: derived (real ISWA font glyph size), NOT AUTHORED -- chosen over an "
                "authored small/medium/large/largest numeric scale because it needed no assumption "
                "about how many size levels exist or what order they're named in (this task's own "
                "A1 finding: variation is not a single consistent size scale across all base "
                "symbols -- see PROGRESS.md). Every group's own mean is normalized to 10.0, so only "
                "the RELATIVE ratio between sibling glyphs is real derived data; the absolute scale "
                "(10.0) is this project's own choice, carried over unchanged from before this task. "
                "plane: derived where the base's own name states one (140/242 -- see "
                "plane_from_name_count below), otherwise still this project's own reading of the "
                "GROUP name (102/242, unchanged fallback). is_hit: fully derived (real ISWA name, "
                "exact 'Hit'/'Hits' match, no numeric estimation, no fallback)."
            ),
            "method": (
                "path_type generated by looking up each base symbol's real name against an "
                "ordered keyword table (fail-loud: raises if no rule matches, never falls back "
                "to a default -- see path_type_for_name()). amplitude generated by grouping base "
                "symbols by (base_symbol_id, path_type) -- i.e. only symbols that are real siblings "
                "AND share a real trajectory shape -- then scaling each sibling's own glyph "
                "max(width, height) so the group's mean is exactly 10.0 (see amplitudes_for_group()). "
                "plane generated by plane_for_name() (checks the base's own name for 'floor plane'/"
                "'wall plane'/'diagonal'; None if absent) falling back to the old per-GROUP table "
                "only when None. is_hit generated by is_hit_for_name() (checks the base's own name "
                "for 'hit'/'hits' as a whole word) with NO fallback. Both re-verified after "
                "generation against the same independent check used to find the original mismatches "
                "-- main() raises if either comes up nonzero (see PROGRESS.md's B3/B4)."
            ),
            "unverified_assumptions": [
                "plane for the 102 base symbols whose own name says nothing about plane still "
                "falls back to the OLD group-derived value (None for most of groups 11/12/20, "
                "the per-group value for the rest); core/movement_paths.py falls back to WALL at "
                "render time when plane is None",
                "curvature/repeat are still constant per path_type, not derived from the real names' "
                "own Single/Double/Triple/Alternating qualifiers (repeat) -- discovered but not in "
                "scope for any task in this chain, flagged for a future task",
                "the 17 non-original PathType values' sample() geometry (core/movement_paths.py) is "
                "this project's own approximation of what each name family's shape implies, not "
                "derived from any ISWA glyph measurement -- see PathType's own docstring",
                "glyph size ratio is a proxy for travel distance, not a direct biomechanical "
                "measurement -- spot-checked against several cases (see PROGRESS.md), not exhaustively",
            ],
            "count": EXPECTED_TOTAL,
            "path_type_distribution": dict(sorted(path_type_counts.items(), key=lambda kv: -kv[1])),
            "amplitude_overall_mean": round(overall_mean, 4),
            "plane_from_name_count": plane_from_name_count,
            "plane_from_group_fallback_count": plane_from_group_fallback_count,
            "is_hit_true_count": is_hit_true_count,
            "generated_by": "scripts/gen_movement_paths.py (path_type, amplitude, plane, is_hit), "
            "scripts/fetch_base_symbol_names.py (names), scripts/gen_movement_glyph_sizes.py (glyph sizes)",
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
