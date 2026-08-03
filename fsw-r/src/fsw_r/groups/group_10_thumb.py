"""Symbol Group 10 -- Thumb.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group10/01-10-001-01.html: index,
middle, ring, and pinky all curled into the fist, thumb extended out to
the side.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-10-001"
("Thumb"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
Thumb `abduction` (how far it splays from the hand) isn't measured by this
method -- still a guess, kept from the original baseline.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup10Thumb(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31, abduction=30), mcp=JointAngle(5), ip=JointAngle(33)),
            index=FingerPose(mcp=JointAngle(53), pip=JointAngle(122), dip=JointAngle(12)),
            middle=FingerPose(mcp=JointAngle(42), pip=JointAngle(129), dip=JointAngle(36)),
            ring=FingerPose(mcp=JointAngle(36), pip=JointAngle(147), dip=JointAngle(43)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(167), dip=JointAngle(26)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=10, base_symbol_number=1)
class BaseSymbol01_10_001_Thumb(SymbolGroup10Thumb):
    """01-10-001 "Thumb" -- base symbol 1 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
