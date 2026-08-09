"""Generates ``src/fsw_r/data/body_poses.json`` for all 18 Category 5
(Trunk & Limb / "Body") base symbols.

Provenance, stated honestly (same standard as ``gen_face_poses.py``): the
base-symbol NAMES are the real, authoritative ISWA names, fetched from
signbank.org's ISWA 2010 HTML reference (``iswa/36d_sg.html`` for Group 27
"Trunk", ``iswa/376_sg.html`` for Group 28 "Limb" -- each group's 9 base
symbols are listed on ONE page, keyed by the group's first base hex, not
one page per base symbol). ``part``/``motion_type``/``limb_length_units``
are derived directly from those verified names (traceable, not invented).
``trunk_rotation_deg``/``shoulder_offset`` are AUTHORED constant
placeholders (identity / zero) -- there is no dataset or verified formula
that would justify assigning "Torso Curved Bend Wall" a different specific
numeric angle than "Upper Body Tilts", so no such number is invented; see
``core/body_types.py``'s module docstring.

Run:  python scripts/gen_body_poses.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of

# Group 27 (Trunk, 0x36d-0x375): base_hex -> (real name, motion_type).
# Names verified against signbank.org/iswa/36d_sg.html.
_TRUNK: dict[int, tuple[str, str]] = {
    0x36D: ("Shoulder Hip Spine", "REFERENCE"),
    0x36E: ("Shoulder Hip Positions", "POSITIONS"),
    0x36F: ("Shoulder Hip Move Wall Plane", "MOVE_WALL"),
    0x370: ("Shoulder Hip Move Floor Plane", "MOVE_FLOOR"),
    0x371: ("Shoulder Tilts (from Waist)", "TILT_WAIST"),
    0x372: ("Torso Straight Stretch Wall", "STRETCH_WALL"),
    0x373: ("Torso Curved Bend Wall", "BEND_WALL"),
    0x374: ("Torso Twist Floor Plane", "TWIST_FLOOR"),
    0x375: ("Upper Body Tilts (from Hip Joints)", "TILT_HIP"),
}

# Group 28 (Limb, 0x376-0x37e): base_hex -> (real name, limb_length_units).
# Names verified against signbank.org/iswa/376_sg.html. "Limb Length N"
# gives limb_length_units directly; "Limb Combinations" and "Fingers" are
# not a fixed length (0).
_LIMB: dict[int, tuple[str, int]] = {
    0x376: ("Limb Combinations", 0),
    0x377: ("Limb Length 1", 1),
    0x378: ("Limb Length 2", 2),
    0x379: ("Limb Length 3", 3),
    0x37A: ("Limb Length 4", 4),
    0x37B: ("Limb Length 5", 5),
    0x37C: ("Limb Length 6", 6),
    0x37D: ("Limb Length 7", 7),
    0x37E: ("Fingers", 0),
}

EXPECTED_TOTAL = 18
_TRUNK_GROUP_START = GROUP_START[26]  # group 27 (1-indexed) -> tuple index 26
_LIMB_GROUP_START = GROUP_START[27]  # group 28 (1-indexed) -> tuple index 27


def build() -> dict[str, object]:
    if _TRUNK_GROUP_START != 0x36D or _LIMB_GROUP_START != 0x376:
        raise RuntimeError(
            f"GROUP_START moved (trunk=0x{_TRUNK_GROUP_START:03x}, "
            f"limb=0x{_LIMB_GROUP_START:03x}) -- _TRUNK/_LIMB tables above are stale"
        )
    if set(_TRUNK) != set(range(0x36D, 0x376)):
        raise RuntimeError("_TRUNK does not cover exactly group 27 (0x36d-0x375)")
    if set(_LIMB) != set(range(0x376, 0x37F)):
        raise RuntimeError("_LIMB does not cover exactly group 28 (0x376-0x37e)")

    entries: dict[str, object] = {}
    for base_hex, (name, motion_type) in _TRUNK.items():
        entries[format(base_hex, "x")] = {
            "symbol_id": symbol_id_of(base_hex),
            "name": name,
            "part": "trunk",
            "motion_type": motion_type,
            "trunk_rotation_deg": [0.0, 0.0, 0.0],
            "shoulder_offset": [0.0, 0.0, 0.0],
            "limb_length_units": None,
        }
    for base_hex, (name, limb_length_units) in _LIMB.items():
        entries[format(base_hex, "x")] = {
            "symbol_id": symbol_id_of(base_hex),
            "name": name,
            "part": "limb",
            "motion_type": "LENGTH" if limb_length_units > 0 else name.upper().replace(" ", "_"),
            "trunk_rotation_deg": None,
            "shoulder_offset": None,
            "limb_length_units": limb_length_units,
        }

    if len(entries) != EXPECTED_TOTAL:
        raise RuntimeError(f"expected {EXPECTED_TOTAL} entries, got {len(entries)}")

    return {
        "_meta": {
            "names_source": (
                "signbank.org ISWA 2010 reference -- iswa/36d_sg.html (Group 27, Trunk) "
                "and iswa/376_sg.html (Group 28, Limb), each listing its group's 9 base "
                "symbols on one page -- authoritative ISWA names"
            ),
            "structure_source": (
                "part/motion_type/limb_length_units are derived directly from those "
                "verified names (traceable, not invented) -- see PROGRESS.md's Category 5 entry"
            ),
            "values_source": (
                "AUTHORED placeholders, not measured -- trunk_rotation_deg is identity "
                "([0,0,0]) and shoulder_offset is zero for every one of the 9 Trunk "
                "symbols; no dataset or verified formula distinguishes them numerically "
                "yet. See core/body_types.py's module docstring."
            ),
            "fill_rotation_note": (
                "fill/rotation semantics for Category 5 are UNVERIFIED (measured on "
                "SignBank+: 92.5% fill=0, 88.7% rotation 0-7 -- too skewed/noisy to guess "
                "a formula from) -- BodyPose does not vary by fill/rotation, keyed by "
                "base_hex only. See core/body_symbol.py's hand_side docstring."
            ),
            "count": EXPECTED_TOTAL,
            "generated_by": "scripts/gen_body_poses.py",
        },
        **entries,
    }


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "body_poses.json"
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(build(), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {EXPECTED_TOTAL} entries to {target}")


if __name__ == "__main__":
    main()
