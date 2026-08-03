"""Symbol Group 6 -- Baby Finger.

Group theme is "Baby Finger" (pinky), but base symbol 1 ("Index Middle
Ring") is not itself a pinky-only shape -- ISWA groups don't always start
with their own namesake finger. Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group06/01-06-001-01.html: index,
middle, and ring fingers extended straight together, pinky curled, thumb
curled/tucked against the palm.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup6BabyFinger(FSWRenderableSymbol, ABC):
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
            middle=straight,
            ring=straight,
            pinky=curled_into_fist,
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=6, base_symbol_number=1)
class BaseSymbol01_06_001_IndexMiddleRing(SymbolGroup6BabyFinger):
    """01-06-001 "Index Middle Ring" -- base symbol 1 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
