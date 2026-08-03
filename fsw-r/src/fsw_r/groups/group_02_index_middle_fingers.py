"""Symbol Group 2 -- Index & Middle Fingers.

ASL handshape "2": index and middle fingers extended straight (spread
apart), ring and pinky curled into the fist, thumb curled/tucked in
against the palm (NOT extended -- only Groups 3, 5, and 10 have the thumb
extended, confirmed by checking real symbol photos).

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-02-001"
("Index Middle"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats
(MediaPipe's own estimate on a real photo, not verified mocap ground
truth). `abduction` (finger spread) isn't measured by this method -- it's
still a guess, kept from the original baseline.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup2IndexMiddleFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(48), mcp=JointAngle(43), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(11, abduction=10), pip=JointAngle(2), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(19, abduction=10), pip=JointAngle(4), dip=JointAngle(10)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(115), dip=JointAngle(26)),
            pinky=FingerPose(mcp=JointAngle(53), pip=JointAngle(113), dip=JointAngle(19)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=2, base_symbol_number=1)
class BaseSymbol01_02_001_IndexMiddle(SymbolGroup2IndexMiddleFingers):
    """01-02-001 "Index Middle" -- base symbol 1 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
