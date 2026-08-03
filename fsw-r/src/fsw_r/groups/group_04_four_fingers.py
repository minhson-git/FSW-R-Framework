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


# 01-04-002 "Four Fingers Bent"
@register_symbol(group=4, base_symbol_number=2)
class BaseSymbol01_04_002_FourFingersBent(SymbolGroup4FourFingers):
    """01-04-002 "Four Fingers Bent" -- base symbol 2 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(83), ip=JointAngle(27)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(59), dip=JointAngle(59)),
            middle=FingerPose(mcp=JointAngle(13), pip=JointAngle(50), dip=JointAngle(64)),
            ring=FingerPose(mcp=JointAngle(17), pip=JointAngle(40), dip=JointAngle(91)),
            pinky=FingerPose(mcp=JointAngle(24), pip=JointAngle(21), dip=JointAngle(89)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-04-003 "Four Fingers Hinge"
@register_symbol(group=4, base_symbol_number=3)
class BaseSymbol01_04_003_FourFingersHinge(SymbolGroup4FourFingers):
    """01-04-003 "Four Fingers Hinge" -- base symbol 3 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(63), ip=JointAngle(49)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(19), dip=JointAngle(1)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(19), dip=JointAngle(7)),
            ring=FingerPose(mcp=JointAngle(30), pip=JointAngle(12), dip=JointAngle(7)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(7), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-04-004 "Four Fingers Unit"
@register_symbol(group=4, base_symbol_number=4)
class BaseSymbol01_04_004_FourFingersUnit(SymbolGroup4FourFingers):
    """01-04-004 "Four Fingers Unit" -- base symbol 4 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(62), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(11), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(11), pip=JointAngle(12), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(5), pip=JointAngle(14), dip=JointAngle(1)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(10), dip=JointAngle(3)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-04-005 "Four Fingers Unit Split"
@register_symbol(group=4, base_symbol_number=5)
class BaseSymbol01_04_005_FourFingersUnitSplit(SymbolGroup4FourFingers):
    """01-04-005 "Four Fingers Unit Split" -- base symbol 5 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(48), mcp=JointAngle(61), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(15), pip=JointAngle(9), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(4), pip=JointAngle(10), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(11), pip=JointAngle(9), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(2), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-04-006 "Four Fingers Unit Claw"
@register_symbol(group=4, base_symbol_number=6)
class BaseSymbol01_04_006_FourFingersUnitClaw(SymbolGroup4FourFingers):
    """01-04-006 "Four Fingers Unit Claw" -- base symbol 6 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(68), ip=JointAngle(43)),
            index=FingerPose(mcp=JointAngle(32), pip=JointAngle(87), dip=JointAngle(49)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(99), dip=JointAngle(41)),
            ring=FingerPose(mcp=JointAngle(21), pip=JointAngle(89), dip=JointAngle(52)),
            pinky=FingerPose(mcp=JointAngle(24), pip=JointAngle(61), dip=JointAngle(75)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-04-007 "Four Fingers Unit Bent"
@register_symbol(group=4, base_symbol_number=7)
class BaseSymbol01_04_007_FourFingersUnitBent(SymbolGroup4FourFingers):
    """01-04-007 "Four Fingers Unit Bent" -- base symbol 7 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(69), ip=JointAngle(39)),
            index=FingerPose(mcp=JointAngle(38), pip=JointAngle(128), dip=JointAngle(11)),
            middle=FingerPose(mcp=JointAngle(26), pip=JointAngle(150), dip=JointAngle(14)),
            ring=FingerPose(mcp=JointAngle(20), pip=JointAngle(163), dip=JointAngle(13)),
            pinky=FingerPose(mcp=JointAngle(17), pip=JointAngle(156), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-04-008 "Four Fingers Unit Hinge"
@register_symbol(group=4, base_symbol_number=8)
class BaseSymbol01_04_008_FourFingersUnitHinge(SymbolGroup4FourFingers):
    """01-04-008 "Four Fingers Unit Hinge" -- base symbol 8 of Group 4."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=4, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(47), mcp=JointAngle(67), ip=JointAngle(33)),
            index=FingerPose(mcp=JointAngle(98), pip=JointAngle(7), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(83), pip=JointAngle(4), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(66), pip=JointAngle(5), dip=JointAngle(19)),
            pinky=FingerPose(mcp=JointAngle(51), pip=JointAngle(1), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
