"""Symbol Group 8 -- Middle Finger.

Group theme is "Middle Finger", but base symbol 1 ("Index Ring Baby") does
not itself involve the middle finger -- confirmed against the real symbol
photo at https://www.signwriting.org/lessons/iswa/group08/01-08-001-01.html:
index, ring, and pinky (baby) fingers extended straight, middle finger
curled, thumb curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-08-001"
("Index Ring Baby"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup8MiddleFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(50), mcp=JointAngle(41), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(22), pip=JointAngle(16), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(54), pip=JointAngle(104), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(31), pip=JointAngle(25), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(13), pip=JointAngle(5), dip=JointAngle(14)),
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
