"""3D renderer. Depends only on FSWRenderableSymbol and HandRigProvider
(both abstract) -- adding a new group or base symbol never requires
touching this file.

A left hand is not a right hand rotated by some angle -- it is a different
chirality (mirror image). So this renderer never mirrors via a rotation
operator: it asks HandRigProvider for the rig matching the symbol's
hand_side (two genuinely distinct rigs/meshes) and only then applies wrist
orientation + joint pose to that rig.
"""

from __future__ import annotations

from typing import Protocol

from scipy.spatial.transform import Rotation

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
        rig = self._rig_provider.get_rig(symbol.hand_side)
        rig.apply_wrist_orientation(symbol.get_wrist_orientation())
        rig.apply_joint_pose(symbol.get_joint_pose())
