"""3D renderer. Depends only on FSWHandRenderable and HandRigProvider (both
abstract) -- adding a new Hands group/base symbol never requires touching
this file. Takes ``FSWHandRenderable`` specifically, not the generic
``FSWRenderableSymbol`` marker -- this renderer only knows how to draw a
hand (wrist orientation + joint pose), so its type signature says so; a
Category 2 (Movement) ``FSWMotionRenderable`` symbol is a type error here,
not a runtime ``isinstance`` branch. A future movement renderer would be
its own class taking ``FSWMotionRenderable``, not a branch added to this
one.

A left hand is not a right hand rotated by some angle -- it is a different
chirality (mirror image). So this renderer never mirrors via a rotation
operator: it asks HandRigProvider for the rig matching the symbol's
hand_side (two genuinely distinct rigs/meshes) and only then applies wrist
orientation + joint pose to that rig.

``hand_side`` can be ``None`` (``FSWBaseSymbol.hand_side`` is now abstract
and per-category, see its docstring -- not every category encodes a hand at
all). No category implemented so far actually returns ``None`` -- this is
a defensive branch for when one does, so it fails with a clear message
instead of ``rig_provider.get_rig(None)`` silently doing something
undefined. TODO: once a category needs "both hands" (Category 2's ``fill``
partially correlates with hand but also has a "both" value, per the corpus
note in ``FSWBaseSymbol.hand_side``), ``HandSide`` will need a ``BOTH``
member and this renderer will need real handling for it, not just this
``None`` guard.
"""

from __future__ import annotations

from typing import Protocol

from scipy.spatial.transform import Rotation

from fsw_r.core.renderable_symbol import FSWHandRenderable
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

    def render(self, symbol: FSWHandRenderable) -> None:
        if symbol.hand_side is None:
            raise ValueError(
                f"{symbol.symbol_id} (category {symbol.category}) doesn't encode a hand_side "
                f"-- HandMeshRenderer3D can't pick a rig for it"
            )
        rig = self._rig_provider.get_rig(symbol.hand_side)
        rig.apply_wrist_orientation(symbol.get_wrist_orientation())
        rig.apply_joint_pose(symbol.get_joint_pose())
