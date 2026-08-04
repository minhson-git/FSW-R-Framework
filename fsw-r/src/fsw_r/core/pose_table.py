"""``PoseTable`` is a generic, ``base_hex``-keyed, validated pose table --
one instance per ISWA category, each with its own pose type (``PoseT``).
The class body itself never references a concrete pose type like
``HandJointPose``; that's supplied by the ``parse`` callback passed to
``__init__``, so a future category (e.g. Movement, with a "motion path"
pose type instead of joint angles) only needs its own ``PoseTable(...)``
instance + parse function, not a new table implementation.

``HAND_POSE_TABLE`` below is the Category 1 (Hands) instance, loading
``data/hand_joint_poses.json`` -- the real, dataset-derived joint pose for
every one of Category 1's 261 base symbols. This is data, not behavior:
every base symbol used to be its own Python class whose only real
difference from its siblings was 15 numbers (see PROGRESS.md's "Refactor
tang Group sang data-driven" entry for the measurements that led here).
``core/hand_symbol.py``'s single ``HandSymbol`` class looks angles up here
instead, by ``base_hex`` (the JSON's top-level keys, e.g. ``"100"`` for
0x100 -- ``symbol_id`` is kept as a field *inside* each entry for human
readability and cross-checking, never as the lookup key itself).

Fails fast at construction time (not at first render) if the JSON is
missing an entry or a field -- a malformed data file should never surface
as a mysterious ``AttributeError`` deep in rendering code.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Callable, Generic, TypeVar

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose

PoseT = TypeVar("PoseT")


class PoseTable(Generic[PoseT]):
    """A validated, ``base_hex``-keyed pose table for one ISWA category.
    Loads and validates its JSON resource once, at construction time."""

    def __init__(
        self,
        resource: str,
        parse: Callable[[str, dict[str, object]], PoseT],
        expected_count: int,
    ) -> None:
        raw_text = resources.files("fsw_r.data").joinpath(resource).read_text(encoding="utf-8")
        raw = json.loads(raw_text)

        table: dict[int, PoseT] = {}
        for key, entry in raw.items():
            if key == "_meta":
                continue
            table[int(key, 16)] = parse(key, entry)

        if len(table) != expected_count:
            raise ValueError(f"{resource} has {len(table)} entries, expected {expected_count}")
        self._table = table

    def __getitem__(self, base_hex: int) -> PoseT:
        return self._table[base_hex]

    def __contains__(self, base_hex: int) -> bool:
        return base_hex in self._table

    def base_hexes(self) -> frozenset[int]:
        return frozenset(self._table)


EXPECTED_SYMBOL_COUNT = 261

_FINGER_JOINTS = ("mcp", "pip", "dip")
_THUMB_JOINTS = ("cmc", "mcp", "ip")


def _entry_label(key: str, entry: dict[str, object]) -> str:
    """Prefer the human-readable symbol_id for error messages when the
    entry has one; fall back to the raw base_hex key otherwise."""
    symbol_id = entry.get("symbol_id")
    return symbol_id if isinstance(symbol_id, str) else f"base 0x{key}"


def _parse_joint_angle(raw: object, label: str, finger: str, joint: str) -> JointAngle:
    if not isinstance(raw, dict) or "flexion" not in raw:
        raise ValueError(f"{label}: {finger}.{joint} is missing or malformed in hand_joint_poses.json")
    return JointAngle(flexion=raw["flexion"], abduction=raw.get("abduction", 0.0))


def _parse_finger(raw: object, label: str, finger: str) -> FingerPose:
    if not isinstance(raw, dict):
        raise ValueError(f"{label}: {finger} is missing or malformed in hand_joint_poses.json")
    return FingerPose(
        **{joint: _parse_joint_angle(raw.get(joint), label, finger, joint) for joint in _FINGER_JOINTS}
    )


def _parse_thumb(raw: object, label: str) -> ThumbPose:
    if not isinstance(raw, dict):
        raise ValueError(f"{label}: thumb is missing or malformed in hand_joint_poses.json")
    return ThumbPose(
        **{joint: _parse_joint_angle(raw.get(joint), label, "thumb", joint) for joint in _THUMB_JOINTS}
    )


def _parse_hand_joint_pose(key: str, entry: dict[str, object]) -> HandJointPose:
    label = _entry_label(key, entry)
    return HandJointPose(
        thumb=_parse_thumb(entry.get("thumb"), label),
        index=_parse_finger(entry.get("index"), label, "index"),
        middle=_parse_finger(entry.get("middle"), label, "middle"),
        ring=_parse_finger(entry.get("ring"), label, "ring"),
        pinky=_parse_finger(entry.get("pinky"), label, "pinky"),
    )


def _load_name_table(resource: str) -> dict[int, str]:
    raw_text = resources.files("fsw_r.data").joinpath(resource).read_text(encoding="utf-8")
    raw = json.loads(raw_text)
    names: dict[int, str] = {}
    for key, entry in raw.items():
        if key == "_meta":
            continue
        name = entry.get("name")
        label = _entry_label(key, entry)
        if not isinstance(name, str) or not name:
            raise ValueError(f"{label}: missing or malformed 'name' in {resource}")
        names[int(key, 16)] = name
    return names


HAND_POSE_TABLE: PoseTable[HandJointPose] = PoseTable(
    "hand_joint_poses.json", _parse_hand_joint_pose, expected_count=EXPECTED_SYMBOL_COUNT
)
HAND_NAME_TABLE: dict[int, str] = _load_name_table("hand_joint_poses.json")
