"""A single class for all 261 Category 1 (Hands) base symbols.

Before this, each base symbol was its own ``FSWRenderableSymbol`` subclass
(``groups/group_0N_*.py``) whose only real difference from its siblings was
15 joint-angle numbers -- 251 of 261 overrode ``get_joint_pose()`` and every
one of the 261 had a ``get_wrist_orientation()`` that just returned
``self._default_wrist_orientation()``. That's data pretending to be
behavior; see PROGRESS.md's "Refactor tang Group sang data-driven" entry.
``HandSymbol`` replaces all 261 classes: it looks up its own pose in
``core/pose_table.py`` by ``symbol_id`` instead of hardcoding it.
"""

from __future__ import annotations

from scipy.spatial.transform import Rotation

from fsw_r.core.pose_table import HAND_NAME_TABLE, HAND_POSE_TABLE
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import HandJointPose


class HandSymbol(FSWRenderableSymbol):
    def __init__(self, category: int, group: int, base_symbol_number: int, fill: int, rotation: int) -> None:
        super().__init__(
            category=category,
            group=group,
            base_symbol_number=base_symbol_number,
            fill=fill,
            rotation=rotation,
        )

    @property
    def name(self) -> str:
        """The base symbol's real name (e.g. "Index"), useful for demos and
        debugging -- not used by rendering itself."""
        return HAND_NAME_TABLE[self.symbol_id]

    def get_joint_pose(self) -> HandJointPose:
        return HAND_POSE_TABLE[self.symbol_id]

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
