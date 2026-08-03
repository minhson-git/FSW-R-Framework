"""Symbol Group 9 -- Index & Thumb.

Group theme is "Index & Thumb", but base symbol 1 ("Middle Ring Baby") does
not itself involve the index finger or thumb -- confirmed against the real
symbol photo at
https://www.signwriting.org/lessons/iswa/group09/01-09-001-01.html: middle,
ring, and pinky (baby) fingers extended straight, index finger curled,
thumb curled/tucked against the palm.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-09-001"
("Middle Ring Baby"), orientation 1 (fill=0, Palm of Hand/Wall Plane). See
group_01_index_finger.py's docstring for the exact method and caveats.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup9IndexThumb(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(43), mcp=JointAngle(56), ip=JointAngle(45)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(89), dip=JointAngle(22)),
            middle=FingerPose(mcp=JointAngle(17), pip=JointAngle(12), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(13), pip=JointAngle(2), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(6), pip=JointAngle(1), dip=JointAngle(6)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=9, base_symbol_number=1)
class BaseSymbol01_09_001_MiddleRingBaby(SymbolGroup9IndexThumb):
    """01-09-001 "Middle Ring Baby" -- base symbol 1 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-002 "Middle Ring Baby on Circle"
@register_symbol(group=9, base_symbol_number=2)
class BaseSymbol01_09_002_MiddleRingBabyOnCircle(SymbolGroup9IndexThumb):
    """01-09-002 "Middle Ring Baby on Circle" -- base symbol 2 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(35), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(39), pip=JointAngle(60), dip=JointAngle(42)),
            middle=FingerPose(mcp=JointAngle(13), pip=JointAngle(7), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(10), pip=JointAngle(2), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(7), pip=JointAngle(7), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-003 "Middle Ring Baby on Curlicue"
@register_symbol(group=9, base_symbol_number=3)
class BaseSymbol01_09_003_MiddleRingBabyOnCurlicue(SymbolGroup9IndexThumb):
    """01-09-003 "Middle Ring Baby on Curlicue" -- base symbol 3 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(48), mcp=JointAngle(35), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(31), pip=JointAngle(9), dip=JointAngle(98)),
            middle=FingerPose(mcp=JointAngle(14), pip=JointAngle(10), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(8), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(23), pip=JointAngle(7), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-004 "Middle Ring Baby on Cup"
@register_symbol(group=9, base_symbol_number=4)
class BaseSymbol01_09_004_MiddleRingBabyOnCup(SymbolGroup9IndexThumb):
    """01-09-004 "Middle Ring Baby on Cup" -- base symbol 4 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(41), ip=JointAngle(13)),
            index=FingerPose(mcp=JointAngle(31), pip=JointAngle(49), dip=JointAngle(49)),
            middle=FingerPose(mcp=JointAngle(8), pip=JointAngle(13), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(4), pip=JointAngle(8), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(5), pip=JointAngle(8), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-005 "Middle Ring Baby on Hinge"
@register_symbol(group=9, base_symbol_number=5)
class BaseSymbol01_09_005_MiddleRingBabyOnHinge(SymbolGroup9IndexThumb):
    """01-09-005 "Middle Ring Baby on Hinge" -- base symbol 5 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(51), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(39), pip=JointAngle(14), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(9), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(4), pip=JointAngle(4), dip=JointAngle(7)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(2), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-006 "Middle Ring Baby on Angle Out"
@register_symbol(group=9, base_symbol_number=6)
class BaseSymbol01_09_006_MiddleRingBabyOnAngleOut(SymbolGroup9IndexThumb):
    """01-09-006 "Middle Ring Baby on Angle Out" -- base symbol 6 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(33), ip=JointAngle(16)),
            index=FingerPose(mcp=JointAngle(53), pip=JointAngle(77), dip=JointAngle(25)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(5), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(11), pip=JointAngle(15), dip=JointAngle(12)),
            pinky=FingerPose(mcp=JointAngle(12), pip=JointAngle(10), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-007 "Middle Ring Baby on Angle In"
@register_symbol(group=9, base_symbol_number=7)
class BaseSymbol01_09_007_MiddleRingBabyOnAngleIn(SymbolGroup9IndexThumb):
    """01-09-007 "Middle Ring Baby on Angle In" -- base symbol 7 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(53), mcp=JointAngle(42), ip=JointAngle(26)),
            index=FingerPose(mcp=JointAngle(67), pip=JointAngle(52), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(18), pip=JointAngle(4), dip=JointAngle(7)),
            ring=FingerPose(mcp=JointAngle(16), pip=JointAngle(5), dip=JointAngle(12)),
            pinky=FingerPose(mcp=JointAngle(13), pip=JointAngle(14), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-008 "Middle Ring Baby on Angle"
@register_symbol(group=9, base_symbol_number=8)
class BaseSymbol01_09_008_MiddleRingBabyOnAngle(SymbolGroup9IndexThumb):
    """01-09-008 "Middle Ring Baby on Angle" -- base symbol 8 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(53), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(56), pip=JointAngle(41), dip=JointAngle(24)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(6), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(3), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(6), pip=JointAngle(4), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-009 "Middle Ring Baby Bent"
@register_symbol(group=9, base_symbol_number=9)
class BaseSymbol01_09_009_MiddleRingBabyBent(SymbolGroup9IndexThumb):
    """01-09-009 "Middle Ring Baby Bent" -- base symbol 9 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(44), ip=JointAngle(13)),
            index=FingerPose(mcp=JointAngle(47), pip=JointAngle(63), dip=JointAngle(44)),
            middle=FingerPose(mcp=JointAngle(16), pip=JointAngle(49), dip=JointAngle(48)),
            ring=FingerPose(mcp=JointAngle(23), pip=JointAngle(40), dip=JointAngle(44)),
            pinky=FingerPose(mcp=JointAngle(31), pip=JointAngle(31), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-010 "Middle Ring Baby Unit on Claw"
@register_symbol(group=9, base_symbol_number=10)
class BaseSymbol01_09_010_MiddleRingBabyUnitOnClaw(SymbolGroup9IndexThumb):
    """01-09-010 "Middle Ring Baby Unit on Claw" -- base symbol 10 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(52), ip=JointAngle(38)),
            index=FingerPose(mcp=JointAngle(38), pip=JointAngle(56), dip=JointAngle(67)),
            middle=FingerPose(mcp=JointAngle(13), pip=JointAngle(11), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(6), pip=JointAngle(6), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(5), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-011 "Middle Ring Baby Unit on Claw Side"
@register_symbol(group=9, base_symbol_number=11)
class BaseSymbol01_09_011_MiddleRingBabyUnitOnClawSide(SymbolGroup9IndexThumb):
    """01-09-011 "Middle Ring Baby Unit on Claw Side" -- base symbol 11 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(8), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(68), dip=JointAngle(55)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(9), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(9), pip=JointAngle(2), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(10), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-012 "Middle Ring Baby Unit on Hook Out"
@register_symbol(group=9, base_symbol_number=12)
class BaseSymbol01_09_012_MiddleRingBabyUnitOnHookOut(SymbolGroup9IndexThumb):
    """01-09-012 "Middle Ring Baby Unit on Hook Out" -- base symbol 12 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(25), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(40), pip=JointAngle(27), dip=JointAngle(25)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(8), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(11), dip=JointAngle(7)),
            pinky=FingerPose(mcp=JointAngle(25), pip=JointAngle(11), dip=JointAngle(4)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-013 "Middle Ring Baby Unit on Hook In"
@register_symbol(group=9, base_symbol_number=13)
class BaseSymbol01_09_013_MiddleRingBabyUnitOnHookIn(SymbolGroup9IndexThumb):
    """01-09-013 "Middle Ring Baby Unit on Hook In" -- base symbol 13 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(64), ip=JointAngle(29)),
            index=FingerPose(mcp=JointAngle(71), pip=JointAngle(61), dip=JointAngle(18)),
            middle=FingerPose(mcp=JointAngle(30), pip=JointAngle(10), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(16), pip=JointAngle(7), dip=JointAngle(9)),
            pinky=FingerPose(mcp=JointAngle(7), pip=JointAngle(23), dip=JointAngle(4)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-014 "Middle Ring Baby Unit on Hook"
@register_symbol(group=9, base_symbol_number=14)
class BaseSymbol01_09_014_MiddleRingBabyUnitOnHook(SymbolGroup9IndexThumb):
    """01-09-014 "Middle Ring Baby Unit on Hook" -- base symbol 14 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(53), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(75), dip=JointAngle(37)),
            middle=FingerPose(mcp=JointAngle(22), pip=JointAngle(17), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(12), pip=JointAngle(10), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(13), pip=JointAngle(9), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-015 "Index Hinge"
@register_symbol(group=9, base_symbol_number=15)
class BaseSymbol01_09_015_IndexHinge(SymbolGroup9IndexThumb):
    """01-09-015 "Index Hinge" -- base symbol 15 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(30), mcp=JointAngle(3), ip=JointAngle(28)),
            index=FingerPose(mcp=JointAngle(44), pip=JointAngle(52), dip=JointAngle(23)),
            middle=FingerPose(mcp=JointAngle(9), pip=JointAngle(7), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(10), pip=JointAngle(3), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(15), pip=JointAngle(5), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-016 "Index Thumb Side"
@register_symbol(group=9, base_symbol_number=16)
class BaseSymbol01_09_016_IndexThumbSide(SymbolGroup9IndexThumb):
    """01-09-016 "Index Thumb Side" -- base symbol 16 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(27), mcp=JointAngle(3), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(3), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(45), pip=JointAngle(111), dip=JointAngle(23)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(118), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(32), pip=JointAngle(136), dip=JointAngle(18)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-017 "Index Thumb Side on Hinge"
@register_symbol(group=9, base_symbol_number=17)
class BaseSymbol01_09_017_IndexThumbSideOnHinge(SymbolGroup9IndexThumb):
    """01-09-017 "Index Thumb Side on Hinge" -- base symbol 17 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=17, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(2), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(11), pip=JointAngle(13), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(42), pip=JointAngle(48), dip=JointAngle(28)),
            ring=FingerPose(mcp=JointAngle(35), pip=JointAngle(36), dip=JointAngle(46)),
            pinky=FingerPose(mcp=JointAngle(29), pip=JointAngle(24), dip=JointAngle(21)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-018 "Index Thumb Side, Thumb Diagonal"
@register_symbol(group=9, base_symbol_number=18)
class BaseSymbol01_09_018_IndexThumbSideThumbDiagonal(SymbolGroup9IndexThumb):
    """01-09-018 "Index Thumb Side, Thumb Diagonal" -- base symbol 18 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=18, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(20), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(31), pip=JointAngle(7), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(47), pip=JointAngle(112), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(48), pip=JointAngle(124), dip=JointAngle(20)),
            pinky=FingerPose(mcp=JointAngle(24), pip=JointAngle(149), dip=JointAngle(16)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-019 "Index Thumb Side, Thumb Unit"
@register_symbol(group=9, base_symbol_number=19)
class BaseSymbol01_09_019_IndexThumbSideThumbUnit(SymbolGroup9IndexThumb):
    """01-09-019 "Index Thumb Side, Thumb Unit" -- base symbol 19 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=19, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(29), ip=JointAngle(24)),
            index=FingerPose(mcp=JointAngle(28), pip=JointAngle(6), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(45), pip=JointAngle(110), dip=JointAngle(21)),
            ring=FingerPose(mcp=JointAngle(47), pip=JointAngle(126), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(38), pip=JointAngle(135), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-020 "Index Thumb Side, Thumb Bent"
@register_symbol(group=9, base_symbol_number=20)
class BaseSymbol01_09_020_IndexThumbSideThumbBent(SymbolGroup9IndexThumb):
    """01-09-020 "Index Thumb Side, Thumb Bent" -- base symbol 20 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=20, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(34), ip=JointAngle(41)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(4), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(39), pip=JointAngle(111), dip=JointAngle(21)),
            ring=FingerPose(mcp=JointAngle(40), pip=JointAngle(129), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(30), pip=JointAngle(144), dip=JointAngle(16)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-021 "Index Thumb Side, Index Bent"
@register_symbol(group=9, base_symbol_number=21)
class BaseSymbol01_09_021_IndexThumbSideIndexBent(SymbolGroup9IndexThumb):
    """01-09-021 "Index Thumb Side, Index Bent" -- base symbol 21 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=21, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(12), ip=JointAngle(31)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(37), dip=JointAngle(55)),
            middle=FingerPose(mcp=JointAngle(60), pip=JointAngle(118), dip=JointAngle(58)),
            ring=FingerPose(mcp=JointAngle(65), pip=JointAngle(119), dip=JointAngle(65)),
            pinky=FingerPose(mcp=JointAngle(47), pip=JointAngle(130), dip=JointAngle(50)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-022 "Index Thumb Side, Both Bent"
@register_symbol(group=9, base_symbol_number=22)
class BaseSymbol01_09_022_IndexThumbSideBothBent(SymbolGroup9IndexThumb):
    """01-09-022 "Index Thumb Side, Both Bent" -- base symbol 22 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=22, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(26), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(53), pip=JointAngle(11), dip=JointAngle(29)),
            middle=FingerPose(mcp=JointAngle(63), pip=JointAngle(107), dip=JointAngle(56)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(112), dip=JointAngle(76)),
            pinky=FingerPose(mcp=JointAngle(71), pip=JointAngle(107), dip=JointAngle(61)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-023 "Index Thumb Side, Index Hinge"
@register_symbol(group=9, base_symbol_number=23)
class BaseSymbol01_09_023_IndexThumbSideIndexHinge(SymbolGroup9IndexThumb):
    """01-09-023 "Index Thumb Side, Index Hinge" -- base symbol 23 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=23, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(9), ip=JointAngle(27)),
            index=FingerPose(mcp=JointAngle(46), pip=JointAngle(7), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(46), pip=JointAngle(126), dip=JointAngle(32)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(133), dip=JointAngle(58)),
            pinky=FingerPose(mcp=JointAngle(37), pip=JointAngle(152), dip=JointAngle(38)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-024 "Index Thumb Forward, Index Straight"
@register_symbol(group=9, base_symbol_number=24)
class BaseSymbol01_09_024_IndexThumbForwardIndexStraight(SymbolGroup9IndexThumb):
    """01-09-024 "Index Thumb Forward, Index Straight" -- base symbol 24 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=24, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(42), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(36), pip=JointAngle(11), dip=JointAngle(12)),
            middle=FingerPose(mcp=JointAngle(40), pip=JointAngle(124), dip=JointAngle(30)),
            ring=FingerPose(mcp=JointAngle(49), pip=JointAngle(128), dip=JointAngle(55)),
            pinky=FingerPose(mcp=JointAngle(46), pip=JointAngle(131), dip=JointAngle(40)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-025 "Index Thumb Forward, Index Bent"
@register_symbol(group=9, base_symbol_number=25)
class BaseSymbol01_09_025_IndexThumbForwardIndexBent(SymbolGroup9IndexThumb):
    """01-09-025 "Index Thumb Forward, Index Bent" -- base symbol 25 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=25, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(35), ip=JointAngle(13)),
            index=FingerPose(mcp=JointAngle(36), pip=JointAngle(24), dip=JointAngle(65)),
            middle=FingerPose(mcp=JointAngle(56), pip=JointAngle(113), dip=JointAngle(42)),
            ring=FingerPose(mcp=JointAngle(58), pip=JointAngle(128), dip=JointAngle(58)),
            pinky=FingerPose(mcp=JointAngle(47), pip=JointAngle(131), dip=JointAngle(50)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-026 "Index Thumb Hook"
@register_symbol(group=9, base_symbol_number=26)
class BaseSymbol01_09_026_IndexThumbHook(SymbolGroup9IndexThumb):
    """01-09-026 "Index Thumb Hook" -- base symbol 26 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=26, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(42), mcp=JointAngle(39), ip=JointAngle(13)),
            index=FingerPose(mcp=JointAngle(41), pip=JointAngle(54), dip=JointAngle(48)),
            middle=FingerPose(mcp=JointAngle(69), pip=JointAngle(109), dip=JointAngle(74)),
            ring=FingerPose(mcp=JointAngle(68), pip=JointAngle(121), dip=JointAngle(76)),
            pinky=FingerPose(mcp=JointAngle(66), pip=JointAngle(113), dip=JointAngle(63)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-027 "Index Thumb Curlicue"
@register_symbol(group=9, base_symbol_number=27)
class BaseSymbol01_09_027_IndexThumbCurlicue(SymbolGroup9IndexThumb):
    """01-09-027 "Index Thumb Curlicue" -- base symbol 27 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=27, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(34), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(67), pip=JointAngle(78), dip=JointAngle(29)),
            middle=FingerPose(mcp=JointAngle(68), pip=JointAngle(106), dip=JointAngle(29)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(115), dip=JointAngle(44)),
            pinky=FingerPose(mcp=JointAngle(52), pip=JointAngle(135), dip=JointAngle(36)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-028 "Index Thumb Curve, Thumb Side"
@register_symbol(group=9, base_symbol_number=28)
class BaseSymbol01_09_028_IndexThumbCurveThumbSide(SymbolGroup9IndexThumb):
    """01-09-028 "Index Thumb Curve, Thumb Side" -- base symbol 28 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=28, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(29), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(65), pip=JointAngle(75), dip=JointAngle(18)),
            middle=FingerPose(mcp=JointAngle(68), pip=JointAngle(103), dip=JointAngle(45)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(119), dip=JointAngle(61)),
            pinky=FingerPose(mcp=JointAngle(49), pip=JointAngle(146), dip=JointAngle(42)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-029 "Index Thumb Curve, Thumb Inside on Claw"
@register_symbol(group=9, base_symbol_number=29)
class BaseSymbol01_09_029_IndexThumbCurveThumbInsideOnClaw(SymbolGroup9IndexThumb):
    """01-09-029 "Index Thumb Curve, Thumb Inside on Claw" -- base symbol 29 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=29, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(49), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(44), pip=JointAngle(77), dip=JointAngle(33)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(97), dip=JointAngle(38)),
            ring=FingerPose(mcp=JointAngle(28), pip=JointAngle(99), dip=JointAngle(50)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(92), dip=JointAngle(66)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-030 "Index Thumb Curve, Thumb Under"
@register_symbol(group=9, base_symbol_number=30)
class BaseSymbol01_09_030_IndexThumbCurveThumbUnder(SymbolGroup9IndexThumb):
    """01-09-030 "Index Thumb Curve, Thumb Under" -- base symbol 30 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=30, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(30), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(53), pip=JointAngle(34), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(65), pip=JointAngle(111), dip=JointAngle(51)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(121), dip=JointAngle(68)),
            pinky=FingerPose(mcp=JointAngle(64), pip=JointAngle(126), dip=JointAngle(52)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-031 "Index Thumb Circle"
@register_symbol(group=9, base_symbol_number=31)
class BaseSymbol01_09_031_IndexThumbCircle(SymbolGroup9IndexThumb):
    """01-09-031 "Index Thumb Circle" -- base symbol 31 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=31, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(40), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(54), pip=JointAngle(53), dip=JointAngle(35)),
            middle=FingerPose(mcp=JointAngle(67), pip=JointAngle(109), dip=JointAngle(76)),
            ring=FingerPose(mcp=JointAngle(71), pip=JointAngle(118), dip=JointAngle(75)),
            pinky=FingerPose(mcp=JointAngle(61), pip=JointAngle(123), dip=JointAngle(61)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-032 "Index Thumb Cup"
@register_symbol(group=9, base_symbol_number=32)
class BaseSymbol01_09_032_IndexThumbCup(SymbolGroup9IndexThumb):
    """01-09-032 "Index Thumb Cup" -- base symbol 32 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=32, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(54), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(39), pip=JointAngle(48), dip=JointAngle(54)),
            middle=FingerPose(mcp=JointAngle(59), pip=JointAngle(117), dip=JointAngle(65)),
            ring=FingerPose(mcp=JointAngle(62), pip=JointAngle(128), dip=JointAngle(73)),
            pinky=FingerPose(mcp=JointAngle(48), pip=JointAngle(132), dip=JointAngle(59)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-033 "Index Thumb Cup Open"
@register_symbol(group=9, base_symbol_number=33)
class BaseSymbol01_09_033_IndexThumbCupOpen(SymbolGroup9IndexThumb):
    """01-09-033 "Index Thumb Cup Open" -- base symbol 33 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=33, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(55), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(29), dip=JointAngle(57)),
            middle=FingerPose(mcp=JointAngle(62), pip=JointAngle(109), dip=JointAngle(53)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(116), dip=JointAngle(71)),
            pinky=FingerPose(mcp=JointAngle(60), pip=JointAngle(113), dip=JointAngle(64)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-034 "Index Thumb Hinge Open"
@register_symbol(group=9, base_symbol_number=34)
class BaseSymbol01_09_034_IndexThumbHingeOpen(SymbolGroup9IndexThumb):
    """01-09-034 "Index Thumb Hinge Open" -- base symbol 34 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=34, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(42), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(6), dip=JointAngle(0)),
            middle=FingerPose(mcp=JointAngle(52), pip=JointAngle(120), dip=JointAngle(25)),
            ring=FingerPose(mcp=JointAngle(47), pip=JointAngle(131), dip=JointAngle(38)),
            pinky=FingerPose(mcp=JointAngle(35), pip=JointAngle(138), dip=JointAngle(34)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-035 "Index Thumb Hinge Large"
@register_symbol(group=9, base_symbol_number=35)
class BaseSymbol01_09_035_IndexThumbHingeLarge(SymbolGroup9IndexThumb):
    """01-09-035 "Index Thumb Hinge Large" -- base symbol 35 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=35, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(43), mcp=JointAngle(48), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(63), pip=JointAngle(3), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(54), pip=JointAngle(119), dip=JointAngle(30)),
            ring=FingerPose(mcp=JointAngle(55), pip=JointAngle(128), dip=JointAngle(45)),
            pinky=FingerPose(mcp=JointAngle(48), pip=JointAngle(129), dip=JointAngle(43)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-036 "Index Thumb Hinge"
@register_symbol(group=9, base_symbol_number=36)
class BaseSymbol01_09_036_IndexThumbHinge(SymbolGroup9IndexThumb):
    """01-09-036 "Index Thumb Hinge" -- base symbol 36 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=36, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(46), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(65), pip=JointAngle(14), dip=JointAngle(17)),
            middle=FingerPose(mcp=JointAngle(75), pip=JointAngle(109), dip=JointAngle(83)),
            ring=FingerPose(mcp=JointAngle(82), pip=JointAngle(108), dip=JointAngle(79)),
            pinky=FingerPose(mcp=JointAngle(79), pip=JointAngle(100), dip=JointAngle(64)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-037 "Index Thumb Hinge Small"
@register_symbol(group=9, base_symbol_number=37)
class BaseSymbol01_09_037_IndexThumbHingeSmall(SymbolGroup9IndexThumb):
    """01-09-037 "Index Thumb Hinge Small" -- base symbol 37 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=37, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(37), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(68), pip=JointAngle(15), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(74), pip=JointAngle(105), dip=JointAngle(52)),
            ring=FingerPose(mcp=JointAngle(78), pip=JointAngle(110), dip=JointAngle(73)),
            pinky=FingerPose(mcp=JointAngle(70), pip=JointAngle(113), dip=JointAngle(58)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-038 "Index Thumb Angle Out"
@register_symbol(group=9, base_symbol_number=38)
class BaseSymbol01_09_038_IndexThumbAngleOut(SymbolGroup9IndexThumb):
    """01-09-038 "Index Thumb Angle Out" -- base symbol 38 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=38, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(32), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(58), pip=JointAngle(114), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(64), pip=JointAngle(127), dip=JointAngle(124)),
            ring=FingerPose(mcp=JointAngle(68), pip=JointAngle(128), dip=JointAngle(95)),
            pinky=FingerPose(mcp=JointAngle(47), pip=JointAngle(149), dip=JointAngle(50)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-039 "Index Thumb Angle In"
@register_symbol(group=9, base_symbol_number=39)
class BaseSymbol01_09_039_IndexThumbAngleIn(SymbolGroup9IndexThumb):
    """01-09-039 "Index Thumb Angle In" -- base symbol 39 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=39, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(42), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(94), pip=JointAngle(71), dip=JointAngle(44)),
            middle=FingerPose(mcp=JointAngle(83), pip=JointAngle(99), dip=JointAngle(83)),
            ring=FingerPose(mcp=JointAngle(79), pip=JointAngle(108), dip=JointAngle(86)),
            pinky=FingerPose(mcp=JointAngle(61), pip=JointAngle(126), dip=JointAngle(64)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-09-040 "Index Thumb Angle"
@register_symbol(group=9, base_symbol_number=40)
class BaseSymbol01_09_040_IndexThumbAngle(SymbolGroup9IndexThumb):
    """01-09-040 "Index Thumb Angle" -- base symbol 40 of Group 9."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=9, base_symbol_number=40, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(49), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(58), pip=JointAngle(39), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(60), pip=JointAngle(119), dip=JointAngle(99)),
            ring=FingerPose(mcp=JointAngle(61), pip=JointAngle(129), dip=JointAngle(83)),
            pinky=FingerPose(mcp=JointAngle(44), pip=JointAngle(146), dip=JointAngle(50)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


