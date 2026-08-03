"""Symbol Group 5 -- Five Fingers.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group05/01-05-001-01.html: all
five fingers (including thumb) extended straight and spread apart -- an
open hand.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup5FiveFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        straight_spread = FingerPose(
            mcp=JointAngle(flexion=0, abduction=8),
            pip=JointAngle(flexion=0),
            dip=JointAngle(flexion=0),
        )
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45, abduction=25), mcp=JointAngle(5), ip=JointAngle(0)),
            index=straight_spread,
            middle=straight_spread,
            ring=straight_spread,
            pinky=straight_spread,
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=5, base_symbol_number=1)
class BaseSymbol01_05_001_FiveFingersSpread(SymbolGroup5FiveFingers):
    """01-05-001 "Five Fingers Spread" -- base symbol 1 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
