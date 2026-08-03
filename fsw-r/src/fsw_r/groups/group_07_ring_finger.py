"""Symbol Group 7 -- Ring Finger.

Group theme is "Ring Finger", but base symbol 1 ("Index Middle Baby") does
not itself involve the ring finger -- confirmed against the real symbol
photo at https://www.signwriting.org/lessons/iswa/group07/01-07-001-01.html:
index, middle, and pinky (baby) fingers extended straight, ring finger
curled, thumb curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-07-001"
("Index Middle Baby"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup7RingFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(49), mcp=JointAngle(49), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(16), pip=JointAngle(6), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(19), pip=JointAngle(12), dip=JointAngle(7)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(118), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(7), dip=JointAngle(13)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=7, base_symbol_number=1)
class BaseSymbol01_07_001_IndexMiddleBaby(SymbolGroup7RingFinger):
    """01-07-001 "Index Middle Baby" -- base symbol 1 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
