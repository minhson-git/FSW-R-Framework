"""3D renderer. Depends only on FSWRenderableSymbol and HandRigProvider
(both abstract) -- adding a new group or base symbol never requires
touching this file.

A left hand is not a right hand rotated by some angle -- it is a different
chirality (mirror image). So this renderer never mirrors via a rotation
operator: it asks HandRigProvider for the rig matching the symbol's
hand_side (two genuinely distinct rigs/meshes) and only then applies wrist
orientation + joint pose to that rig.

This renderer only handles Category 1 (Hands). Other categories have their
own pose types and their own renderers (a facial-expression blend-shape is
not a hand joint pose) -- so a non-hand symbol routed here fails loudly with
a clear message rather than via a missing ``get_joint_pose()`` attribute.
The category dispatch that decides which renderer a symbol goes to lives
above this class (in ``fsw-r-viz``); this ``isinstance`` check is the
last-line guard. TODO: once a category needs "both hands" (Category 2's
``fill`` partially correlates with hand but also has a "both" value, per the
corpus note in ``FSWBaseSymbol.hand_side``), ``HandSide`` will need a
``BOTH`` member and hand rendering will need real handling for it.
"""

from __future__ import annotations

from typing import Protocol

from scipy.spatial.transform import Rotation

from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import HandJointPose, HandSide


class HandSkeleton(Protocol):
    def apply_wrist_orientation(self, rotation: Rotation) -> None: ...
    def apply_joint_pose(self, pose: HandJointPose) -> None: ...


class HandRigProvider(Protocol):
    """Returns the rig (mesh/skeleton) matching hand_side -- two separate
    rigs, not one rig mirrored via a rotation operator."""

    def get_rig(self, hand_side: HandSide) -> HandSkeleton: ...


class HandMeshRenderer3D:
    def __init__(self, rig_provider: HandRigProvider) -> None:
        self._rig_provider = rig_provider

    def render(self, symbol: FSWRenderableSymbol) -> None:
        if not isinstance(symbol, HandSymbol):
            raise ValueError(
                f"{symbol.symbol_id} (category {symbol.category}) is not a hand symbol "
                f"-- HandMeshRenderer3D only renders Category 1 (Hands)"
            )
        rig = self._rig_provider.get_rig(symbol.hand_side)
        rig.apply_wrist_orientation(symbol.get_wrist_orientation())
        rig.apply_joint_pose(symbol.get_joint_pose())
