"""Symbol Group 2 -- Index & Middle Fingers.

ASL handshape "2": index and middle fingers extended straight (spread
apart), ring and pinky curled into the fist, thumb pressed against the side
of the hand.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup2IndexMiddleFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        curled_into_fist = FingerPose(
            mcp=JointAngle(flexion=90),
            pip=JointAngle(flexion=100),
            dip=JointAngle(flexion=80),
        )
        straight_spread = FingerPose(
            mcp=JointAngle(flexion=0, abduction=10),
            pip=JointAngle(flexion=0),
            dip=JointAngle(flexion=0),
        )
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(20), mcp=JointAngle(15), ip=JointAngle(10)),
            index=straight_spread,
            middle=straight_spread,
            ring=curled_into_fist,
            pinky=curled_into_fist,
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=2, base_symbol_number=1)
class BaseSymbol01_02_001_IndexMiddle(SymbolGroup2IndexMiddleFingers):
    """01-02-001 "Index Middle" -- base symbol 1 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return Rotation.from_euler("z", self._rotation_angle_degrees(), degrees=True)
