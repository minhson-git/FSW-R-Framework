"""Symbol Group 7 -- Ring Finger.

Group theme is "Ring Finger", but base symbol 1 ("Index Middle Baby") does
not itself involve the ring finger -- confirmed against the real symbol
photo at https://www.signwriting.org/lessons/iswa/group07/01-07-001-01.html:
index, middle, and pinky (baby) fingers extended straight, ring finger
curled, thumb curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-07-001"
("Index Middle Baby"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup7RingFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(49), mcp=JointAngle(49), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(16), pip=JointAngle(6), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(19), pip=JointAngle(12), dip=JointAngle(7)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(118), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(7), dip=JointAngle(13)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=7, base_symbol_number=1)
class BaseSymbol01_07_001_IndexMiddleBaby(SymbolGroup7RingFinger):
    """01-07-001 "Index Middle Baby" -- base symbol 1 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-002 "Index Middle Baby on Circle"
@register_symbol(group=7, base_symbol_number=2)
class BaseSymbol01_07_002_IndexMiddleBabyOnCircle(SymbolGroup7RingFinger):
    """01-07-002 "Index Middle Baby on Circle" -- base symbol 2 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(43), mcp=JointAngle(45), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(10), pip=JointAngle(4), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(20), pip=JointAngle(7), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(16), pip=JointAngle(145), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(6), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-003 "Index Middle Baby on Hinge"
@register_symbol(group=7, base_symbol_number=3)
class BaseSymbol01_07_003_IndexMiddleBabyOnHinge(SymbolGroup7RingFinger):
    """01-07-003 "Index Middle Baby on Hinge" -- base symbol 3 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(43), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(17), pip=JointAngle(5), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(9), pip=JointAngle(12), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(40), pip=JointAngle(26), dip=JointAngle(10)),
            pinky=FingerPose(mcp=JointAngle(42), pip=JointAngle(41), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-004 "Ring Hinge"
@register_symbol(group=7, base_symbol_number=4)
class BaseSymbol01_07_004_RingHinge(SymbolGroup7RingFinger):
    """01-07-004 "Ring Hinge" -- base symbol 4 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(3), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(8), pip=JointAngle(5), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(5), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(54), dip=JointAngle(34)),
            pinky=FingerPose(mcp=JointAngle(17), pip=JointAngle(6), dip=JointAngle(10)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-005 "Index Middle Baby on Angle"
@register_symbol(group=7, base_symbol_number=5)
class BaseSymbol01_07_005_IndexMiddleBabyOnAngle(SymbolGroup7RingFinger):
    """01-07-005 "Index Middle Baby on Angle" -- base symbol 5 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(58), mcp=JointAngle(41), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(16), pip=JointAngle(6), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(18), pip=JointAngle(14), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(44), pip=JointAngle(28), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(49), pip=JointAngle(34), dip=JointAngle(27)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-006 "Index Middle Cross with Baby"
@register_symbol(group=7, base_symbol_number=6)
class BaseSymbol01_07_006_IndexMiddleCrossWithBaby(SymbolGroup7RingFinger):
    """01-07-006 "Index Middle Cross with Baby" -- base symbol 6 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(48), mcp=JointAngle(55), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(35), pip=JointAngle(12), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(18), dip=JointAngle(20)),
            ring=FingerPose(mcp=JointAngle(30), pip=JointAngle(135), dip=JointAngle(26)),
            pinky=FingerPose(mcp=JointAngle(27), pip=JointAngle(4), dip=JointAngle(15)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-007 "Index Middle Cross with Baby on Circle"
@register_symbol(group=7, base_symbol_number=7)
class BaseSymbol01_07_007_IndexMiddleCrossWithBabyOnCircle(SymbolGroup7RingFinger):
    """01-07-007 "Index Middle Cross with Baby on Circle" -- base symbol 7 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(42), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(32), pip=JointAngle(7), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(9), pip=JointAngle(6), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(22), pip=JointAngle(147), dip=JointAngle(17)),
            pinky=FingerPose(mcp=JointAngle(25), pip=JointAngle(9), dip=JointAngle(11)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-008 "Ring Down"
@register_symbol(group=7, base_symbol_number=8)
class BaseSymbol01_07_008_RingDown(SymbolGroup7RingFinger):
    """01-07-008 "Ring Down" -- base symbol 8 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(7), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(21), pip=JointAngle(5), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(16), pip=JointAngle(3), dip=JointAngle(8)),
            ring=FingerPose(mcp=JointAngle(24), pip=JointAngle(153), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(18), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-009 "Ring Down, Index Thumb Hook, Middle Hinge"
@register_symbol(group=7, base_symbol_number=9)
class BaseSymbol01_07_009_RingDownIndexThumbHookMiddleHinge(SymbolGroup7RingFinger):
    """01-07-009 "Ring Down, Index Thumb Hook, Middle Hinge" -- base symbol 9 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(24), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(38), pip=JointAngle(25), dip=JointAngle(30)),
            middle=FingerPose(mcp=JointAngle(68), pip=JointAngle(36), dip=JointAngle(31)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(59), dip=JointAngle(31)),
            pinky=FingerPose(mcp=JointAngle(50), pip=JointAngle(12), dip=JointAngle(18)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-010 "Ring Down, Middle Thumb Angle, Index Cross"
@register_symbol(group=7, base_symbol_number=10)
class BaseSymbol01_07_010_RingDownMiddleThumbAngleIndexCross(SymbolGroup7RingFinger):
    """01-07-010 "Ring Down, Middle Thumb Angle, Index Cross" -- base symbol 10 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(44), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(79), pip=JointAngle(43), dip=JointAngle(24)),
            middle=FingerPose(mcp=JointAngle(65), pip=JointAngle(85), dip=JointAngle(36)),
            ring=FingerPose(mcp=JointAngle(64), pip=JointAngle(88), dip=JointAngle(40)),
            pinky=FingerPose(mcp=JointAngle(30), pip=JointAngle(16), dip=JointAngle(34)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-011 "Ring Up"
@register_symbol(group=7, base_symbol_number=11)
class BaseSymbol01_07_011_RingUp(SymbolGroup7RingFinger):
    """01-07-011 "Ring Up" -- base symbol 11 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(54), mcp=JointAngle(49), ip=JointAngle(37)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(130), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(45), pip=JointAngle(128), dip=JointAngle(34)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(25), dip=JointAngle(44)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(166), dip=JointAngle(42)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-012 "Ring Raised Knuckle"
@register_symbol(group=7, base_symbol_number=12)
class BaseSymbol01_07_012_RingRaisedKnuckle(SymbolGroup7RingFinger):
    """01-07-012 "Ring Raised Knuckle" -- base symbol 12 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(58), ip=JointAngle(32)),
            index=FingerPose(mcp=JointAngle(63), pip=JointAngle(114), dip=JointAngle(21)),
            middle=FingerPose(mcp=JointAngle(46), pip=JointAngle(129), dip=JointAngle(34)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(150), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(147), dip=JointAngle(26)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-013 "Ring Baby"
@register_symbol(group=7, base_symbol_number=13)
class BaseSymbol01_07_013_RingBaby(SymbolGroup7RingFinger):
    """01-07-013 "Ring Baby" -- base symbol 13 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(46), ip=JointAngle(45)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(129), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(43), pip=JointAngle(116), dip=JointAngle(25)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(12), dip=JointAngle(18)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(7), dip=JointAngle(11)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-014 "Ring Baby on Circle"
@register_symbol(group=7, base_symbol_number=14)
class BaseSymbol01_07_014_RingBabyOnCircle(SymbolGroup7RingFinger):
    """01-07-014 "Ring Baby on Circle" -- base symbol 14 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(34), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(55), dip=JointAngle(63)),
            middle=FingerPose(mcp=JointAngle(34), pip=JointAngle(90), dip=JointAngle(47)),
            ring=FingerPose(mcp=JointAngle(19), pip=JointAngle(2), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(10), pip=JointAngle(4), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-015 "Ring Baby on Oval"
@register_symbol(group=7, base_symbol_number=15)
class BaseSymbol01_07_015_RingBabyOnOval(SymbolGroup7RingFinger):
    """01-07-015 "Ring Baby on Oval" -- base symbol 15 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(44), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(55), pip=JointAngle(50), dip=JointAngle(29)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(39), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(24), pip=JointAngle(9), dip=JointAngle(7)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(2), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-016 "Ring Baby on Angle"
@register_symbol(group=7, base_symbol_number=16)
class BaseSymbol01_07_016_RingBabyOnAngle(SymbolGroup7RingFinger):
    """01-07-016 "Ring Baby on Angle" -- base symbol 16 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(32), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(71), pip=JointAngle(14), dip=JointAngle(12)),
            middle=FingerPose(mcp=JointAngle(48), pip=JointAngle(7), dip=JointAngle(8)),
            ring=FingerPose(mcp=JointAngle(33), pip=JointAngle(8), dip=JointAngle(8)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(8), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-017 "Ring Middle"
@register_symbol(group=7, base_symbol_number=17)
class BaseSymbol01_07_017_RingMiddle(SymbolGroup7RingFinger):
    """01-07-017 "Ring Middle" -- base symbol 17 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=17, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(65), mcp=JointAngle(50), ip=JointAngle(26)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(101), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(18), pip=JointAngle(19), dip=JointAngle(10)),
            ring=FingerPose(mcp=JointAngle(28), pip=JointAngle(10), dip=JointAngle(15)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(141), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-018 "Ring Middle Unit"
@register_symbol(group=7, base_symbol_number=18)
class BaseSymbol01_07_018_RingMiddleUnit(SymbolGroup7RingFinger):
    """01-07-018 "Ring Middle Unit" -- base symbol 18 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=18, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(50), mcp=JointAngle(50), ip=JointAngle(41)),
            index=FingerPose(mcp=JointAngle(47), pip=JointAngle(115), dip=JointAngle(30)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(16), dip=JointAngle(12)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(16), dip=JointAngle(10)),
            pinky=FingerPose(mcp=JointAngle(30), pip=JointAngle(159), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-019 "Ring Middle Raised Knuckles"
@register_symbol(group=7, base_symbol_number=19)
class BaseSymbol01_07_019_RingMiddleRaisedKnuckles(SymbolGroup7RingFinger):
    """01-07-019 "Ring Middle Raised Knuckles" -- base symbol 19 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=19, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(53), ip=JointAngle(34)),
            index=FingerPose(mcp=JointAngle(57), pip=JointAngle(117), dip=JointAngle(11)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(138), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(25), pip=JointAngle(156), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(159), dip=JointAngle(11)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-020 "Ring Index"
@register_symbol(group=7, base_symbol_number=20)
class BaseSymbol01_07_020_RingIndex(SymbolGroup7RingFinger):
    """01-07-020 "Ring Index" -- base symbol 20 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=20, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(49), mcp=JointAngle(55), ip=JointAngle(28)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(12), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(49), pip=JointAngle(122), dip=JointAngle(27)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(15), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(159), dip=JointAngle(49)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-021 "Ring Thumb"
@register_symbol(group=7, base_symbol_number=21)
class BaseSymbol01_07_021_RingThumb(SymbolGroup7RingFinger):
    """01-07-021 "Ring Thumb" -- base symbol 21 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=21, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(9), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(44), pip=JointAngle(118), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(122), dip=JointAngle(16)),
            ring=FingerPose(mcp=JointAngle(17), pip=JointAngle(17), dip=JointAngle(12)),
            pinky=FingerPose(mcp=JointAngle(10), pip=JointAngle(47), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-07-022 "Ring Thumb Hook"
@register_symbol(group=7, base_symbol_number=22)
class BaseSymbol01_07_022_RingThumbHook(SymbolGroup7RingFinger):
    """01-07-022 "Ring Thumb Hook" -- base symbol 22 of Group 7."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=7, base_symbol_number=22, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(18), mcp=JointAngle(25), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(44), pip=JointAngle(116), dip=JointAngle(22)),
            middle=FingerPose(mcp=JointAngle(39), pip=JointAngle(121), dip=JointAngle(23)),
            ring=FingerPose(mcp=JointAngle(31), pip=JointAngle(115), dip=JointAngle(32)),
            pinky=FingerPose(mcp=JointAngle(58), pip=JointAngle(108), dip=JointAngle(21)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


