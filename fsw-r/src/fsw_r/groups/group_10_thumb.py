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


# 01-10-002 "Thumb Heel"
@register_symbol(group=10, base_symbol_number=2)
class BaseSymbol01_10_002_ThumbHeel(SymbolGroup10Thumb):
    """01-10-002 "Thumb Heel" -- base symbol 2 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(8), mcp=JointAngle(7), ip=JointAngle(42)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(68), dip=JointAngle(42)),
            middle=FingerPose(mcp=JointAngle(21), pip=JointAngle(96), dip=JointAngle(65)),
            ring=FingerPose(mcp=JointAngle(6), pip=JointAngle(115), dip=JointAngle(54)),
            pinky=FingerPose(mcp=JointAngle(6), pip=JointAngle(78), dip=JointAngle(55)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-003 "Thumb Side Diagonal"
@register_symbol(group=10, base_symbol_number=3)
class BaseSymbol01_10_003_ThumbSideDiagonal(SymbolGroup10Thumb):
    """01-10-003 "Thumb Side Diagonal" -- base symbol 3 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(25), mcp=JointAngle(18), ip=JointAngle(24)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(120), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(41), pip=JointAngle(126), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(35), pip=JointAngle(147), dip=JointAngle(19)),
            pinky=FingerPose(mcp=JointAngle(28), pip=JointAngle(158), dip=JointAngle(14)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-004 "Thumb Side Unit"
@register_symbol(group=10, base_symbol_number=4)
class BaseSymbol01_10_004_ThumbSideUnit(SymbolGroup10Thumb):
    """01-10-004 "Thumb Side Unit" -- base symbol 4 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(39), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(56), pip=JointAngle(120), dip=JointAngle(1)),
            middle=FingerPose(mcp=JointAngle(49), pip=JointAngle(131), dip=JointAngle(30)),
            ring=FingerPose(mcp=JointAngle(46), pip=JointAngle(146), dip=JointAngle(49)),
            pinky=FingerPose(mcp=JointAngle(40), pip=JointAngle(155), dip=JointAngle(38)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-005 "Thumb Side Bent"
@register_symbol(group=10, base_symbol_number=5)
class BaseSymbol01_10_005_ThumbSideBent(SymbolGroup10Thumb):
    """01-10-005 "Thumb Side Bent" -- base symbol 5 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(25), mcp=JointAngle(34), ip=JointAngle(47)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(121), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(42), pip=JointAngle(133), dip=JointAngle(65)),
            ring=FingerPose(mcp=JointAngle(38), pip=JointAngle(150), dip=JointAngle(64)),
            pinky=FingerPose(mcp=JointAngle(31), pip=JointAngle(162), dip=JointAngle(38)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-006 "Thumb Forward"
@register_symbol(group=10, base_symbol_number=6)
class BaseSymbol01_10_006_ThumbForward(SymbolGroup10Thumb):
    """01-10-006 "Thumb Forward" -- base symbol 6 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(51), ip=JointAngle(29)),
            index=FingerPose(mcp=JointAngle(46), pip=JointAngle(118), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(44), pip=JointAngle(137), dip=JointAngle(73)),
            ring=FingerPose(mcp=JointAngle(42), pip=JointAngle(151), dip=JointAngle(55)),
            pinky=FingerPose(mcp=JointAngle(32), pip=JointAngle(156), dip=JointAngle(38)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-007 "Thumb Between Index Middle"
@register_symbol(group=10, base_symbol_number=7)
class BaseSymbol01_10_007_ThumbBetweenIndexMiddle(SymbolGroup10Thumb):
    """01-10-007 "Thumb Between Index Middle" -- base symbol 7 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(45), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(113), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(50), pip=JointAngle(125), dip=JointAngle(32)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(138), dip=JointAngle(47)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(153), dip=JointAngle(33)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-008 "Thumb Between Middle Ring"
@register_symbol(group=10, base_symbol_number=8)
class BaseSymbol01_10_008_ThumbBetweenMiddleRing(SymbolGroup10Thumb):
    """01-10-008 "Thumb Between Middle Ring" -- base symbol 8 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(52), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(107), dip=JointAngle(12)),
            middle=FingerPose(mcp=JointAngle(37), pip=JointAngle(125), dip=JointAngle(19)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(140), dip=JointAngle(22)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(148), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-009 "Thumb Between Ring Baby"
@register_symbol(group=10, base_symbol_number=9)
class BaseSymbol01_10_009_ThumbBetweenRingBaby(SymbolGroup10Thumb):
    """01-10-009 "Thumb Between Ring Baby" -- base symbol 9 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(53), mcp=JointAngle(56), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(42), pip=JointAngle(114), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(30), pip=JointAngle(128), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(22), pip=JointAngle(149), dip=JointAngle(13)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(136), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-010 "Thumb Under Two Fingers"
@register_symbol(group=10, base_symbol_number=10)
class BaseSymbol01_10_010_ThumbUnderTwoFingers(SymbolGroup10Thumb):
    """01-10-010 "Thumb Under Two Fingers" -- base symbol 10 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(44), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(110), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(32), pip=JointAngle(133), dip=JointAngle(26)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(135), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(49), pip=JointAngle(139), dip=JointAngle(32)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-011 "Thumb Over Two Fingers"
@register_symbol(group=10, base_symbol_number=11)
class BaseSymbol01_10_011_ThumbOverTwoFingers(SymbolGroup10Thumb):
    """01-10-011 "Thumb Over Two Fingers" -- base symbol 11 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(53), ip=JointAngle(49)),
            index=FingerPose(mcp=JointAngle(51), pip=JointAngle(119), dip=JointAngle(1)),
            middle=FingerPose(mcp=JointAngle(48), pip=JointAngle(130), dip=JointAngle(40)),
            ring=FingerPose(mcp=JointAngle(46), pip=JointAngle(142), dip=JointAngle(52)),
            pinky=FingerPose(mcp=JointAngle(37), pip=JointAngle(156), dip=JointAngle(35)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-012 "Thumb Under Three Fingers"
@register_symbol(group=10, base_symbol_number=12)
class BaseSymbol01_10_012_ThumbUnderThreeFingers(SymbolGroup10Thumb):
    """01-10-012 "Thumb Under Three Fingers" -- base symbol 12 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(56), mcp=JointAngle(65), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(38), pip=JointAngle(134), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(140), dip=JointAngle(14)),
            ring=FingerPose(mcp=JointAngle(23), pip=JointAngle(149), dip=JointAngle(12)),
            pinky=FingerPose(mcp=JointAngle(56), pip=JointAngle(122), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-013 "Thumb Under Four Fingers"
@register_symbol(group=10, base_symbol_number=13)
class BaseSymbol01_10_013_ThumbUnderFourFingers(SymbolGroup10Thumb):
    """01-10-013 "Thumb Under Four Fingers" -- base symbol 13 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(32), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(119), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(43), pip=JointAngle(126), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(38), pip=JointAngle(144), dip=JointAngle(15)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(153), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-014 "Thumb Over Four Raised Knuckles"
@register_symbol(group=10, base_symbol_number=14)
class BaseSymbol01_10_014_ThumbOverFourRaisedKnuckles(SymbolGroup10Thumb):
    """01-10-014 "Thumb Over Four Raised Knuckles" -- base symbol 14 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(59), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(45), pip=JointAngle(132), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(150), dip=JointAngle(12)),
            ring=FingerPose(mcp=JointAngle(19), pip=JointAngle(167), dip=JointAngle(8)),
            pinky=FingerPose(mcp=JointAngle(14), pip=JointAngle(158), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-015 "Fist"
@register_symbol(group=10, base_symbol_number=15)
class BaseSymbol01_10_015_Fist(SymbolGroup10Thumb):
    """01-10-015 "Fist" -- base symbol 15 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(70), ip=JointAngle(35)),
            index=FingerPose(mcp=JointAngle(55), pip=JointAngle(125), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(43), pip=JointAngle(140), dip=JointAngle(37)),
            ring=FingerPose(mcp=JointAngle(39), pip=JointAngle(148), dip=JointAngle(44)),
            pinky=FingerPose(mcp=JointAngle(22), pip=JointAngle(164), dip=JointAngle(22)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-10-016 "Fist Heel"
@register_symbol(group=10, base_symbol_number=16)
class BaseSymbol01_10_016_FistHeel(SymbolGroup10Thumb):
    """01-10-016 "Fist Heel" -- base symbol 16 of Group 10."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=10, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(51), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(21), pip=JointAngle(94), dip=JointAngle(87)),
            middle=FingerPose(mcp=JointAngle(45), pip=JointAngle(108), dip=JointAngle(37)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(118), dip=JointAngle(34)),
            pinky=FingerPose(mcp=JointAngle(43), pip=JointAngle(113), dip=JointAngle(34)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


