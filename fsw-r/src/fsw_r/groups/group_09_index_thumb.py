"""Symbol Group 9 -- Index & Thumb.

Group theme is "Index & Thumb", but base symbol 1 ("Middle Ring Baby") does
not itself involve the index finger or thumb -- confirmed against the real
symbol photo at
https://www.signwriting.org/lessons/iswa/group09/01-09-001-01.html: middle,
ring, and pinky (baby) fingers extended straight, index finger curled,
thumb curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-09-001"
("Middle Ring Baby"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup9IndexThumb(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(43), mcp=JointAngle(56), ip=JointAngle(45)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(89), dip=JointAngle(22)),
            middle=FingerPose(mcp=JointAngle(17), pip=JointAngle(12), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(13), pip=JointAngle(2), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(6), pip=JointAngle(1), dip=JointAngle(6)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=9, base_symbol_number=1)
class BaseSymbol01_09_001_MiddleRingBaby(SymbolGroup9IndexThumb):
    """01-09-001 "Middle Ring Baby" -- base symbol 1 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
