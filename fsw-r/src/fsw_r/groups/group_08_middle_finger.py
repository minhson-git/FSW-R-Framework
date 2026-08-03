"""Symbol Group 8 -- Middle Finger.

Group theme is "Middle Finger", but base symbol 1 ("Index Ring Baby") does
not itself involve the middle finger -- confirmed against the real symbol
photo at https://www.signwriting.org/lessons/iswa/group08/01-08-001-01.html:
index, ring, and pinky (baby) fingers extended straight, middle finger
curled, thumb curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-08-001"
("Index Ring Baby"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup8MiddleFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(50), mcp=JointAngle(41), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(22), pip=JointAngle(16), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(54), pip=JointAngle(104), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(31), pip=JointAngle(25), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(13), pip=JointAngle(5), dip=JointAngle(14)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=8, base_symbol_number=1)
class BaseSymbol01_08_001_IndexRingBaby(SymbolGroup8MiddleFinger):
    """01-08-001 "Index Ring Baby" -- base symbol 1 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-002 "Index Ring Baby on Circle"
@register_symbol(group=8, base_symbol_number=2)
class BaseSymbol01_08_002_IndexRingBabyOnCircle(SymbolGroup8MiddleFinger):
    """01-08-002 "Index Ring Baby on Circle" -- base symbol 2 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(42), mcp=JointAngle(26), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(11), pip=JointAngle(8), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(34), pip=JointAngle(103), dip=JointAngle(39)),
            ring=FingerPose(mcp=JointAngle(19), pip=JointAngle(6), dip=JointAngle(9)),
            pinky=FingerPose(mcp=JointAngle(10), pip=JointAngle(3), dip=JointAngle(13)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-003 "Index Ring Baby on Curlicue"
@register_symbol(group=8, base_symbol_number=3)
class BaseSymbol01_08_003_IndexRingBabyOnCurlicue(SymbolGroup8MiddleFinger):
    """01-08-003 "Index Ring Baby on Curlicue" -- base symbol 3 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(36), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(27), pip=JointAngle(13), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(44), pip=JointAngle(118), dip=JointAngle(25)),
            ring=FingerPose(mcp=JointAngle(17), pip=JointAngle(14), dip=JointAngle(8)),
            pinky=FingerPose(mcp=JointAngle(14), pip=JointAngle(6), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-004 "Index Ring Baby on Hook Out"
@register_symbol(group=8, base_symbol_number=4)
class BaseSymbol01_08_004_IndexRingBabyOnHookOut(SymbolGroup8MiddleFinger):
    """01-08-004 "Index Ring Baby on Hook Out" -- base symbol 4 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(64), mcp=JointAngle(32), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(5), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(39), pip=JointAngle(69), dip=JointAngle(46)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(35), dip=JointAngle(12)),
            pinky=FingerPose(mcp=JointAngle(53), pip=JointAngle(85), dip=JointAngle(22)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-005 "Index Ring Baby on Hook In"
@register_symbol(group=8, base_symbol_number=5)
class BaseSymbol01_08_005_IndexRingBabyOnHookIn(SymbolGroup8MiddleFinger):
    """01-08-005 "Index Ring Baby on Hook In" -- base symbol 5 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(66), mcp=JointAngle(27), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(12), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(57), pip=JointAngle(81), dip=JointAngle(24)),
            ring=FingerPose(mcp=JointAngle(30), pip=JointAngle(0), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(10), pip=JointAngle(9), dip=JointAngle(37)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-006 "Index Ring Baby on Hook Under"
@register_symbol(group=8, base_symbol_number=6)
class BaseSymbol01_08_006_IndexRingBabyOnHookUnder(SymbolGroup8MiddleFinger):
    """01-08-006 "Index Ring Baby on Hook Under" -- base symbol 6 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(60), mcp=JointAngle(27), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(28), pip=JointAngle(7), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(41), pip=JointAngle(65), dip=JointAngle(23)),
            ring=FingerPose(mcp=JointAngle(23), pip=JointAngle(22), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(8), dip=JointAngle(18)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-007 "Index Ring Baby on Cup"
@register_symbol(group=8, base_symbol_number=7)
class BaseSymbol01_08_007_IndexRingBabyOnCup(SymbolGroup8MiddleFinger):
    """01-08-007 "Index Ring Baby on Cup" -- base symbol 7 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(36), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(6), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(25), pip=JointAngle(70), dip=JointAngle(27)),
            ring=FingerPose(mcp=JointAngle(11), pip=JointAngle(21), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(16), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-008 "Index Ring Baby on Hinge"
@register_symbol(group=8, base_symbol_number=8)
class BaseSymbol01_08_008_IndexRingBabyOnHinge(SymbolGroup8MiddleFinger):
    """01-08-008 "Index Ring Baby on Hinge" -- base symbol 8 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(47), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(24), pip=JointAngle(7), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(26), pip=JointAngle(6), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(8), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(75), pip=JointAngle(46), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-009 "Index Ring Baby on Angle Out"
@register_symbol(group=8, base_symbol_number=9)
class BaseSymbol01_08_009_IndexRingBabyOnAngleOut(SymbolGroup8MiddleFinger):
    """01-08-009 "Index Ring Baby on Angle Out" -- base symbol 9 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(54), mcp=JointAngle(32), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(11), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(37), dip=JointAngle(41)),
            ring=FingerPose(mcp=JointAngle(31), pip=JointAngle(22), dip=JointAngle(11)),
            pinky=FingerPose(mcp=JointAngle(38), pip=JointAngle(20), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-010 "Index Ring Baby on Angle"
@register_symbol(group=8, base_symbol_number=10)
class BaseSymbol01_08_010_IndexRingBabyOnAngle(SymbolGroup8MiddleFinger):
    """01-08-010 "Index Ring Baby on Angle" -- base symbol 10 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(54), mcp=JointAngle(30), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(29), pip=JointAngle(5), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(38), pip=JointAngle(38), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(28), pip=JointAngle(22), dip=JointAngle(18)),
            pinky=FingerPose(mcp=JointAngle(42), pip=JointAngle(44), dip=JointAngle(26)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-011 "Middle Down"
@register_symbol(group=8, base_symbol_number=11)
class BaseSymbol01_08_011_MiddleDown(SymbolGroup8MiddleFinger):
    """01-08-011 "Middle Down" -- base symbol 11 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(9), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(15), pip=JointAngle(4), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(117), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(17), pip=JointAngle(7), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(7), pip=JointAngle(10), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-012 "Middle Hinge"
@register_symbol(group=8, base_symbol_number=12)
class BaseSymbol01_08_012_MiddleHinge(SymbolGroup8MiddleFinger):
    """01-08-012 "Middle Hinge" -- base symbol 12 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(10), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(29), pip=JointAngle(13), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(37), pip=JointAngle(51), dip=JointAngle(17)),
            ring=FingerPose(mcp=JointAngle(20), pip=JointAngle(21), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(24), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-013 "Middle Up"
@register_symbol(group=8, base_symbol_number=13)
class BaseSymbol01_08_013_MiddleUp(SymbolGroup8MiddleFinger):
    """01-08-013 "Middle Up" -- base symbol 13 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(58), ip=JointAngle(34)),
            index=FingerPose(mcp=JointAngle(45), pip=JointAngle(113), dip=JointAngle(21)),
            middle=FingerPose(mcp=JointAngle(27), pip=JointAngle(14), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(44), pip=JointAngle(126), dip=JointAngle(20)),
            pinky=FingerPose(mcp=JointAngle(31), pip=JointAngle(153), dip=JointAngle(13)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-014 "Middle Up on Circle"
@register_symbol(group=8, base_symbol_number=14)
class BaseSymbol01_08_014_MiddleUpOnCircle(SymbolGroup8MiddleFinger):
    """01-08-014 "Middle Up on Circle" -- base symbol 14 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(48), ip=JointAngle(29)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(89), dip=JointAngle(28)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(15), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(25), pip=JointAngle(126), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(136), dip=JointAngle(21)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-015 "Middle Raised Knuckle"
@register_symbol(group=8, base_symbol_number=15)
class BaseSymbol01_08_015_MiddleRaisedKnuckle(SymbolGroup8MiddleFinger):
    """01-08-015 "Middle Raised Knuckle" -- base symbol 15 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(54), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(69), pip=JointAngle(91), dip=JointAngle(11)),
            middle=FingerPose(mcp=JointAngle(41), pip=JointAngle(125), dip=JointAngle(19)),
            ring=FingerPose(mcp=JointAngle(59), pip=JointAngle(115), dip=JointAngle(62)),
            pinky=FingerPose(mcp=JointAngle(52), pip=JointAngle(126), dip=JointAngle(46)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-016 "Middle Up, Thumb Side"
@register_symbol(group=8, base_symbol_number=16)
class BaseSymbol01_08_016_MiddleUpThumbSide(SymbolGroup8MiddleFinger):
    """01-08-016 "Middle Up, Thumb Side" -- base symbol 16 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(10), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(55), pip=JointAngle(111), dip=JointAngle(21)),
            middle=FingerPose(mcp=JointAngle(40), pip=JointAngle(9), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(131), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(36), pip=JointAngle(164), dip=JointAngle(10)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-017 "Middle Thumb Hook"
@register_symbol(group=8, base_symbol_number=17)
class BaseSymbol01_08_017_MiddleThumbHook(SymbolGroup8MiddleFinger):
    """01-08-017 "Middle Thumb Hook" -- base symbol 17 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=17, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(44), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(64), pip=JointAngle(75), dip=JointAngle(41)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(56), dip=JointAngle(78)),
            ring=FingerPose(mcp=JointAngle(45), pip=JointAngle(136), dip=JointAngle(19)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(159), dip=JointAngle(15)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-018 "Middle Thumb Baby"
@register_symbol(group=8, base_symbol_number=18)
class BaseSymbol01_08_018_MiddleThumbBaby(SymbolGroup8MiddleFinger):
    """01-08-018 "Middle Thumb Baby" -- base symbol 18 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=18, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(9), ip=JointAngle(27)),
            index=FingerPose(mcp=JointAngle(40), pip=JointAngle(101), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(8), dip=JointAngle(8)),
            ring=FingerPose(mcp=JointAngle(26), pip=JointAngle(148), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(21), dip=JointAngle(11)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-08-019 "Middle Baby"
@register_symbol(group=8, base_symbol_number=19)
class BaseSymbol01_08_019_MiddleBaby(SymbolGroup8MiddleFinger):
    """01-08-019 "Middle Baby" -- base symbol 19 of Group 8."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=8, base_symbol_number=19, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(42), mcp=JointAngle(43), ip=JointAngle(40)),
            index=FingerPose(mcp=JointAngle(46), pip=JointAngle(106), dip=JointAngle(18)),
            middle=FingerPose(mcp=JointAngle(31), pip=JointAngle(18), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(29), pip=JointAngle(160), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(7), pip=JointAngle(9), dip=JointAngle(1)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


