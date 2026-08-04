"""One-time migration: extract the real, dataset-derived joint pose of every
registered Category 1 (Hands) base symbol out of the ``groups/*.py`` class
hierarchy and into ``src/fsw_r/data/hand_joint_poses.json`` -- the new
single source of truth for joint angles (see PROGRESS.md's "Refactor tang
Group sang data-driven" entry for why).

This does NOT recompute or change any angle: it imports the existing
``groups/`` modules, instantiates each registered class (using that base
symbol's own first valid fill, from ``core/iswa_data.py``, and rotation=0
-- joint pose never varies with either), and calls the existing
``get_joint_pose()``. The output is exactly what the current code already
produces, just relocated.

Run once against the ``groups/`` implementation; after
``core/pose_table.py`` is reading from the JSON this produces and a parity
check confirms the two agree, ``groups/`` is deleted.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import cast

import fsw_r.groups.group_01_index_finger as group_01
import fsw_r.groups.group_02_index_middle_fingers as group_02
import fsw_r.groups.group_03_index_middle_thumb as group_03
import fsw_r.groups.group_04_four_fingers as group_04
import fsw_r.groups.group_05_five_fingers as group_05
import fsw_r.groups.group_06_baby_finger as group_06
import fsw_r.groups.group_07_ring_finger as group_07
import fsw_r.groups.group_08_middle_finger as group_08
import fsw_r.groups.group_09_index_thumb as group_09
import fsw_r.groups.group_10_thumb as group_10
from fsw_r.core.iswa_data import HAND_GROUP_START, valid_combinations_for
from fsw_r.core.registry import _REGISTRY  # noqa: SLF001 -- one-off migration script
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose

_ALL_GROUP_MODULES = (
    group_01, group_02, group_03, group_04, group_05,
    group_06, group_07, group_08, group_09, group_10,
)  # imported so @register_symbol runs for every group; referenced to keep linters happy

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "hand_joint_poses.json"

_NAME_RE = re.compile(r'01-\d{2}-\d{3}\s+"([^"]+)"')


def _extract_name(cls: type) -> str:
    doc = cls.__doc__ or ""
    match = _NAME_RE.search(doc)
    if match is None:
        raise ValueError(f"could not find a real name in {cls.__name__}'s docstring")
    return match.group(1)


def _joint_angle_to_dict(angle: JointAngle) -> dict[str, float]:
    return {"flexion": angle.flexion, "abduction": angle.abduction}


def _finger_to_dict(finger: FingerPose) -> dict[str, dict[str, float]]:
    return {
        "mcp": _joint_angle_to_dict(finger.mcp),
        "pip": _joint_angle_to_dict(finger.pip),
        "dip": _joint_angle_to_dict(finger.dip),
    }


def _thumb_to_dict(thumb: ThumbPose) -> dict[str, dict[str, float]]:
    return {
        "cmc": _joint_angle_to_dict(thumb.cmc),
        "mcp": _joint_angle_to_dict(thumb.mcp),
        "ip": _joint_angle_to_dict(thumb.ip),
    }


def _pose_to_dict(pose: HandJointPose) -> dict[str, object]:
    return {
        "thumb": _thumb_to_dict(pose.thumb),
        "index": _finger_to_dict(pose.index),
        "middle": _finger_to_dict(pose.middle),
        "ring": _finger_to_dict(pose.ring),
        "pinky": _finger_to_dict(pose.pinky),
    }


def main() -> None:
    entries: dict[str, object] = {}
    for (group, base_symbol_number), ctor in sorted(_REGISTRY.items()):
        cls = cast(type, ctor)
        base_hex = HAND_GROUP_START[group - 1] + (base_symbol_number - 1)
        fill = min(valid_combinations_for(base_hex).fills)
        instance = ctor(fill=fill, rotation=0)
        pose = instance.get_joint_pose()
        symbol_id = f"01-{group:02d}-{base_symbol_number:03d}"
        entries[symbol_id] = {
            "name": _extract_name(cls),
            **_pose_to_dict(pose),
        }

    if len(entries) != 261:
        raise RuntimeError(f"expected 261 registered Category 1 base symbols, found {len(entries)}")

    output = {
        "_meta": {
            "source": "sign-language-processing/3d-hands-benchmark (MediaPipe v0.10.3 estimates, median of 48 crops)",
            "method": "per-joint flexion = angle between consecutive bone vectors (wrist->mcp->pip->dip->tip)",
            "limitation": (
                "MediaPipe pose estimate on real photos, NOT verified motion capture "
                "(the benchmark itself makes no such claim either); abduction values are "
                "still estimated, not measured, from this dataset"
            ),
            "count": len(entries),
            "generated_by": "scripts/export_joint_poses.py",
        },
        **entries,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {len(entries)} entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
