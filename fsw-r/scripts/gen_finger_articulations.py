"""Generates ``src/fsw_r/data/finger_articulations.json`` for all 20
Category 2 Group 12 (Finger Movement) base symbols (0x216-0x229).

Provenance, stated honestly (same standard as ``gen_dynamics_modifiers.py``/
``gen_body_poses.py``): the 5 leading base symbols' NAMES (covering 76.1% of
real Group 12 token usage, sign-language-processing/signbank-plus corpus --
see PROGRESS.md's "Chuyển động khớp ngón tay" entry) are the real,
authoritative ISWA names, fetched from signbank.org's ISWA 2010 HTML
reference (``iswa/{hex}/{hex}_bs.html``, one page per base symbol). The
other 15 bases' names were NOT individually looked up (out of this task's
own stated scope -- "15 base còn lại có thể dùng giá trị mặc định") and get
a shared DEFAULT ``FingerArticulation`` instead, flagged explicitly below and
in ``_meta``. ``FingerArticulation`` FIELD VALUES for ALL 20 bases --
including the 5 with real names -- are AUTHORED: a human reading of each
name mapped onto amplitude_deg/cycles/phase_offset/fingers/joints, NOT
measured. No dataset maps ISWA finger-movement symbols to numeric joint-angle
amplitudes.

Run:  python scripts/gen_finger_articulations.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fsw_r.core.iswa_data import GROUP_START, symbol_id_of

EXPECTED_TOTAL = 20
_GROUP_START = GROUP_START[11]  # group 12 (1-indexed) -> tuple index 11

# The 5 base symbols covering 76.1% of real Group 12 token usage (see
# PROGRESS.md's own measurement table for this task) -- names verified
# against signbank.org/iswa/{hex}/{hex}_bs.html, fetched individually.
# fields: (real name, fingers, joints, amplitude_deg, cycles, phase_offset)
_RESEARCHED: dict[int, tuple[str, frozenset[str], frozenset[str], float, float, float]] = {
    # "Hinge Movement, Up Down Large" (38.2% of all Group 12 tokens, the
    # single most common base by a wide margin) -- the name does not
    # specify which finger, so this project's own reading applies it to
    # all 4 non-thumb fingers at the MCP ("hinge") joint, moving in sync
    # (phase_offset=0 -- "Alternating" is a DIFFERENT, separately-named
    # base, see 0x225 below, so its absence here is meaningful, not an
    # oversight). "Large" -> the larger of this project's two amplitude
    # tiers (see 0x222 "Small" below for the smaller one).
    0x221: ("Hinge Movement, Up Down Large", frozenset({"index", "middle", "ring", "pinky"}), frozenset({"mcp"}), 30.0, 2.0, 0.0),
    # "Hinge Movement, Up Down Alternating Large" (16.0%) -- same
    # fingers/joint/amplitude as 0x221, but "Alternating" explicitly names
    # a phase difference between fingers -- modeled as a fixed pi/2 (90
    # degree) stagger per finger in canonical order (thumb, index, middle,
    # ring, pinky -- see core/finger_articulation.py), producing a
    # "ripple" across the 4 fingers rather than them moving in lockstep.
    # The EXACT stagger amount is this project's own choice -- ISWA does
    # not specify a numeric phase difference for "Alternating".
    0x225: ("Hinge Movement, Up Down Alternating Large", frozenset({"index", "middle", "ring", "pinky"}), frozenset({"mcp"}), 30.0, 2.0, 1.5707963267948966),
    # "Squeeze Large Single" (8.9%) -- "Squeeze" (unlike "Hinge Up Down")
    # implies the WHOLE finger curling in, not just the base knuckle --
    # applied to MCP+PIP together. "Single" (contrasted with "Alternating"
    # above and with a hypothetical repeated variant) -> cycles=1, one
    # squeeze-and-release, not a repeated wiggle.
    0x216: ("Squeeze Large Single", frozenset({"index", "middle", "ring", "pinky"}), frozenset({"mcp", "pip"}), 30.0, 1.0, 0.0),
    # "Flick Large Single" (7.9%) -- a flick is a single-finger, sharp,
    # distal-joint snap -- this project's own reading targets the INDEX
    # finger only (the most common single-finger gesture) at PIP+DIP (the
    # distal joints, where a "flick" snap visibly happens), NOT MCP.
    # "Single" -> cycles=1, same reasoning as 0x216.
    0x21B: ("Flick Large Single", frozenset({"index"}), frozenset({"pip", "dip"}), 35.0, 1.0, 0.0),
    # "Hinge Movement, Up Down Small" (5.1%) -- same reading as 0x221, but
    # "Small" -> this project's smaller amplitude tier (half of "Large"'s
    # 30 degrees).
    0x222: ("Hinge Movement, Up Down Small", frozenset({"index", "middle", "ring", "pinky"}), frozenset({"mcp"}), 15.0, 2.0, 0.0),
}

# Shared DEFAULT for the other 15 bases -- NOT individually researched
# (out of this task's stated scope). A moderate, generic reading: all 4
# non-thumb fingers, MCP joint, an amplitude between the researched
# "Small" (15) and "Large" (30) tiers, 2 cycles, in sync.
_DEFAULT_FINGERS = frozenset({"index", "middle", "ring", "pinky"})
_DEFAULT_JOINTS = frozenset({"mcp"})
_DEFAULT_AMPLITUDE_DEG = 20.0
_DEFAULT_CYCLES = 2.0
_DEFAULT_PHASE_OFFSET = 0.0


def build() -> dict[str, object]:
    if _GROUP_START != 0x216:
        raise RuntimeError(f"GROUP_START moved (group 12 = 0x{_GROUP_START:03x}) -- this script is stale")
    all_bases = set(range(0x216, 0x22A))
    if not set(_RESEARCHED) <= all_bases:
        raise RuntimeError("_RESEARCHED contains a base outside group 12 (0x216-0x229)")

    entries: dict[str, object] = {}
    default_bases: list[str] = []
    for base_hex in sorted(all_bases):
        key = format(base_hex, "x")
        if base_hex in _RESEARCHED:
            name, fingers, joints, amplitude_deg, cycles, phase_offset = _RESEARCHED[base_hex]
        else:
            name = None
            fingers, joints = _DEFAULT_FINGERS, _DEFAULT_JOINTS
            amplitude_deg, cycles, phase_offset = _DEFAULT_AMPLITUDE_DEG, _DEFAULT_CYCLES, _DEFAULT_PHASE_OFFSET
            default_bases.append(key)
        entries[key] = {
            "symbol_id": symbol_id_of(base_hex),
            "name": name,
            "fingers": sorted(fingers),
            "joints": sorted(joints),
            "amplitude_deg": amplitude_deg,
            "cycles": cycles,
            "phase_offset": phase_offset,
        }

    if len(entries) != EXPECTED_TOTAL:
        raise RuntimeError(f"expected {EXPECTED_TOTAL} entries, got {len(entries)}")

    return {
        "_meta": {
            "names_source": (
                "signbank.org ISWA 2010 reference -- iswa/{hex}/{hex}_bs.html, one page "
                "per base symbol (0x221, 0x225, 0x216, 0x21b, 0x222 fetched "
                "individually) -- authoritative ISWA names, for the 5 bases "
                "covering 76.1% of real Group 12 token usage. The other 15 "
                "bases' real names were NOT looked up (out of this task's "
                "stated scope) -- their 'name' field is null, see "
                "'default_bases' below."
            ),
            "values_source": (
                "AUTHORED, not measured, for ALL 20 entries including the 5 "
                "with real names -- fingers/joints/amplitude_deg/cycles/"
                "phase_offset are a human reading of each name (or, for the "
                "15 defaulted bases, a generic placeholder) mapped onto "
                "FingerArticulation's fields. No dataset maps ISWA "
                "finger-movement symbols to numeric joint-angle amplitudes."
            ),
            "default_bases": default_bases,
            "unverified_assumptions": [
                "which finger(s) participate for the 3 base symbols whose "
                "real name does not specify one ('Hinge Movement, Up Down "
                "Large/Small/Alternating Large' -- 0x221/0x222/0x225): "
                "AUTHORED as all 4 non-thumb fingers together; ISWA may "
                "intend this to depend on which fingers the SIGN's own "
                "Category 1 hand symbol has extended, which this table "
                "does not encode",
                "'Alternating' (0x225) phase_offset is a fixed pi/2 stagger "
                "per finger in canonical order -- an arbitrary but "
                "documented choice, not an ISWA-specified numeric value",
                "'Flick' (0x21b) targeting the index finger specifically, "
                "and at PIP+DIP rather than MCP, is this project's own "
                "reading of what a single-finger 'flick' snap looks like -- "
                "not confirmed against any per-finger ISWA source",
                "amplitude_deg's two researched tiers (Large=30, Small=15) "
                "and the 15 defaulted bases' amplitude (20) are illustrative "
                "authored placeholders, not calibrated against any real "
                "sign's finger movement",
                "the 15 defaulted bases (see 'default_bases' above) were not "
                "individually researched at all -- they share one generic "
                "placeholder, not a reading of their own real ISWA names",
            ],
            "count": EXPECTED_TOTAL,
            "generated_by": "scripts/gen_finger_articulations.py",
        },
        **entries,
    }


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "finger_articulations.json"
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(build(), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {EXPECTED_TOTAL} entries to {target}")


if __name__ == "__main__":
    main()
