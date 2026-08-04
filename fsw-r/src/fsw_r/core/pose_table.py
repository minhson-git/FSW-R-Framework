"""Loads ``data/hand_joint_poses.json`` -- the real, dataset-derived joint
pose for every one of Category 1 (Hands)'s 261 base symbols -- into
``HAND_POSE_TABLE``, a ``dict[str, HandJointPose]`` keyed by ``symbol_id``
(e.g. ``"01-01-001"``). ``HAND_NAME_TABLE`` holds each symbol's real name
(e.g. ``"Index"``) alongside it.

This is data, not behavior: every base symbol used to be its own Python
class whose only real difference from its siblings was 15 numbers (see
PROGRESS.md's "Refactor tang Group sang data-driven" entry for the
measurements that led here). ``core/hand_symbol.py``'s single ``HandSymbol``
class looks angles up here instead.

Fails fast at import time (not at first render) if the JSON is missing an
entry or a field -- a malformed data file should never surface as a
mysterious ``AttributeError`` deep in rendering code.
"""

from __future__ import annotations

import json
from importlib import resources

from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose

EXPECTED_SYMBOL_COUNT = 261

_FINGER_JOINTS = ("mcp", "pip", "dip")
_THUMB_JOINTS = ("cmc", "mcp", "ip")


def _parse_joint_angle(raw: object, symbol_id: str, finger: str, joint: str) -> JointAngle:
    if not isinstance(raw, dict) or "flexion" not in raw:
        raise ValueError(f"{symbol_id}: {finger}.{joint} is missing or malformed in hand_joint_poses.json")
    return JointAngle(flexion=raw["flexion"], abduction=raw.get("abduction", 0.0))


def _parse_finger(raw: object, symbol_id: str, finger: str) -> FingerPose:
    if not isinstance(raw, dict):
        raise ValueError(f"{symbol_id}: {finger} is missing or malformed in hand_joint_poses.json")
    return FingerPose(
        **{joint: _parse_joint_angle(raw.get(joint), symbol_id, finger, joint) for joint in _FINGER_JOINTS}
    )


def _parse_thumb(raw: object, symbol_id: str) -> ThumbPose:
    if not isinstance(raw, dict):
        raise ValueError(f"{symbol_id}: thumb is missing or malformed in hand_joint_poses.json")
    return ThumbPose(
        **{joint: _parse_joint_angle(raw.get(joint), symbol_id, "thumb", joint) for joint in _THUMB_JOINTS}
    )


def _parse_pose(symbol_id: str, raw: dict[str, object]) -> HandJointPose:
    return HandJointPose(
        thumb=_parse_thumb(raw.get("thumb"), symbol_id),
        index=_parse_finger(raw.get("index"), symbol_id, "index"),
        middle=_parse_finger(raw.get("middle"), symbol_id, "middle"),
        ring=_parse_finger(raw.get("ring"), symbol_id, "ring"),
        pinky=_parse_finger(raw.get("pinky"), symbol_id, "pinky"),
    )


def _parse_name(symbol_id: str, raw: dict[str, object]) -> str:
    name = raw.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError(f"{symbol_id}: missing or malformed 'name' in hand_joint_poses.json")
    return name


def _load_tables() -> tuple[dict[str, HandJointPose], dict[str, str]]:
    raw_text = resources.files("fsw_r.data").joinpath("hand_joint_poses.json").read_text(encoding="utf-8")
    raw = json.loads(raw_text)

    poses: dict[str, HandJointPose] = {}
    names: dict[str, str] = {}
    for symbol_id, entry in raw.items():
        if symbol_id == "_meta":
            continue
        poses[symbol_id] = _parse_pose(symbol_id, entry)
        names[symbol_id] = _parse_name(symbol_id, entry)

    if len(poses) != EXPECTED_SYMBOL_COUNT:
        raise ValueError(
            f"hand_joint_poses.json has {len(poses)} entries, expected {EXPECTED_SYMBOL_COUNT}"
        )
    return poses, names


HAND_POSE_TABLE, HAND_NAME_TABLE = _load_tables()
