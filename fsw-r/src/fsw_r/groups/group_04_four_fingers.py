"""Symbol Group 4 -- Four Fingers.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group04/01-04-001-01.html: index,
middle, ring, and pinky all extended straight and spread apart, thumb
curled/tucked into the palm.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup4FourFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        straight_spread = FingerPose(
            mcp=JointAngle(flexion=0, abduction=8),
            pip=JointAngle(flexion=0),
            dip=JointAngle(flexion=0),
        )
        thumb_curled = ThumbPose(cmc=JointAngle(70), mcp=JointAngle(80), ip=JointAngle(60))
        return HandJointPose(
            thumb=thumb_curled,
            index=straight_spread,
            middle=straight_spread,
            ring=straight_spread,
            pinky=straight_spread,
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=4, base_symbol_number=1)
class BaseSymbol01_04_001_FourFingers(SymbolGroup4FourFingers):
    """01-04-001 "Four Fingers" -- base symbol 1 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
