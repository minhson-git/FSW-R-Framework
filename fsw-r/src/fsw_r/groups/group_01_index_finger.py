"""Symbol Group 1 -- Index Finger.

ASL handshape "1": index finger extended straight, the other three fingers
curled into the fist, thumb curled/tucked in against the palm (NOT
extended out to the side -- confirmed by checking real symbol photos: only
Groups 3, 5, and 10 have the thumb extended).

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import replace

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup1IndexFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        curled_into_fist = FingerPose(
            mcp=JointAngle(flexion=90),
            pip=JointAngle(flexion=100),
            dip=JointAngle(flexion=80),
        )
        straight = FingerPose(
            mcp=JointAngle(flexion=0),
            pip=JointAngle(flexion=0),
            dip=JointAngle(flexion=0),
        )
        thumb_curled = ThumbPose(cmc=JointAngle(70), mcp=JointAngle(80), ip=JointAngle(60))
        return HandJointPose(
            thumb=thumb_curled,
            index=straight,
            middle=curled_into_fist,
            ring=curled_into_fist,
            pinky=curled_into_fist,
        )

    # Default: base symbols that don't need a distinct pose use the group template as-is.
    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=1, base_symbol_number=1)
class BaseSymbol01_01_001_Index(SymbolGroup1IndexFinger):
    """01-01-001 "Index". `rotation` sweeps which way the extended finger
    points on the page (0=up, 90=side, 180=down, ...); `fill` is the "Six
    Palm Facings" -- which side of the hand shows (Palm/Side/Back) and
    which plane the arm reaches in (Wall/Floor). The joint pose itself
    never changes with either."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        # TODO: replace with the real logic already present in the system's FSWBaseSymbol.
        return self._default_wrist_orientation()


@register_symbol(group=1, base_symbol_number=7)
class BaseSymbol01_01_007_IndexBent(SymbolGroup1IndexFinger):
    """01-01-007 "Index Bent". Illustrates why the default joint template
    lives on the group while the override lives on the base symbol: this
    variant only differs from "Index" in the index finger's PIP flexion."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        base = self._default_joint_pose()
        bent_index = FingerPose(
            mcp=JointAngle(flexion=0),
            pip=JointAngle(flexion=90),
            dip=JointAngle(flexion=0),
        )
        return replace(base, index=bent_index)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
