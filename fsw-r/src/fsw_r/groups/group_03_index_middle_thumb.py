"""Symbol Group 3 -- Index, Middle, Thumb.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group03/01-03-001-01.html: index
and middle fingers extended straight together, thumb extended out to the
side, ring and pinky curled into the fist.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-03-001"
("Index Middle Thumb"), orientation 1 (fill=0, Palm of Hand/Wall Plane).
See group_01_index_finger.py's docstring for the exact method and caveats.
Thumb `abduction` (how far it splays from the hand) isn't measured by this
method -- still a guess, kept from the original baseline.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup3IndexMiddleThumb(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(22, abduction=20), mcp=JointAngle(3), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(11), pip=JointAngle(2), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(17), pip=JointAngle(3), dip=JointAngle(7)),
            ring=FingerPose(mcp=JointAngle(45), pip=JointAngle(120), dip=JointAngle(17)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(119), dip=JointAngle(16)),
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
