"""Symbol Group 8 -- Middle Finger.

Group theme is "Middle Finger", but base symbol 1 ("Index Ring Baby") does
not itself involve the middle finger -- confirmed against the real symbol
photo at https://www.signwriting.org/lessons/iswa/group08/01-08-001-01.html:
index, ring, and pinky (baby) fingers extended straight, middle finger
curled, thumb curled/tucked against the palm.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup8MiddleFinger(FSWRenderableSymbol, ABC):
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
            ring=straight,
            pinky=straight,
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=8, base_symbol_number=1)
class BaseSymbol01_08_001_IndexRingBaby(SymbolGroup8MiddleFinger):
    """01-08-001 "Index Ring Baby" -- base symbol 1 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
