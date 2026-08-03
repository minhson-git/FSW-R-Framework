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


# 01-06-002 "Index Middle Ring on Circle"
@register_symbol(group=6, base_symbol_number=2)
class BaseSymbol01_06_002_IndexMiddleRingOnCircle(SymbolGroup6BabyFinger):
    """01-06-002 "Index Middle Ring on Circle" -- base symbol 2 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(52), mcp=JointAngle(55), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(10), pip=JointAngle(7), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(4), pip=JointAngle(16), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(18), dip=JointAngle(7)),
            pinky=FingerPose(mcp=JointAngle(32), pip=JointAngle(77), dip=JointAngle(53)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-003 "Index Middle Ring on Hinge"
@register_symbol(group=6, base_symbol_number=3)
class BaseSymbol01_06_003_IndexMiddleRingOnHinge(SymbolGroup6BabyFinger):
    """01-06-003 "Index Middle Ring on Hinge" -- base symbol 3 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(27), mcp=JointAngle(48), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(8), pip=JointAngle(5), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(6), pip=JointAngle(10), dip=JointAngle(6)),
            ring=FingerPose(mcp=JointAngle(5), pip=JointAngle(15), dip=JointAngle(2)),
            pinky=FingerPose(mcp=JointAngle(23), pip=JointAngle(10), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-004 "Index Middle Ring on Angle"
@register_symbol(group=6, base_symbol_number=4)
class BaseSymbol01_06_004_IndexMiddleRingOnAngle(SymbolGroup6BabyFinger):
    """01-06-004 "Index Middle Ring on Angle" -- base symbol 4 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(49), mcp=JointAngle(30), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(16), pip=JointAngle(5), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(8), pip=JointAngle(19), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(30), pip=JointAngle(21), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(52), pip=JointAngle(25), dip=JointAngle(11)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-005 "Baby Hinge"
@register_symbol(group=6, base_symbol_number=5)
class BaseSymbol01_06_005_BabyHinge(SymbolGroup6BabyFinger):
    """01-06-005 "Baby Hinge" -- base symbol 5 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(7), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(7), pip=JointAngle(10), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(2), pip=JointAngle(12), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(11), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(27), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-006 "Index Middle Ring, Bent"
@register_symbol(group=6, base_symbol_number=6)
class BaseSymbol01_06_006_IndexMiddleRingBent(SymbolGroup6BabyFinger):
    """01-06-006 "Index Middle Ring, Bent" -- base symbol 6 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(47), mcp=JointAngle(55), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(9), pip=JointAngle(40), dip=JointAngle(58)),
            middle=FingerPose(mcp=JointAngle(13), pip=JointAngle(44), dip=JointAngle(42)),
            ring=FingerPose(mcp=JointAngle(33), pip=JointAngle(42), dip=JointAngle(26)),
            pinky=FingerPose(mcp=JointAngle(68), pip=JointAngle(59), dip=JointAngle(29)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-007 "Index Middle Ring, Unit"
@register_symbol(group=6, base_symbol_number=7)
class BaseSymbol01_06_007_IndexMiddleRingUnit(SymbolGroup6BabyFinger):
    """01-06-007 "Index Middle Ring, Unit" -- base symbol 7 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(62), mcp=JointAngle(66), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(9), dip=JointAngle(1)),
            middle=FingerPose(mcp=JointAngle(15), pip=JointAngle(13), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(20), pip=JointAngle(19), dip=JointAngle(11)),
            pinky=FingerPose(mcp=JointAngle(58), pip=JointAngle(94), dip=JointAngle(14)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-008 "Index Middle Ring, Unit Hinge"
@register_symbol(group=6, base_symbol_number=8)
class BaseSymbol01_06_008_IndexMiddleRingUnitHinge(SymbolGroup6BabyFinger):
    """01-06-008 "Index Middle Ring, Unit Hinge" -- base symbol 8 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(51), mcp=JointAngle(52), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(72), pip=JointAngle(45), dip=JointAngle(20)),
            middle=FingerPose(mcp=JointAngle(65), pip=JointAngle(61), dip=JointAngle(36)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(96), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(70), pip=JointAngle(98), dip=JointAngle(29)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-009 "Baby Down"
@register_symbol(group=6, base_symbol_number=9)
class BaseSymbol01_06_009_BabyDown(SymbolGroup6BabyFinger):
    """01-06-009 "Baby Down" -- base symbol 9 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(5), ip=JointAngle(22)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(10), dip=JointAngle(1)),
            middle=FingerPose(mcp=JointAngle(5), pip=JointAngle(8), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(9), dip=JointAngle(11)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(34), dip=JointAngle(59)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-010 "Baby Down, Ripple Straight"
@register_symbol(group=6, base_symbol_number=10)
class BaseSymbol01_06_010_BabyDownRippleStraight(SymbolGroup6BabyFinger):
    """01-06-010 "Baby Down, Ripple Straight" -- base symbol 10 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(12), ip=JointAngle(35)),
            index=FingerPose(mcp=JointAngle(7), pip=JointAngle(6), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(13), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(38), pip=JointAngle(14), dip=JointAngle(8)),
            pinky=FingerPose(mcp=JointAngle(59), pip=JointAngle(19), dip=JointAngle(18)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-011 "Baby Down, Ripple Curved"
@register_symbol(group=6, base_symbol_number=11)
class BaseSymbol01_06_011_BabyDownRippleCurved(SymbolGroup6BabyFinger):
    """01-06-011 "Baby Down, Ripple Curved" -- base symbol 11 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(30), mcp=JointAngle(6), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(9), pip=JointAngle(8), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(18), pip=JointAngle(21), dip=JointAngle(60)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(80), dip=JointAngle(51)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(101), dip=JointAngle(24)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-012 "Baby Down, Others Circle"
@register_symbol(group=6, base_symbol_number=12)
class BaseSymbol01_06_012_BabyDownOthersCircle(SymbolGroup6BabyFinger):
    """01-06-012 "Baby Down, Others Circle" -- base symbol 12 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(46), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(32), pip=JointAngle(74), dip=JointAngle(51)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(101), dip=JointAngle(45)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(138), dip=JointAngle(20)),
            pinky=FingerPose(mcp=JointAngle(29), pip=JointAngle(144), dip=JointAngle(16)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-013 "Baby Up"
@register_symbol(group=6, base_symbol_number=13)
class BaseSymbol01_06_013_BabyUp(SymbolGroup6BabyFinger):
    """01-06-013 "Baby Up" -- base symbol 13 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(51), mcp=JointAngle(54), ip=JointAngle(31)),
            index=FingerPose(mcp=JointAngle(40), pip=JointAngle(132), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(138), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(46), pip=JointAngle(133), dip=JointAngle(23)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(11), dip=JointAngle(10)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-014 "Baby Up On Fist Thumb Under"
@register_symbol(group=6, base_symbol_number=14)
class BaseSymbol01_06_014_BabyUpOnFistThumbUnder(SymbolGroup6BabyFinger):
    """01-06-014 "Baby Up On Fist Thumb Under" -- base symbol 14 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(26), ip=JointAngle(28)),
            index=FingerPose(mcp=JointAngle(45), pip=JointAngle(125), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(40), pip=JointAngle(124), dip=JointAngle(19)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(146), dip=JointAngle(17)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(9), dip=JointAngle(10)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-015 "Baby Up On Circle"
@register_symbol(group=6, base_symbol_number=15)
class BaseSymbol01_06_015_BabyUpOnCircle(SymbolGroup6BabyFinger):
    """01-06-015 "Baby Up On Circle" -- base symbol 15 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(49), ip=JointAngle(31)),
            index=FingerPose(mcp=JointAngle(38), pip=JointAngle(70), dip=JointAngle(66)),
            middle=FingerPose(mcp=JointAngle(28), pip=JointAngle(98), dip=JointAngle(42)),
            ring=FingerPose(mcp=JointAngle(20), pip=JointAngle(96), dip=JointAngle(55)),
            pinky=FingerPose(mcp=JointAngle(10), pip=JointAngle(4), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-016 "Baby Up On Oval"
@register_symbol(group=6, base_symbol_number=16)
class BaseSymbol01_06_016_BabyUpOnOval(SymbolGroup6BabyFinger):
    """01-06-016 "Baby Up On Oval" -- base symbol 16 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(50), mcp=JointAngle(24), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(84), pip=JointAngle(28), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(75), pip=JointAngle(33), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(83), pip=JointAngle(51), dip=JointAngle(39)),
            pinky=FingerPose(mcp=JointAngle(56), pip=JointAngle(37), dip=JointAngle(0)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-017 "Baby Up On Angle"
@register_symbol(group=6, base_symbol_number=17)
class BaseSymbol01_06_017_BabyUpOnAngle(SymbolGroup6BabyFinger):
    """01-06-017 "Baby Up On Angle" -- base symbol 17 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=17, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(52), mcp=JointAngle(43), ip=JointAngle(2)),
            index=FingerPose(mcp=JointAngle(79), pip=JointAngle(15), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(70), pip=JointAngle(34), dip=JointAngle(17)),
            ring=FingerPose(mcp=JointAngle(43), pip=JointAngle(3), dip=JointAngle(11)),
            pinky=FingerPose(mcp=JointAngle(22), pip=JointAngle(5), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-018 "Baby Raised Knuckle"
@register_symbol(group=6, base_symbol_number=18)
class BaseSymbol01_06_018_BabyRaisedKnuckle(SymbolGroup6BabyFinger):
    """01-06-018 "Baby Raised Knuckle" -- base symbol 18 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=18, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(66), ip=JointAngle(36)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(129), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(141), dip=JointAngle(21)),
            ring=FingerPose(mcp=JointAngle(31), pip=JointAngle(151), dip=JointAngle(22)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(166), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-019 "Baby Bent"
@register_symbol(group=6, base_symbol_number=19)
class BaseSymbol01_06_019_BabyBent(SymbolGroup6BabyFinger):
    """01-06-019 "Baby Bent" -- base symbol 19 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=19, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(69), ip=JointAngle(44)),
            index=FingerPose(mcp=JointAngle(61), pip=JointAngle(127), dip=JointAngle(21)),
            middle=FingerPose(mcp=JointAngle(47), pip=JointAngle(144), dip=JointAngle(54)),
            ring=FingerPose(mcp=JointAngle(42), pip=JointAngle(152), dip=JointAngle(31)),
            pinky=FingerPose(mcp=JointAngle(26), pip=JointAngle(11), dip=JointAngle(27)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-020 "Baby Touches Thumb"
@register_symbol(group=6, base_symbol_number=20)
class BaseSymbol01_06_020_BabyTouchesThumb(SymbolGroup6BabyFinger):
    """01-06-020 "Baby Touches Thumb" -- base symbol 20 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=20, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(56), ip=JointAngle(33)),
            index=FingerPose(mcp=JointAngle(46), pip=JointAngle(145), dip=JointAngle(21)),
            middle=FingerPose(mcp=JointAngle(27), pip=JointAngle(160), dip=JointAngle(20)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(167), dip=JointAngle(2)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(27), dip=JointAngle(78)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-021 "Baby Thumb"
@register_symbol(group=6, base_symbol_number=21)
class BaseSymbol01_06_021_BabyThumb(SymbolGroup6BabyFinger):
    """01-06-021 "Baby Thumb" -- base symbol 21 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=21, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(9), ip=JointAngle(31)),
            index=FingerPose(mcp=JointAngle(42), pip=JointAngle(125), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(124), dip=JointAngle(14)),
            ring=FingerPose(mcp=JointAngle(25), pip=JointAngle(143), dip=JointAngle(15)),
            pinky=FingerPose(mcp=JointAngle(8), pip=JointAngle(15), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-022 "Baby Thumb on Hinge"
@register_symbol(group=6, base_symbol_number=22)
class BaseSymbol01_06_022_BabyThumbOnHinge(SymbolGroup6BabyFinger):
    """01-06-022 "Baby Thumb on Hinge" -- base symbol 22 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=22, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(27), mcp=JointAngle(18), ip=JointAngle(32)),
            index=FingerPose(mcp=JointAngle(58), pip=JointAngle(46), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(42), pip=JointAngle(45), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(25), dip=JointAngle(30)),
            pinky=FingerPose(mcp=JointAngle(8), pip=JointAngle(6), dip=JointAngle(4)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-023 "Baby Index Thumb"
@register_symbol(group=6, base_symbol_number=23)
class BaseSymbol01_06_023_BabyIndexThumb(SymbolGroup6BabyFinger):
    """01-06-023 "Baby Index Thumb" -- base symbol 23 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=23, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(7), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(14), pip=JointAngle(5), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(42), pip=JointAngle(117), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(143), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(19), dip=JointAngle(13)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-024 "Baby Index Thumb on Hinge"
@register_symbol(group=6, base_symbol_number=24)
class BaseSymbol01_06_024_BabyIndexThumbOnHinge(SymbolGroup6BabyFinger):
    """01-06-024 "Baby Index Thumb on Hinge" -- base symbol 24 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=24, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(43), mcp=JointAngle(13), ip=JointAngle(28)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(12), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(54), pip=JointAngle(85), dip=JointAngle(20)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(17), dip=JointAngle(23)),
            pinky=FingerPose(mcp=JointAngle(14), pip=JointAngle(4), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-025 "Baby Index Thumb, Angle Out"
@register_symbol(group=6, base_symbol_number=25)
class BaseSymbol01_06_025_BabyIndexThumbAngleOut(SymbolGroup6BabyFinger):
    """01-06-025 "Baby Index Thumb, Angle Out" -- base symbol 25 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=25, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(21), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(59), pip=JointAngle(33), dip=JointAngle(11)),
            middle=FingerPose(mcp=JointAngle(70), pip=JointAngle(99), dip=JointAngle(26)),
            ring=FingerPose(mcp=JointAngle(67), pip=JointAngle(115), dip=JointAngle(28)),
            pinky=FingerPose(mcp=JointAngle(48), pip=JointAngle(11), dip=JointAngle(24)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-026 "Baby Index Thumb, Index Thumb Angle"
@register_symbol(group=6, base_symbol_number=26)
class BaseSymbol01_06_026_BabyIndexThumbIndexThumbAngle(SymbolGroup6BabyFinger):
    """01-06-026 "Baby Index Thumb, Index Thumb Angle" -- base symbol 26 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=26, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(49), mcp=JointAngle(32), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(78), pip=JointAngle(5), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(80), pip=JointAngle(89), dip=JointAngle(24)),
            ring=FingerPose(mcp=JointAngle(76), pip=JointAngle(98), dip=JointAngle(32)),
            pinky=FingerPose(mcp=JointAngle(58), pip=JointAngle(23), dip=JointAngle(46)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-027 "Baby Index"
@register_symbol(group=6, base_symbol_number=27)
class BaseSymbol01_06_027_BabyIndex(SymbolGroup6BabyFinger):
    """01-06-027 "Baby Index" -- base symbol 27 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=27, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(52), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(5), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(61), pip=JointAngle(99), dip=JointAngle(34)),
            ring=FingerPose(mcp=JointAngle(63), pip=JointAngle(104), dip=JointAngle(45)),
            pinky=FingerPose(mcp=JointAngle(30), pip=JointAngle(11), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-028 "Baby Index On Circle"
@register_symbol(group=6, base_symbol_number=28)
class BaseSymbol01_06_028_BabyIndexOnCircle(SymbolGroup6BabyFinger):
    """01-06-028 "Baby Index On Circle" -- base symbol 28 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=28, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(42), mcp=JointAngle(43), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(6), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(38), pip=JointAngle(95), dip=JointAngle(27)),
            ring=FingerPose(mcp=JointAngle(29), pip=JointAngle(113), dip=JointAngle(35)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(7), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-029 "Baby Index On Hinge"
@register_symbol(group=6, base_symbol_number=29)
class BaseSymbol01_06_029_BabyIndexOnHinge(SymbolGroup6BabyFinger):
    """01-06-029 "Baby Index On Hinge" -- base symbol 29 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=29, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(42), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(15), pip=JointAngle(3), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(41), pip=JointAngle(29), dip=JointAngle(7)),
            ring=FingerPose(mcp=JointAngle(35), pip=JointAngle(12), dip=JointAngle(15)),
            pinky=FingerPose(mcp=JointAngle(65), pip=JointAngle(33), dip=JointAngle(14)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-06-030 "Baby Index On Angle"
@register_symbol(group=6, base_symbol_number=30)
class BaseSymbol01_06_030_BabyIndexOnAngle(SymbolGroup6BabyFinger):
    """01-06-030 "Baby Index On Angle" -- base symbol 30 of Group 6."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=6, base_symbol_number=30, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(57), mcp=JointAngle(23), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(21), dip=JointAngle(1)),
            middle=FingerPose(mcp=JointAngle(62), pip=JointAngle(36), dip=JointAngle(15)),
            ring=FingerPose(mcp=JointAngle(55), pip=JointAngle(30), dip=JointAngle(13)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(14), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


