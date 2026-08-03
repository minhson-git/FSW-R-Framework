"""Symbol Group 3 -- Index, Middle, Thumb.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group03/01-03-001-01.html: index
and middle fingers extended straight together, thumb extended out to the
side, ring and pinky curled into the fist.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup3IndexMiddleThumb(FSWRenderableSymbol, ABC):
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
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40, abduction=20), mcp=JointAngle(10), ip=JointAngle(0)),
            index=straight,
            middle=straight,
            ring=curled_into_fist,
            pinky=curled_into_fist,
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=3, base_symbol_number=1)
class BaseSymbol01_03_001_IndexMiddleThumb(SymbolGroup3IndexMiddleThumb):
    """01-03-001 "Index Middle Thumb" -- base symbol 1 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
