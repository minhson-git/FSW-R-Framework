"""Symbol Group 1 -- Index Finger.

ASL handshape "1": index finger extended straight, the other three fingers
curled into the fist, thumb curled/tucked in against the palm (NOT
extended out to the side -- confirmed by checking real symbol photos: only
Groups 3, 5, and 10 have the thumb extended).

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-01-001"
("Index"), orientation 1 (fill=0, Palm of Hand/Wall Plane). Per-joint
flexion = angle between consecutive bone vectors (wrist->mcp, mcp->pip,
pip->dip, dip->tip). This is MediaPipe's own pose *estimate* on a real
photo, not verified motion-capture ground truth -- see that repo's README
-- but it's real, photographed data, not an invented number. DIP flexion in
particular looks systematically low for curled fingers (a known weak point
of monocular depth/z estimation at the fingertip); still preferred here
over a hand-picked guess.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import replace

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup1IndexFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(53), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(30), pip=JointAngle(3), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(55), pip=JointAngle(116), dip=JointAngle(23)),
            ring=FingerPose(mcp=JointAngle(55), pip=JointAngle(127), dip=JointAngle(45)),
            pinky=FingerPose(mcp=JointAngle(38), pip=JointAngle(140), dip=JointAngle(30)),
        )

    # Default: base symbols that don't need a distinct pose use the group template as-is.
    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=1, base_symbol_number=1)
class BaseSymbol01_01_001_Index(SymbolGroup1IndexFinger):
    """01-01-001 "Index". `rotation` sweeps which way the extended finger
    points on the page (0=up, 90=side, 180=down, ...); `fill` is the "Six
    Palm Facings" -- which side of the hand shows (Palm/Side/Back) and
    which plane the arm reaches in (Wall/Floor). The joint pose itself
    never changes with either."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        # TODO: replace with the real logic already present in the system's FSWBaseSymbol.
        return self._default_wrist_orientation()


@register_symbol(group=1, base_symbol_number=7)
class BaseSymbol01_01_007_IndexBent(SymbolGroup1IndexFinger):
    """01-01-007 "Index Bent". Illustrates why the default joint template
    lives on the group while the override lives on the base symbol: this
    variant only differs from "Index" in the index finger's flexion.

    The index angles below are real data (same source/method as the group
    docstring), from dataset symbol "01-01-007" -- the other four fingers
    also measured slightly differently there than in "01-01-001" (natural
    photo-to-photo variance, not part of what the symbol actually encodes),
    so this only takes the index finger from that measurement and keeps the
    rest of the pose from the shared group template, matching the ISWA
    definition that "Index Bent" differs only in the index finger.
    """

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        base = self._default_joint_pose()
        bent_index = FingerPose(
            mcp=JointAngle(flexion=32),
            pip=JointAngle(flexion=46),
            dip=JointAngle(flexion=69),
        )
        return replace(base, index=bent_index)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
