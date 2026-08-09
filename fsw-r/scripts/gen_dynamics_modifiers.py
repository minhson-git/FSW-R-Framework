"""Generates ``src/fsw_r/data/dynamics_modifiers.json`` for all 8 Category 3
(Dynamics) base symbols.

Provenance, stated honestly (same standard as ``gen_face_poses.py`` /
``gen_body_poses.py``): the base-symbol NAMES are the real, authoritative
ISWA names, fetched from signbank.org's ISWA 2010 HTML reference
(``iswa/2f7_sg.html`` -- all 8 Category 3 base symbols are listed on this
one page, Group 21 "Dynamics & Timing"). ``DynamicsModifier`` FIELD VALUES
are AUTHORED -- a human reading of each name -- NOT measured; see
``core/dynamics_types.py``'s module docstring for why intra-base
fill/rotation variation is deliberately not decoded.

Run:  python scripts/gen_dynamics_modifiers.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of

# base_hex -> (real name, speed, repeat, tension, alternating). Names
# verified against signbank.org/iswa/2f7_sg.html.
_DYNAMICS: dict[int, tuple[str, float, int | None, bool, bool]] = {
    0x2F7: ("Fast", 0.7, None, False, False),
    0x2F8: ("Slow", 1.4, None, False, False),
    0x2F9: ("Tense", 1.0, None, True, False),
    0x2FA: ("Relaxed", 1.0, None, False, False),
    0x2FB: ("Same Time", 1.0, None, False, False),
    0x2FC: ("Same Time Alternating", 1.0, None, False, True),
    0x2FD: ("Every Other Time", 1.0, 2, False, True),
    # "Gradual" (a tempo that changes DURING the sign) doesn't fit any
    # current field precisely -- left at the neutral default rather than
    # forcing it into speed/repeat/tension/alternating; flagged explicitly
    # in _meta below, not silently treated as "no effect".
    0x2FE: ("Gradual", 1.0, None, False, False),
}

EXPECTED_TOTAL = 8
_GROUP_START = GROUP_START[20]  # group 21 (1-indexed) -> tuple index 20


def build() -> dict[str, object]:
    if _GROUP_START != 0x2F7:
        raise RuntimeError(f"GROUP_START moved (dynamics=0x{_GROUP_START:03x}) -- _DYNAMICS table above is stale")
    if set(_DYNAMICS) != set(range(0x2F7, 0x2FF)):
        raise RuntimeError("_DYNAMICS does not cover exactly group 21 (0x2f7-0x2fe)")

    entries: dict[str, object] = {}
    for base_hex, (name, speed, repeat, tension, alternating) in _DYNAMICS.items():
        entries[format(base_hex, "x")] = {
            "symbol_id": symbol_id_of(base_hex),
            "name": name,
            "speed": speed,
            "repeat": repeat,
            "tension": tension,
            "alternating": alternating,
        }

    if len(entries) != EXPECTED_TOTAL:
        raise RuntimeError(f"expected {EXPECTED_TOTAL} entries, got {len(entries)}")

    return {
        "_meta": {
            "names_source": (
                "signbank.org ISWA 2010 reference -- iswa/2f7_sg.html (Group 21, "
                "Dynamics & Timing), listing all 8 base symbols on one page -- "
                "authoritative ISWA names"
            ),
            "values_source": (
                "AUTHORED, not measured -- speed/repeat/tension/alternating are a "
                "human reading of each symbol's real name mapped onto "
                "DynamicsModifier's fields. No dataset keys ISWA Dynamics symbols "
                "to numeric timing coefficients."
            ),
            "unverified_assumptions": [
                "intra-base fill/rotation variation (Fast/Tense/Relaxed vary by "
                "fill 1-4; Slow/Same-Time-family/Gradual vary by rotation 1-8) is "
                "NOT decoded -- every valid (fill, rotation) of a base gets the "
                "same DynamicsModifier, see core/dynamics_types.py",
                "'Gradual' (0x2fe) doesn't fit speed/repeat/tension/alternating "
                "precisely (its real meaning is a tempo that changes DURING the "
                "sign) -- stored at the neutral default rather than guessed",
                "speed's exact numeric values (Fast=0.7, Slow=1.4) are illustrative "
                "authored placeholders, not calibrated against any real sign timing",
            ],
            "count": EXPECTED_TOTAL,
            "generated_by": "scripts/gen_dynamics_modifiers.py",
        },
        **entries,
    }


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "dynamics_modifiers.json"
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(build(), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {EXPECTED_TOTAL} entries to {target}")


if __name__ == "__main__":
    main()
