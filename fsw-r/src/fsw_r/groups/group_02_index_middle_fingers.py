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


# 01-02-002 "Index Middle on Circle"
@register_symbol(group=2, base_symbol_number=2)
class BaseSymbol01_02_002_IndexMiddleOnCircle(SymbolGroup2IndexMiddleFingers):
    """01-02-002 "Index Middle on Circle" -- base symbol 2 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(56), mcp=JointAngle(43), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(2), pip=JointAngle(1), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(6), pip=JointAngle(9), dip=JointAngle(6)),
            ring=FingerPose(mcp=JointAngle(43), pip=JointAngle(87), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(54), pip=JointAngle(68), dip=JointAngle(37)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-003 "Index Middle Bent"
@register_symbol(group=2, base_symbol_number=3)
class BaseSymbol01_02_003_IndexMiddleBent(SymbolGroup2IndexMiddleFingers):
    """01-02-003 "Index Middle Bent" -- base symbol 3 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(52), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(32), pip=JointAngle(47), dip=JointAngle(71)),
            middle=FingerPose(mcp=JointAngle(32), pip=JointAngle(50), dip=JointAngle(72)),
            ring=FingerPose(mcp=JointAngle(61), pip=JointAngle(92), dip=JointAngle(32)),
            pinky=FingerPose(mcp=JointAngle(49), pip=JointAngle(112), dip=JointAngle(25)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-004 "Index Middle Raised Knuckles"
@register_symbol(group=2, base_symbol_number=4)
class BaseSymbol01_02_004_IndexMiddleRaisedKnuckles(SymbolGroup2IndexMiddleFingers):
    """01-02-004 "Index Middle Raised Knuckles" -- base symbol 4 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(64), ip=JointAngle(39)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(122), dip=JointAngle(14)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(141), dip=JointAngle(34)),
            ring=FingerPose(mcp=JointAngle(52), pip=JointAngle(127), dip=JointAngle(63)),
            pinky=FingerPose(mcp=JointAngle(47), pip=JointAngle(139), dip=JointAngle(46)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-005 "Index Middle Hinge"
@register_symbol(group=2, base_symbol_number=5)
class BaseSymbol01_02_005_IndexMiddleHinge(SymbolGroup2IndexMiddleFingers):
    """01-02-005 "Index Middle Hinge" -- base symbol 5 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(44), mcp=JointAngle(54), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(25), pip=JointAngle(11), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(8), dip=JointAngle(8)),
            ring=FingerPose(mcp=JointAngle(55), pip=JointAngle(114), dip=JointAngle(27)),
            pinky=FingerPose(mcp=JointAngle(59), pip=JointAngle(106), dip=JointAngle(23)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-006 "Index Up, Middle Hinge"
@register_symbol(group=2, base_symbol_number=6)
class BaseSymbol01_02_006_IndexUpMiddleHinge(SymbolGroup2IndexMiddleFingers):
    """01-02-006 "Index Up, Middle Hinge" -- base symbol 6 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(66), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(21), pip=JointAngle(4), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(19), dip=JointAngle(15)),
            ring=FingerPose(mcp=JointAngle(59), pip=JointAngle(111), dip=JointAngle(29)),
            pinky=FingerPose(mcp=JointAngle(58), pip=JointAngle(107), dip=JointAngle(27)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-007 "Index Hinge, Middle Up"
@register_symbol(group=2, base_symbol_number=7)
class BaseSymbol01_02_007_IndexHingeMiddleUp(SymbolGroup2IndexMiddleFingers):
    """01-02-007 "Index Hinge, Middle Up" -- base symbol 7 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(56), ip=JointAngle(13)),
            index=FingerPose(mcp=JointAngle(55), pip=JointAngle(41), dip=JointAngle(22)),
            middle=FingerPose(mcp=JointAngle(22), pip=JointAngle(6), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(51), pip=JointAngle(113), dip=JointAngle(28)),
            pinky=FingerPose(mcp=JointAngle(42), pip=JointAngle(134), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-008 "Index Middle Unit"
@register_symbol(group=2, base_symbol_number=8)
class BaseSymbol01_02_008_IndexMiddleUnit(SymbolGroup2IndexMiddleFingers):
    """01-02-008 "Index Middle Unit" -- base symbol 8 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(56), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(22), pip=JointAngle(5), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(13), pip=JointAngle(5), dip=JointAngle(10)),
            ring=FingerPose(mcp=JointAngle(42), pip=JointAngle(120), dip=JointAngle(22)),
            pinky=FingerPose(mcp=JointAngle(42), pip=JointAngle(121), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-009 "Index Middle Unit, Index Bent"
@register_symbol(group=2, base_symbol_number=9)
class BaseSymbol01_02_009_IndexMiddleUnitIndexBent(SymbolGroup2IndexMiddleFingers):
    """01-02-009 "Index Middle Unit, Index Bent" -- base symbol 9 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(45), mcp=JointAngle(45), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(27), pip=JointAngle(56), dip=JointAngle(54)),
            middle=FingerPose(mcp=JointAngle(15), pip=JointAngle(14), dip=JointAngle(10)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(112), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(48), pip=JointAngle(119), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-010 "Index Middle Unit, Middle Bent"
@register_symbol(group=2, base_symbol_number=10)
class BaseSymbol01_02_010_IndexMiddleUnitMiddleBent(SymbolGroup2IndexMiddleFingers):
    """01-02-010 "Index Middle Unit, Middle Bent" -- base symbol 10 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(53), mcp=JointAngle(45), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(19), pip=JointAngle(7), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(61), dip=JointAngle(69)),
            ring=FingerPose(mcp=JointAngle(56), pip=JointAngle(87), dip=JointAngle(31)),
            pinky=FingerPose(mcp=JointAngle(60), pip=JointAngle(83), dip=JointAngle(25)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-011 "Index Middle Unit Cup"
@register_symbol(group=2, base_symbol_number=11)
class BaseSymbol01_02_011_IndexMiddleUnitCup(SymbolGroup2IndexMiddleFingers):
    """01-02-011 "Index Middle Unit Cup" -- base symbol 11 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(50), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(36), dip=JointAngle(42)),
            middle=FingerPose(mcp=JointAngle(27), pip=JointAngle(73), dip=JointAngle(37)),
            ring=FingerPose(mcp=JointAngle(53), pip=JointAngle(90), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(62), pip=JointAngle(74), dip=JointAngle(32)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-012 "Index Middle Unit Hinge"
@register_symbol(group=2, base_symbol_number=12)
class BaseSymbol01_02_012_IndexMiddleUnitHinge(SymbolGroup2IndexMiddleFingers):
    """01-02-012 "Index Middle Unit Hinge" -- base symbol 12 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(31), mcp=JointAngle(68), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(36), pip=JointAngle(18), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(26), pip=JointAngle(14), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(58), pip=JointAngle(109), dip=JointAngle(21)),
            pinky=FingerPose(mcp=JointAngle(53), pip=JointAngle(116), dip=JointAngle(16)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-013 "Index Middle Cross"
@register_symbol(group=2, base_symbol_number=13)
class BaseSymbol01_02_013_IndexMiddleCross(SymbolGroup2IndexMiddleFingers):
    """01-02-013 "Index Middle Cross" -- base symbol 13 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(51), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(4), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(15), pip=JointAngle(12), dip=JointAngle(10)),
            ring=FingerPose(mcp=JointAngle(53), pip=JointAngle(105), dip=JointAngle(27)),
            pinky=FingerPose(mcp=JointAngle(61), pip=JointAngle(98), dip=JointAngle(25)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-014 "Index Middle Cross On Circle"
@register_symbol(group=2, base_symbol_number=14)
class BaseSymbol01_02_014_IndexMiddleCrossOnCircle(SymbolGroup2IndexMiddleFingers):
    """01-02-014 "Index Middle Cross On Circle" -- base symbol 14 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(47), mcp=JointAngle(43), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(9), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(39), pip=JointAngle(81), dip=JointAngle(45)),
            ring=FingerPose(mcp=JointAngle(48), pip=JointAngle(78), dip=JointAngle(22)),
            pinky=FingerPose(mcp=JointAngle(57), pip=JointAngle(64), dip=JointAngle(34)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-015 "Middle Bent Over Index"
@register_symbol(group=2, base_symbol_number=15)
class BaseSymbol01_02_015_MiddleBentOverIndex(SymbolGroup2IndexMiddleFingers):
    """01-02-015 "Middle Bent Over Index" -- base symbol 15 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(45), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(42), pip=JointAngle(5), dip=JointAngle(11)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(8), dip=JointAngle(12)),
            ring=FingerPose(mcp=JointAngle(57), pip=JointAngle(107), dip=JointAngle(35)),
            pinky=FingerPose(mcp=JointAngle(68), pip=JointAngle(99), dip=JointAngle(25)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-02-016 "Index Bent Over Middle"
@register_symbol(group=2, base_symbol_number=16)
class BaseSymbol01_02_016_IndexBentOverMiddle(SymbolGroup2IndexMiddleFingers):
    """01-02-016 "Index Bent Over Middle" -- base symbol 16 of Group 2."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=2, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(49), mcp=JointAngle(47), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(8), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(20), pip=JointAngle(8), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(58), pip=JointAngle(106), dip=JointAngle(32)),
            pinky=FingerPose(mcp=JointAngle(55), pip=JointAngle(119), dip=JointAngle(20)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


