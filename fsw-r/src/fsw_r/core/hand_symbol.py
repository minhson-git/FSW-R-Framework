"""A single class for all 261 Category 1 (Hands) base symbols.

Before this, each base symbol was its own ``FSWRenderableSymbol`` subclass
(``groups/group_0N_*.py``) whose only real difference from its siblings was
15 joint-angle numbers -- 251 of 261 overrode ``get_joint_pose()`` and every
one of the 261 had a ``get_wrist_orientation()`` that just returned
``self._default_wrist_orientation()``. That's data pretending to be
behavior; see PROGRESS.md's "Refactor tang Group sang data-driven" entry.
``HandSymbol`` replaces all 261 classes: it looks up its own pose in
``core/pose_table.py`` by ``base_hex`` instead of hardcoding it.
"""

from __future__ import annotations

from scipy.spatial.transform import Rotation

from fsw_r.core.pose_table import HAND_NAME_TABLE, HAND_POSE_TABLE
from fsw_r.core.renderable_symbol import FSWHandRenderable
from fsw_r.core.types import HandJointPose, HandSide


class HandSymbol(FSWHandRenderable):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide:
        """ISWA rule for Category 1 (Hands) specifically: rotation 0-7 ->
        RIGHT, 8-15 -> LEFT (mirror half) -- confirmed against
        ``signwriting.utils.mirror.mirror.py``'s own docstring. This is a
        pure function of ``rotation``, identical for every Hands symbol --
        it must NOT be assumed to hold for other categories (see
        ``FSWBaseSymbol.hand_side``'s docstring for the corpus evidence
        that Category 2 doesn't follow this rule)."""
        return HandSide.LEFT if self.rotation >= 8 else HandSide.RIGHT

    @property
    def name(self) -> str:
        """The base symbol's real name (e.g. "Index"), useful for demos and
        debugging -- not used by rendering itself."""
        return HAND_NAME_TABLE[self.base_hex]

    def get_joint_pose(self) -> HandJointPose:
        return HAND_POSE_TABLE[self.base_hex]

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
