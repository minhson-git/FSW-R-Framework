"""The Category 4 (facial expression) instance of the generic
``PoseTable`` -- the face analogue of ``pose_table.py``'s
``HAND_POSE_TABLE``.

Two structural differences from the hand table, both driven by how ISWA
encodes faces (see PHASE4_PLAN.md):

1. The value type is ``dict[int, FaceExpressionPose]`` (fill -> pose), not a
   single pose. For a hand, ``fill`` only rotates the wrist (a formula) and
   the joint pose is fill-independent; for a face, ``fill`` changes the
   expression itself, so the pose is keyed by ``(base_hex, fill)``.
2. It is intentionally partial. Only the authored facial symbols are
   present -- ``registry.py``'s Category 4 dispatch checks membership here
   and raises a clear "not yet supported" for the rest (Head movement paths,
   un-authored groups), rather than pretending an un-authored symbol exists.

``PoseTable`` itself is unchanged -- its class body never mentions
``FaceExpressionPose``; the parse callback below supplies the type.
"""

from __future__ import annotations

from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.pose_table import PoseTable, _load_name_table

# Authored facial-expression base symbols so far: Group 25 (Mouth/Lips) 27
# shape symbols (0x33b-0x355) + Group 24 (Cheeks/Nose) 7 deformation symbols.
# Non-deformation symbols (Group 24 airflow/breath/ears, the Group 25/24
# annotation marks) are deferred -- see data/face_expression_poses.json's
# _meta "deferred" list and scripts/gen_face_poses.py.
EXPECTED_FACE_SYMBOL_COUNT = 34


def _parse_face_expression(key: str, entry: dict[str, object]) -> dict[int, FaceExpressionPose]:
    """Build the ``fill -> FaceExpressionPose`` map for one base symbol from
    its JSON entry's ``fills`` object (keys are decimal fill strings)."""
    symbol_id = entry.get("symbol_id")
    label = symbol_id if isinstance(symbol_id, str) else f"base 0x{key}"
    fills = entry.get("fills")
    if not isinstance(fills, dict) or not fills:
        raise ValueError(f"{label}: missing or empty 'fills' in face_expression_poses.json")

    by_fill: dict[int, FaceExpressionPose] = {}
    for fill_key, raw_pose in fills.items():
        if not isinstance(raw_pose, dict):
            raise ValueError(f"{label}: fill {fill_key} is not an object of blend-shape weights")
        # FaceExpressionPose validates blend-shape names / ranges itself.
        by_fill[int(fill_key)] = FaceExpressionPose(blendshapes={str(n): float(w) for n, w in raw_pose.items()})
    return by_fill


FACE_POSE_TABLE: PoseTable[dict[int, FaceExpressionPose]] = PoseTable(
    "face_expression_poses.json", _parse_face_expression, expected_count=EXPECTED_FACE_SYMBOL_COUNT
)
FACE_NAME_TABLE: dict[int, str] = _load_name_table("face_expression_poses.json")
