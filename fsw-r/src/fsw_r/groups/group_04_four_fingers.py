"""Symbol Group 4 -- Four Fingers.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group04/01-04-001-01.html: index,
middle, ring, and pinky all extended straight and spread apart, thumb
curled/tucked into the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-04-001"
("Four Fingers"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
`abduction` (finger spread) isn't measured by this method -- still a
guess, kept from the original baseline.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup4FourFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(42), mcp=JointAngle(78), ip=JointAngle(22)),
            index=FingerPose(mcp=JointAngle(4, abduction=8), pip=JointAngle(7), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(11, abduction=8), pip=JointAngle(9), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(7, abduction=8), pip=JointAngle(9), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(15, abduction=8), pip=JointAngle(0), dip=JointAngle(6)),
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
