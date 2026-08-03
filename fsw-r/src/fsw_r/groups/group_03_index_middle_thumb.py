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


# 01-03-002 "Index Middle Thumb on Circle"
@register_symbol(group=3, base_symbol_number=2)
class BaseSymbol01_03_002_IndexMiddleThumbOnCircle(SymbolGroup3IndexMiddleThumb):
    """01-03-002 "Index Middle Thumb on Circle" -- base symbol 2 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(6), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(6), pip=JointAngle(3), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(11), pip=JointAngle(6), dip=JointAngle(6)),
            ring=FingerPose(mcp=JointAngle(40), pip=JointAngle(67), dip=JointAngle(31)),
            pinky=FingerPose(mcp=JointAngle(37), pip=JointAngle(54), dip=JointAngle(29)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-003 "Index Middle Straight, Thumb Bent"
@register_symbol(group=3, base_symbol_number=3)
class BaseSymbol01_03_003_IndexMiddleStraightThumbBent(SymbolGroup3IndexMiddleThumb):
    """01-03-003 "Index Middle Straight, Thumb Bent" -- base symbol 3 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(23), ip=JointAngle(37)),
            index=FingerPose(mcp=JointAngle(17), pip=JointAngle(1), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(6), dip=JointAngle(10)),
            ring=FingerPose(mcp=JointAngle(57), pip=JointAngle(108), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(55), pip=JointAngle(104), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-004 "Index Middle Bent, Thumb Straight"
@register_symbol(group=3, base_symbol_number=4)
class BaseSymbol01_03_004_IndexMiddleBentThumbStraight(SymbolGroup3IndexMiddleThumb):
    """01-03-004 "Index Middle Bent, Thumb Straight" -- base symbol 4 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(5), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(39), pip=JointAngle(46), dip=JointAngle(69)),
            middle=FingerPose(mcp=JointAngle(34), pip=JointAngle(68), dip=JointAngle(60)),
            ring=FingerPose(mcp=JointAngle(59), pip=JointAngle(96), dip=JointAngle(40)),
            pinky=FingerPose(mcp=JointAngle(54), pip=JointAngle(104), dip=JointAngle(41)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-005 "Index Middle Thumb Bent"
@register_symbol(group=3, base_symbol_number=5)
class BaseSymbol01_03_005_IndexMiddleThumbBent(SymbolGroup3IndexMiddleThumb):
    """01-03-005 "Index Middle Thumb Bent" -- base symbol 5 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(20), ip=JointAngle(40)),
            index=FingerPose(mcp=JointAngle(35), pip=JointAngle(61), dip=JointAngle(78)),
            middle=FingerPose(mcp=JointAngle(27), pip=JointAngle(92), dip=JointAngle(57)),
            ring=FingerPose(mcp=JointAngle(52), pip=JointAngle(107), dip=JointAngle(42)),
            pinky=FingerPose(mcp=JointAngle(44), pip=JointAngle(113), dip=JointAngle(41)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-006 "Index Middle Hinge Spread, Thumb Side"
@register_symbol(group=3, base_symbol_number=6)
class BaseSymbol01_03_006_IndexMiddleHingeSpreadThumbSide(SymbolGroup3IndexMiddleThumb):
    """01-03-006 "Index Middle Hinge Spread, Thumb Side" -- base symbol 6 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(20), mcp=JointAngle(3), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(54), pip=JointAngle(18), dip=JointAngle(12)),
            middle=FingerPose(mcp=JointAngle(45), pip=JointAngle(19), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(57), pip=JointAngle(117), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(40), pip=JointAngle(129), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-007 "Index Up, Middle Hinge, Thumb Side"
@register_symbol(group=3, base_symbol_number=7)
class BaseSymbol01_03_007_IndexUpMiddleHingeThumbSide(SymbolGroup3IndexMiddleThumb):
    """01-03-007 "Index Up, Middle Hinge, Thumb Side" -- base symbol 7 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(24), mcp=JointAngle(2), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(16), pip=JointAngle(4), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(38), pip=JointAngle(24), dip=JointAngle(24)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(118), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(36), pip=JointAngle(133), dip=JointAngle(18)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-008 "Index Up, Middle Hinge, Thumb Tight"
@register_symbol(group=3, base_symbol_number=8)
class BaseSymbol01_03_008_IndexUpMiddleHingeThumbTight(SymbolGroup3IndexMiddleThumb):
    """01-03-008 "Index Up, Middle Hinge, Thumb Tight" -- base symbol 8 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(30), mcp=JointAngle(33), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(17), pip=JointAngle(7), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(19), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(121), dip=JointAngle(20)),
            pinky=FingerPose(mcp=JointAngle(45), pip=JointAngle(120), dip=JointAngle(21)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-009 "Index Hinge, Middle Up, Thumb Side"
@register_symbol(group=3, base_symbol_number=9)
class BaseSymbol01_03_009_IndexHingeMiddleUpThumbSide(SymbolGroup3IndexMiddleThumb):
    """01-03-009 "Index Hinge, Middle Up, Thumb Side" -- base symbol 9 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(21), mcp=JointAngle(4), ip=JointAngle(22)),
            index=FingerPose(mcp=JointAngle(66), pip=JointAngle(27), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(25), pip=JointAngle(2), dip=JointAngle(12)),
            ring=FingerPose(mcp=JointAngle(48), pip=JointAngle(124), dip=JointAngle(23)),
            pinky=FingerPose(mcp=JointAngle(30), pip=JointAngle(151), dip=JointAngle(13)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-010 "Index Middle Up Spread, Thumb Forward"
@register_symbol(group=3, base_symbol_number=10)
class BaseSymbol01_03_010_IndexMiddleUpSpreadThumbForward(SymbolGroup3IndexMiddleThumb):
    """01-03-010 "Index Middle Up Spread, Thumb Forward" -- base symbol 10 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(19), mcp=JointAngle(48), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(18), pip=JointAngle(1), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(14), pip=JointAngle(8), dip=JointAngle(9)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(127), dip=JointAngle(19)),
            pinky=FingerPose(mcp=JointAngle(27), pip=JointAngle(132), dip=JointAngle(18)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-011 "Index Middle Thumb Cup"
@register_symbol(group=3, base_symbol_number=11)
class BaseSymbol01_03_011_IndexMiddleThumbCup(SymbolGroup3IndexMiddleThumb):
    """01-03-011 "Index Middle Thumb Cup" -- base symbol 11 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(8), mcp=JointAngle(148), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(44), pip=JointAngle(46), dip=JointAngle(95)),
            middle=FingerPose(mcp=JointAngle(33), pip=JointAngle(27), dip=JointAngle(114)),
            ring=FingerPose(mcp=JointAngle(74), pip=JointAngle(115), dip=JointAngle(17)),
            pinky=FingerPose(mcp=JointAngle(97), pip=JointAngle(43), dip=JointAngle(99)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-012 "Index Middle Thumb Circle"
@register_symbol(group=3, base_symbol_number=12)
class BaseSymbol01_03_012_IndexMiddleThumbCircle(SymbolGroup3IndexMiddleThumb):
    """01-03-012 "Index Middle Thumb Circle" -- base symbol 12 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(46), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(67), dip=JointAngle(36)),
            middle=FingerPose(mcp=JointAngle(40), pip=JointAngle(92), dip=JointAngle(46)),
            ring=FingerPose(mcp=JointAngle(56), pip=JointAngle(109), dip=JointAngle(38)),
            pinky=FingerPose(mcp=JointAngle(53), pip=JointAngle(115), dip=JointAngle(36)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-013 "Index Middle Thumb Hook"
@register_symbol(group=3, base_symbol_number=13)
class BaseSymbol01_03_013_IndexMiddleThumbHook(SymbolGroup3IndexMiddleThumb):
    """01-03-013 "Index Middle Thumb Hook" -- base symbol 13 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(90), mcp=JointAngle(90), ip=JointAngle(90)),
            index=FingerPose(mcp=JointAngle(90), pip=JointAngle(90), dip=JointAngle(90)),
            middle=FingerPose(mcp=JointAngle(90), pip=JointAngle(90), dip=JointAngle(90)),
            ring=FingerPose(mcp=JointAngle(90), pip=JointAngle(90), dip=JointAngle(90)),
            pinky=FingerPose(mcp=JointAngle(90), pip=JointAngle(90), dip=JointAngle(90)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-014 "Index Middle Thumb Hinge"
@register_symbol(group=3, base_symbol_number=14)
class BaseSymbol01_03_014_IndexMiddleThumbHinge(SymbolGroup3IndexMiddleThumb):
    """01-03-014 "Index Middle Thumb Hinge" -- base symbol 14 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(36), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(71), pip=JointAngle(7), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(69), pip=JointAngle(14), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(85), pip=JointAngle(80), dip=JointAngle(31)),
            pinky=FingerPose(mcp=JointAngle(83), pip=JointAngle(72), dip=JointAngle(39)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-015 "Thumb Between Index Middle"
@register_symbol(group=3, base_symbol_number=15)
class BaseSymbol01_03_015_ThumbBetweenIndexMiddle(SymbolGroup3IndexMiddleThumb):
    """01-03-015 "Thumb Between Index Middle" -- base symbol 15 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(47), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(80), pip=JointAngle(27), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(76), pip=JointAngle(35), dip=JointAngle(34)),
            ring=FingerPose(mcp=JointAngle(76), pip=JointAngle(102), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(56), pip=JointAngle(115), dip=JointAngle(24)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-016 "Index Middle Unit, Thumb Side"
@register_symbol(group=3, base_symbol_number=16)
class BaseSymbol01_03_016_IndexMiddleUnitThumbSide(SymbolGroup3IndexMiddleThumb):
    """01-03-016 "Index Middle Unit, Thumb Side" -- base symbol 16 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(7), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(27), pip=JointAngle(2), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(16), pip=JointAngle(3), dip=JointAngle(9)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(113), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(57), pip=JointAngle(102), dip=JointAngle(25)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-017 "Index Middle Unit, Thumb Tight"
@register_symbol(group=3, base_symbol_number=17)
class BaseSymbol01_03_017_IndexMiddleUnitThumbTight(SymbolGroup3IndexMiddleThumb):
    """01-03-017 "Index Middle Unit, Thumb Tight" -- base symbol 17 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=17, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(31), ip=JointAngle(27)),
            index=FingerPose(mcp=JointAngle(22), pip=JointAngle(2), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(26), dip=JointAngle(32)),
            ring=FingerPose(mcp=JointAngle(44), pip=JointAngle(108), dip=JointAngle(28)),
            pinky=FingerPose(mcp=JointAngle(52), pip=JointAngle(95), dip=JointAngle(31)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-018 "Index Middle Unit, Thumb Bent"
@register_symbol(group=3, base_symbol_number=18)
class BaseSymbol01_03_018_IndexMiddleUnitThumbBent(SymbolGroup3IndexMiddleThumb):
    """01-03-018 "Index Middle Unit, Thumb Bent" -- base symbol 18 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=18, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(21), ip=JointAngle(29)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(2), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(15), pip=JointAngle(3), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(124), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(32), pip=JointAngle(133), dip=JointAngle(26)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-019 "Middle Thumb Hook, Index Up"
@register_symbol(group=3, base_symbol_number=19)
class BaseSymbol01_03_019_MiddleThumbHookIndexUp(SymbolGroup3IndexMiddleThumb):
    """01-03-019 "Middle Thumb Hook, Index Up" -- base symbol 19 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=19, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(41), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(29), pip=JointAngle(6), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(88), dip=JointAngle(48)),
            ring=FingerPose(mcp=JointAngle(63), pip=JointAngle(100), dip=JointAngle(47)),
            pinky=FingerPose(mcp=JointAngle(55), pip=JointAngle(111), dip=JointAngle(44)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-020 "Index Thumb Hook, Middle Up"
@register_symbol(group=3, base_symbol_number=20)
class BaseSymbol01_03_020_IndexThumbHookMiddleUp(SymbolGroup3IndexMiddleThumb):
    """01-03-020 "Index Thumb Hook, Middle Up" -- base symbol 20 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=20, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(54), mcp=JointAngle(40), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(41), pip=JointAngle(73), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(20), pip=JointAngle(13), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(103), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(53), pip=JointAngle(105), dip=JointAngle(24)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-021 "Index Middle Unit Hinge, Thumb Side"
@register_symbol(group=3, base_symbol_number=21)
class BaseSymbol01_03_021_IndexMiddleUnitHingeThumbSide(SymbolGroup3IndexMiddleThumb):
    """01-03-021 "Index Middle Unit Hinge, Thumb Side" -- base symbol 21 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=21, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(23), mcp=JointAngle(6), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(61), pip=JointAngle(20), dip=JointAngle(12)),
            middle=FingerPose(mcp=JointAngle(48), pip=JointAngle(20), dip=JointAngle(17)),
            ring=FingerPose(mcp=JointAngle(64), pip=JointAngle(109), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(48), pip=JointAngle(122), dip=JointAngle(25)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-022 "Index Middle Cross, Thumb Side"
@register_symbol(group=3, base_symbol_number=22)
class BaseSymbol01_03_022_IndexMiddleCrossThumbSide(SymbolGroup3IndexMiddleThumb):
    """01-03-022 "Index Middle Cross, Thumb Side" -- base symbol 22 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=22, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(3), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(4), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(28), pip=JointAngle(84), dip=JointAngle(57)),
            ring=FingerPose(mcp=JointAngle(49), pip=JointAngle(120), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(43), pip=JointAngle(125), dip=JointAngle(24)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-023 "Index Middle Unit, Thumb Forward"
@register_symbol(group=3, base_symbol_number=23)
class BaseSymbol01_03_023_IndexMiddleUnitThumbForward(SymbolGroup3IndexMiddleThumb):
    """01-03-023 "Index Middle Unit, Thumb Forward" -- base symbol 23 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=23, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(47), mcp=JointAngle(54), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(30), pip=JointAngle(61), dip=JointAngle(60)),
            middle=FingerPose(mcp=JointAngle(33), pip=JointAngle(104), dip=JointAngle(108)),
            ring=FingerPose(mcp=JointAngle(45), pip=JointAngle(105), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(42), pip=JointAngle(109), dip=JointAngle(22)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-024 "Index Middle Unit Cup, Thumb Forward"
@register_symbol(group=3, base_symbol_number=24)
class BaseSymbol01_03_024_IndexMiddleUnitCupThumbForward(SymbolGroup3IndexMiddleThumb):
    """01-03-024 "Index Middle Unit Cup, Thumb Forward" -- base symbol 24 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=24, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(57), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(32), pip=JointAngle(31), dip=JointAngle(44)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(43), dip=JointAngle(52)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(107), dip=JointAngle(28)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(112), dip=JointAngle(40)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-025 "Middle Thumb Cup, Index Up"
@register_symbol(group=3, base_symbol_number=25)
class BaseSymbol01_03_025_MiddleThumbCupIndexUp(SymbolGroup3IndexMiddleThumb):
    """01-03-025 "Middle Thumb Cup, Index Up" -- base symbol 25 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=25, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(82), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(19), pip=JointAngle(5), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(17), pip=JointAngle(125), dip=JointAngle(36)),
            ring=FingerPose(mcp=JointAngle(45), pip=JointAngle(127), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(138), dip=JointAngle(30)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-026 "Index Thumb Cup, Middle Up"
@register_symbol(group=3, base_symbol_number=26)
class BaseSymbol01_03_026_IndexThumbCupMiddleUp(SymbolGroup3IndexMiddleThumb):
    """01-03-026 "Index Thumb Cup, Middle Up" -- base symbol 26 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=26, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(52), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(31), pip=JointAngle(23), dip=JointAngle(48)),
            middle=FingerPose(mcp=JointAngle(21), pip=JointAngle(6), dip=JointAngle(9)),
            ring=FingerPose(mcp=JointAngle(37), pip=JointAngle(121), dip=JointAngle(19)),
            pinky=FingerPose(mcp=JointAngle(33), pip=JointAngle(124), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-027 "Middle Thumb Circle, Index Up"
@register_symbol(group=3, base_symbol_number=27)
class BaseSymbol01_03_027_MiddleThumbCircleIndexUp(SymbolGroup3IndexMiddleThumb):
    """01-03-027 "Middle Thumb Circle, Index Up" -- base symbol 27 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=27, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(41), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(19), pip=JointAngle(7), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(40), pip=JointAngle(107), dip=JointAngle(38)),
            ring=FingerPose(mcp=JointAngle(63), pip=JointAngle(108), dip=JointAngle(43)),
            pinky=FingerPose(mcp=JointAngle(46), pip=JointAngle(128), dip=JointAngle(39)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-028 "Middle Thumb Circle, Index Hinge"
@register_symbol(group=3, base_symbol_number=28)
class BaseSymbol01_03_028_MiddleThumbCircleIndexHinge(SymbolGroup3IndexMiddleThumb):
    """01-03-028 "Middle Thumb Circle, Index Hinge" -- base symbol 28 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=28, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(36), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(6), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(40), pip=JointAngle(109), dip=JointAngle(39)),
            ring=FingerPose(mcp=JointAngle(61), pip=JointAngle(112), dip=JointAngle(43)),
            pinky=FingerPose(mcp=JointAngle(46), pip=JointAngle(127), dip=JointAngle(41)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-029 "Index Thumb Angle Out, Middle Up"
@register_symbol(group=3, base_symbol_number=29)
class BaseSymbol01_03_029_IndexThumbAngleOutMiddleUp(SymbolGroup3IndexMiddleThumb):
    """01-03-029 "Index Thumb Angle Out, Middle Up" -- base symbol 29 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=29, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(31), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(47), pip=JointAngle(94), dip=JointAngle(18)),
            middle=FingerPose(mcp=JointAngle(31), pip=JointAngle(25), dip=JointAngle(34)),
            ring=FingerPose(mcp=JointAngle(57), pip=JointAngle(113), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(57), pip=JointAngle(117), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-030 "Index Thumb Angle In, Middle Up"
@register_symbol(group=3, base_symbol_number=30)
class BaseSymbol01_03_030_IndexThumbAngleInMiddleUp(SymbolGroup3IndexMiddleThumb):
    """01-03-030 "Index Thumb Angle In, Middle Up" -- base symbol 30 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=30, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(62), ip=JointAngle(27)),
            index=FingerPose(mcp=JointAngle(69), pip=JointAngle(71), dip=JointAngle(25)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(1), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(54), pip=JointAngle(104), dip=JointAngle(26)),
            pinky=FingerPose(mcp=JointAngle(43), pip=JointAngle(120), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-031 "Index Thumb Circle, Middle Up"
@register_symbol(group=3, base_symbol_number=31)
class BaseSymbol01_03_031_IndexThumbCircleMiddleUp(SymbolGroup3IndexMiddleThumb):
    """01-03-031 "Index Thumb Circle, Middle Up" -- base symbol 31 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=31, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(54), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(71), dip=JointAngle(35)),
            middle=FingerPose(mcp=JointAngle(26), pip=JointAngle(4), dip=JointAngle(14)),
            ring=FingerPose(mcp=JointAngle(47), pip=JointAngle(117), dip=JointAngle(26)),
            pinky=FingerPose(mcp=JointAngle(28), pip=JointAngle(141), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-032 "Index Middle Thumb, Unit Hinge"
@register_symbol(group=3, base_symbol_number=32)
class BaseSymbol01_03_032_IndexMiddleThumbUnitHinge(SymbolGroup3IndexMiddleThumb):
    """01-03-032 "Index Middle Thumb, Unit Hinge" -- base symbol 32 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=32, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(49), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(82), pip=JointAngle(4), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(75), pip=JointAngle(51), dip=JointAngle(54)),
            ring=FingerPose(mcp=JointAngle(81), pip=JointAngle(94), dip=JointAngle(55)),
            pinky=FingerPose(mcp=JointAngle(69), pip=JointAngle(93), dip=JointAngle(56)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-033 "Index Middle Thumb, Angle Out"
@register_symbol(group=3, base_symbol_number=33)
class BaseSymbol01_03_033_IndexMiddleThumbAngleOut(SymbolGroup3IndexMiddleThumb):
    """01-03-033 "Index Middle Thumb, Angle Out" -- base symbol 33 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=33, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(35), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(67), pip=JointAngle(53), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(71), pip=JointAngle(13), dip=JointAngle(20)),
            ring=FingerPose(mcp=JointAngle(81), pip=JointAngle(102), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(69), pip=JointAngle(109), dip=JointAngle(31)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-034 "Index Middle Thumb Angle"
@register_symbol(group=3, base_symbol_number=34)
class BaseSymbol01_03_034_IndexMiddleThumbAngle(SymbolGroup3IndexMiddleThumb):
    """01-03-034 "Index Middle Thumb Angle" -- base symbol 34 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=34, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(34), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(76), pip=JointAngle(11), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(67), pip=JointAngle(90), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(72), pip=JointAngle(105), dip=JointAngle(49)),
            pinky=FingerPose(mcp=JointAngle(63), pip=JointAngle(110), dip=JointAngle(51)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-035 "Middle Thumb Angle Out, Index Up"
@register_symbol(group=3, base_symbol_number=35)
class BaseSymbol01_03_035_MiddleThumbAngleOutIndexUp(SymbolGroup3IndexMiddleThumb):
    """01-03-035 "Middle Thumb Angle Out, Index Up" -- base symbol 35 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=35, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(46), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(10), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(56), pip=JointAngle(15), dip=JointAngle(31)),
            ring=FingerPose(mcp=JointAngle(62), pip=JointAngle(113), dip=JointAngle(20)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(128), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-036 "Middle Thumb Angle Out, Index Crossed"
@register_symbol(group=3, base_symbol_number=36)
class BaseSymbol01_03_036_MiddleThumbAngleOutIndexCrossed(SymbolGroup3IndexMiddleThumb):
    """01-03-036 "Middle Thumb Angle Out, Index Crossed" -- base symbol 36 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=36, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(35), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(122), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(46), pip=JointAngle(137), dip=JointAngle(35)),
            ring=FingerPose(mcp=JointAngle(48), pip=JointAngle(133), dip=JointAngle(44)),
            pinky=FingerPose(mcp=JointAngle(36), pip=JointAngle(135), dip=JointAngle(39)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-037 "Middle Thumb Angle, Index Up"
@register_symbol(group=3, base_symbol_number=37)
class BaseSymbol01_03_037_MiddleThumbAngleIndexUp(SymbolGroup3IndexMiddleThumb):
    """01-03-037 "Middle Thumb Angle, Index Up" -- base symbol 37 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=37, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(48), mcp=JointAngle(56), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(25), pip=JointAngle(11), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(48), pip=JointAngle(80), dip=JointAngle(48)),
            ring=FingerPose(mcp=JointAngle(62), pip=JointAngle(110), dip=JointAngle(26)),
            pinky=FingerPose(mcp=JointAngle(44), pip=JointAngle(123), dip=JointAngle(28)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-03-038 "Index Thumb Hook, Middle Angle"
@register_symbol(group=3, base_symbol_number=38)
class BaseSymbol01_03_038_IndexThumbHookMiddleAngle(SymbolGroup3IndexMiddleThumb):
    """01-03-038 "Index Thumb Hook, Middle Angle" -- base symbol 38 of Group 3."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=3, base_symbol_number=38, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(38), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(37), pip=JointAngle(27), dip=JointAngle(25)),
            middle=FingerPose(mcp=JointAngle(60), pip=JointAngle(75), dip=JointAngle(110)),
            ring=FingerPose(mcp=JointAngle(68), pip=JointAngle(108), dip=JointAngle(57)),
            pinky=FingerPose(mcp=JointAngle(51), pip=JointAngle(126), dip=JointAngle(47)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


