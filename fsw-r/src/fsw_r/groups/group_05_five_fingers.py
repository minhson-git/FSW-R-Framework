"""Symbol Group 5 -- Five Fingers.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group05/01-05-001-01.html: all
five fingers (including thumb) extended straight and spread apart -- an
open hand.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-05-001"
("Five Fingers Spread"), orientation 1 (fill=0, Palm of Hand/Wall Plane).
See group_01_index_finger.py's docstring for the exact method and caveats.
`abduction` (finger spread) isn't measured by this method -- still a
guess, kept from the original baseline.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup5FiveFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26, abduction=25), mcp=JointAngle(4), ip=JointAngle(26)),
            index=FingerPose(mcp=JointAngle(8, abduction=8), pip=JointAngle(8), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(5, abduction=8), pip=JointAngle(8), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(9, abduction=8), pip=JointAngle(4), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(9, abduction=8), pip=JointAngle(5), dip=JointAngle(6)),
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
