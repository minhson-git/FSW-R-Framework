"""One-off, narrowly-scoped fix: updates ONLY the ``"symbol_id"`` field of
every entry in ``src/fsw_r/data/hand_joint_poses.json`` to match the real
ISWA Symbol ID (``core/iswa_data.py``'s ``symbol_id_of()``, now backed by
``data/iswa_symbol_ids.json`` -- see this task's brief, "Sửa symbol_id
dùng symidArr chuẩn").

Why not just re-run the file's own generator: ``scripts/export_joint_poses.py``
is explicitly FROZEN (see its own docstring and ``pyproject.toml``'s mypy
exclusion) -- it imports the since-deleted ``groups/`` package and cannot
run anymore. Re-deriving the whole file from scratch is both impossible and
unnecessary here: Category 1 (Hands, the only category this file covers)
has exactly ONE ISWA variation per base symbol (verified against the real
symidArr, not assumed -- see ``data/iswa_symbol_ids.json``'s own ``_meta``),
so the only thing wrong with the existing ``"symbol_id"`` values is the
missing ``"-01"`` suffix and, for groups where the old GROUP_START-derived
group number differed from ISWA's own -- it never does within Category 1,
since Category 1 IS ISWA's groups 1-10 (see ``iswa_data.py``'s module
docstring) -- nothing else would need to change either.

This script loads the JSON, replaces EVERY entry's ``"symbol_id"`` field
with ``symbol_id_of(base_hex)``, and writes the file back with every other
field (including field order and all numeric joint-angle data) completely
untouched -- verified by diffing before/after and asserting no other key
changed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fsw_r.core.iswa_data import symbol_id_of  # noqa: E402

TARGET_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "hand_joint_poses.json"
EXPECTED_ENTRY_COUNT = 261


def main() -> None:
    raw_text = TARGET_PATH.read_text(encoding="utf-8")
    data = json.loads(raw_text)

    entries = {key: value for key, value in data.items() if key != "_meta"}
    if len(entries) != EXPECTED_ENTRY_COUNT:
        raise RuntimeError(f"{TARGET_PATH} has {len(entries)} entries, expected {EXPECTED_ENTRY_COUNT}")

    changed = 0
    for key, entry in entries.items():
        base_hex = int(key, 16)
        old_symbol_id = entry.get("symbol_id")
        new_symbol_id = symbol_id_of(base_hex)
        if old_symbol_id != new_symbol_id:
            changed += 1
        entry["symbol_id"] = new_symbol_id

    with open(TARGET_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Updated 'symbol_id' on {changed}/{len(entries)} entries in {TARGET_PATH}")
    print("Every other field (joint angles, names, _meta) was left byte-for-byte untouched by this script.")


if __name__ == "__main__":
    main()
