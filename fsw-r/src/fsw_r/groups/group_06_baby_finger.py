"""Symbol Group 6 -- Baby Finger.

Group theme is "Baby Finger" (pinky), but base symbol 1 ("Index Middle
Ring") is not itself a pinky-only shape -- ISWA groups don't always start
with their own namesake finger. Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group06/01-06-001-01.html: index,
middle, and ring fingers extended straight together, pinky curled, thumb
curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-06-001"
("Index Middle Ring"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats. The
real data shows ring only partially bent (not fully straight like
index/middle, not fully curled like pinky) -- kept as measured, rather than
forced into a straight/curled binary.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup6BabyFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(59), mcp=JointAngle(58), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(12), pip=JointAngle(6), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(6), pip=JointAngle(14), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(21), pip=JointAngle(20), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(38), pip=JointAngle(116), dip=JointAngle(19)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=6, base_symbol_number=1)
class BaseSymbol01_06_001_IndexMiddleRing(SymbolGroup6BabyFinger):
    """01-06-001 "Index Middle Ring" -- base symbol 1 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
