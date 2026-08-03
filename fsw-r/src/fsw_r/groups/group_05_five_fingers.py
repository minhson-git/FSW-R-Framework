"""Symbol Group 5 -- Five Fingers.

Confirmed against the real symbol photo at
https://www.signwriting.org/lessons/iswa/group05/01-05-001-01.html: all
five fingers (including thumb) extended straight and spread apart -- an
open hand.

The angle values below are derived from real data, not guessed: median 3D
hand keypoints (MediaPipe v0.10.3, 48 crops) from
github.com/sign-language-processing/3d-hands-benchmark, symbol "01-05-001"
("Five Fingers Spread"), orientation 1 (fill=0, Palm of Hand/Wall Plane).
See group_01_index_finger.py's docstring for the exact method and caveats.
`abduction` (finger spread) isn't measured by this method -- still a
guess, kept from the original baseline.
"""

from __future__ import annotations

from abc import ABC

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup5FiveFingers(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26, abduction=25), mcp=JointAngle(4), ip=JointAngle(26)),
            index=FingerPose(mcp=JointAngle(8, abduction=8), pip=JointAngle(8), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(5, abduction=8), pip=JointAngle(8), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(9, abduction=8), pip=JointAngle(4), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(9, abduction=8), pip=JointAngle(5), dip=JointAngle(6)),
        )

    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=5, base_symbol_number=1)
class BaseSymbol01_05_001_FiveFingersSpread(SymbolGroup5FiveFingers):
    """01-05-001 "Five Fingers Spread" -- base symbol 1 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-002 "Five Fingers Spread Heel"
@register_symbol(group=5, base_symbol_number=2)
class BaseSymbol01_05_002_FiveFingersSpreadHeel(SymbolGroup5FiveFingers):
    """01-05-002 "Five Fingers Spread Heel" -- base symbol 2 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(19), mcp=JointAngle(11), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(21), pip=JointAngle(6), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(4), pip=JointAngle(14), dip=JointAngle(6)),
            ring=FingerPose(mcp=JointAngle(15), pip=JointAngle(30), dip=JointAngle(10)),
            pinky=FingerPose(mcp=JointAngle(9), pip=JointAngle(12), dip=JointAngle(10)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-003 "Five Fingers Spread, 4-Bent"
@register_symbol(group=5, base_symbol_number=3)
class BaseSymbol01_05_003_FiveFingersSpread4Bent(SymbolGroup5FiveFingers):
    """01-05-003 "Five Fingers Spread, 4-Bent" -- base symbol 3 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(30), mcp=JointAngle(2), ip=JointAngle(29)),
            index=FingerPose(mcp=JointAngle(25), pip=JointAngle(33), dip=JointAngle(65)),
            middle=FingerPose(mcp=JointAngle(22), pip=JointAngle(31), dip=JointAngle(77)),
            ring=FingerPose(mcp=JointAngle(19), pip=JointAngle(21), dip=JointAngle(99)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(5), dip=JointAngle(64)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-004 "Five Fingers Spread Four Bent Heel"
@register_symbol(group=5, base_symbol_number=4)
class BaseSymbol01_05_004_FiveFingersSpreadFourBentHeel(SymbolGroup5FiveFingers):
    """01-05-004 "Five Fingers Spread Four Bent Heel" -- base symbol 4 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(9), mcp=JointAngle(26), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(30), pip=JointAngle(26), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(33), dip=JointAngle(15)),
            ring=FingerPose(mcp=JointAngle(52), pip=JointAngle(14), dip=JointAngle(18)),
            pinky=FingerPose(mcp=JointAngle(44), pip=JointAngle(31), dip=JointAngle(27)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-005 "Five Fingers Spread All Bent"
@register_symbol(group=5, base_symbol_number=5)
class BaseSymbol01_05_005_FiveFingersSpreadAllBent(SymbolGroup5FiveFingers):
    """01-05-005 "Five Fingers Spread All Bent" -- base symbol 5 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(56), ip=JointAngle(30)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(27), dip=JointAngle(60)),
            middle=FingerPose(mcp=JointAngle(17), pip=JointAngle(25), dip=JointAngle(61)),
            ring=FingerPose(mcp=JointAngle(17), pip=JointAngle(19), dip=JointAngle(75)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(10), dip=JointAngle(37)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-006 "Five Fingers Spread All Bent Heel"
@register_symbol(group=5, base_symbol_number=6)
class BaseSymbol01_05_006_FiveFingersSpreadAllBentHeel(SymbolGroup5FiveFingers):
    """01-05-006 "Five Fingers Spread All Bent Heel" -- base symbol 6 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(25), mcp=JointAngle(42), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(21), pip=JointAngle(22), dip=JointAngle(14)),
            middle=FingerPose(mcp=JointAngle(20), pip=JointAngle(61), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(30), pip=JointAngle(57), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(14), pip=JointAngle(50), dip=JointAngle(30)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-007 "Five Fingers Spread Thumb Forward"
@register_symbol(group=5, base_symbol_number=7)
class BaseSymbol01_05_007_FiveFingersSpreadThumbForward(SymbolGroup5FiveFingers):
    """01-05-007 "Five Fingers Spread Thumb Forward" -- base symbol 7 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(19), mcp=JointAngle(45), ip=JointAngle(34)),
            index=FingerPose(mcp=JointAngle(7), pip=JointAngle(6), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(3), pip=JointAngle(6), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(5), pip=JointAngle(5), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(3), pip=JointAngle(5), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-008 "Five Fingers Spread Cup"
@register_symbol(group=5, base_symbol_number=8)
class BaseSymbol01_05_008_FiveFingersSpreadCup(SymbolGroup5FiveFingers):
    """01-05-008 "Five Fingers Spread Cup" -- base symbol 8 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(48), ip=JointAngle(33)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(49), dip=JointAngle(54)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(40), dip=JointAngle(65)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(32), dip=JointAngle(90)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(7), dip=JointAngle(49)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-009 "Five Fingers Spread Cup Open"
@register_symbol(group=5, base_symbol_number=9)
class BaseSymbol01_05_009_FiveFingersSpreadCupOpen(SymbolGroup5FiveFingers):
    """01-05-009 "Five Fingers Spread Cup Open" -- base symbol 9 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(53), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(37), dip=JointAngle(58)),
            middle=FingerPose(mcp=JointAngle(17), pip=JointAngle(28), dip=JointAngle(69)),
            ring=FingerPose(mcp=JointAngle(16), pip=JointAngle(13), dip=JointAngle(86)),
            pinky=FingerPose(mcp=JointAngle(23), pip=JointAngle(1), dip=JointAngle(30)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-010 "Five Fingers Spread Hinge Open"
@register_symbol(group=5, base_symbol_number=10)
class BaseSymbol01_05_010_FiveFingersSpreadHingeOpen(SymbolGroup5FiveFingers):
    """01-05-010 "Five Fingers Spread Hinge Open" -- base symbol 10 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(58), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(19), pip=JointAngle(22), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(14), pip=JointAngle(21), dip=JointAngle(20)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(4), dip=JointAngle(12)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(3), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-011 "Five Fingers Spread Oval"
@register_symbol(group=5, base_symbol_number=11)
class BaseSymbol01_05_011_FiveFingersSpreadOval(SymbolGroup5FiveFingers):
    """01-05-011 "Five Fingers Spread Oval" -- base symbol 11 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(54), mcp=JointAngle(38), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(37), dip=JointAngle(36)),
            middle=FingerPose(mcp=JointAngle(21), pip=JointAngle(31), dip=JointAngle(9)),
            ring=FingerPose(mcp=JointAngle(39), pip=JointAngle(38), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(33), pip=JointAngle(38), dip=JointAngle(56)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-012 "Five Fingers Spread Hinge"
@register_symbol(group=5, base_symbol_number=12)
class BaseSymbol01_05_012_FiveFingersSpreadHinge(SymbolGroup5FiveFingers):
    """01-05-012 "Five Fingers Spread Hinge" -- base symbol 12 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(59), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(30), pip=JointAngle(31), dip=JointAngle(19)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(30), dip=JointAngle(17)),
            ring=FingerPose(mcp=JointAngle(28), pip=JointAngle(14), dip=JointAngle(15)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(5), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-013 "Five Fingers Spread Hinge, Thumb Side"
@register_symbol(group=5, base_symbol_number=13)
class BaseSymbol01_05_013_FiveFingersSpreadHingeThumbSide(SymbolGroup5FiveFingers):
    """01-05-013 "Five Fingers Spread Hinge, Thumb Side" -- base symbol 13 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(25), mcp=JointAngle(5), ip=JointAngle(26)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(34), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(21), pip=JointAngle(23), dip=JointAngle(13)),
            ring=FingerPose(mcp=JointAngle(24), pip=JointAngle(9), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(9), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-014 "Five Fingers Spread Hinge, No Thumb"
@register_symbol(group=5, base_symbol_number=14)
class BaseSymbol01_05_014_FiveFingersSpreadHingeNoThumb(SymbolGroup5FiveFingers):
    """01-05-014 "Five Fingers Spread Hinge, No Thumb" -- base symbol 14 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(31), ip=JointAngle(12)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(33), dip=JointAngle(15)),
            middle=FingerPose(mcp=JointAngle(48), pip=JointAngle(25), dip=JointAngle(15)),
            ring=FingerPose(mcp=JointAngle(48), pip=JointAngle(16), dip=JointAngle(19)),
            pinky=FingerPose(mcp=JointAngle(41), pip=JointAngle(14), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-015 "Flat Hand"
@register_symbol(group=5, base_symbol_number=15)
class BaseSymbol01_05_015_FlatHand(SymbolGroup5FiveFingers):
    """01-05-015 "Flat Hand" -- base symbol 15 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=15, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(34), ip=JointAngle(1)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(11), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(9), pip=JointAngle(11), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(7), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(9), dip=JointAngle(4)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-016 "Flat Hand, In-Between Palm Facings"
@register_symbol(group=5, base_symbol_number=16)
class BaseSymbol01_05_016_FlatHandInBetweenPalmFacings(SymbolGroup5FiveFingers):
    """01-05-016 "Flat Hand, In-Between Palm Facings" -- base symbol 16 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=16, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(43), mcp=JointAngle(28), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(7), dip=JointAngle(2)),
            middle=FingerPose(mcp=JointAngle(13), pip=JointAngle(10), dip=JointAngle(4)),
            ring=FingerPose(mcp=JointAngle(2), pip=JointAngle(18), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(13), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-017 "Flat Hand, Heel"
@register_symbol(group=5, base_symbol_number=17)
class BaseSymbol01_05_017_FlatHandHeel(SymbolGroup5FiveFingers):
    """01-05-017 "Flat Hand, Heel" -- base symbol 17 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=17, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(21), mcp=JointAngle(17), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(3), pip=JointAngle(19), dip=JointAngle(7)),
            middle=FingerPose(mcp=JointAngle(6), pip=JointAngle(17), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(16), pip=JointAngle(63), dip=JointAngle(57)),
            pinky=FingerPose(mcp=JointAngle(28), pip=JointAngle(49), dip=JointAngle(19)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-018 "Flat Thumb Side"
@register_symbol(group=5, base_symbol_number=18)
class BaseSymbol01_05_018_FlatThumbSide(SymbolGroup5FiveFingers):
    """01-05-018 "Flat Thumb Side" -- base symbol 18 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=18, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(6), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(9), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(7), pip=JointAngle(6), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(4), dip=JointAngle(2)),
            pinky=FingerPose(mcp=JointAngle(19), pip=JointAngle(11), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-019 "Flat Thumb Side, Heel"
@register_symbol(group=5, base_symbol_number=19)
class BaseSymbol01_05_019_FlatThumbSideHeel(SymbolGroup5FiveFingers):
    """01-05-019 "Flat Thumb Side, Heel" -- base symbol 19 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=19, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(20), mcp=JointAngle(5), ip=JointAngle(22)),
            index=FingerPose(mcp=JointAngle(8), pip=JointAngle(6), dip=JointAngle(25)),
            middle=FingerPose(mcp=JointAngle(15), pip=JointAngle(23), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(25), pip=JointAngle(37), dip=JointAngle(75)),
            pinky=FingerPose(mcp=JointAngle(37), pip=JointAngle(23), dip=JointAngle(10)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-020 "Flat Thumb Bent"
@register_symbol(group=5, base_symbol_number=20)
class BaseSymbol01_05_020_FlatThumbBent(SymbolGroup5FiveFingers):
    """01-05-020 "Flat Thumb Bent" -- base symbol 20 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=20, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(27), mcp=JointAngle(19), ip=JointAngle(36)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(9), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(9), pip=JointAngle(6), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(7), pip=JointAngle(3), dip=JointAngle(2)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(9), dip=JointAngle(4)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-021 "Flat Thumb Forward"
@register_symbol(group=5, base_symbol_number=21)
class BaseSymbol01_05_021_FlatThumbForward(SymbolGroup5FiveFingers):
    """01-05-021 "Flat Thumb Forward" -- base symbol 21 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=21, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(24), mcp=JointAngle(46), ip=JointAngle(25)),
            index=FingerPose(mcp=JointAngle(16), pip=JointAngle(8), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(3), pip=JointAngle(8), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(7), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(8), dip=JointAngle(4)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-022 "Flat Split, Index Thumb Side"
@register_symbol(group=5, base_symbol_number=22)
class BaseSymbol01_05_022_FlatSplitIndexThumbSide(SymbolGroup5FiveFingers):
    """01-05-022 "Flat Split, Index Thumb Side" -- base symbol 22 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=22, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(22), mcp=JointAngle(5), ip=JointAngle(28)),
            index=FingerPose(mcp=JointAngle(10), pip=JointAngle(9), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(11), pip=JointAngle(6), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(5), pip=JointAngle(5), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(17), pip=JointAngle(11), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-023 "Flat Split Center"
@register_symbol(group=5, base_symbol_number=23)
class BaseSymbol01_05_023_FlatSplitCenter(SymbolGroup5FiveFingers):
    """01-05-023 "Flat Split Center" -- base symbol 23 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=23, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(32), ip=JointAngle(18)),
            index=FingerPose(mcp=JointAngle(13), pip=JointAngle(8), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(8), pip=JointAngle(8), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(12), pip=JointAngle(1), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(8), pip=JointAngle(10), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-024 "Flat Split Center Thumb Side"
@register_symbol(group=5, base_symbol_number=24)
class BaseSymbol01_05_024_FlatSplitCenterThumbSide(SymbolGroup5FiveFingers):
    """01-05-024 "Flat Split Center Thumb Side" -- base symbol 24 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=24, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(25), mcp=JointAngle(4), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(12), pip=JointAngle(10), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(6), pip=JointAngle(8), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(11), pip=JointAngle(1), dip=JointAngle(6)),
            pinky=FingerPose(mcp=JointAngle(4), pip=JointAngle(9), dip=JointAngle(3)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-025 "Flat Split Center Thumb Side Bent"
@register_symbol(group=5, base_symbol_number=25)
class BaseSymbol01_05_025_FlatSplitCenterThumbSideBent(SymbolGroup5FiveFingers):
    """01-05-025 "Flat Split Center Thumb Side Bent" -- base symbol 25 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=25, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(23), ip=JointAngle(35)),
            index=FingerPose(mcp=JointAngle(13), pip=JointAngle(9), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(7), pip=JointAngle(6), dip=JointAngle(3)),
            ring=FingerPose(mcp=JointAngle(10), pip=JointAngle(1), dip=JointAngle(5)),
            pinky=FingerPose(mcp=JointAngle(9), pip=JointAngle(9), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-026 "Flat Split Baby"
@register_symbol(group=5, base_symbol_number=26)
class BaseSymbol01_05_026_FlatSplitBaby(SymbolGroup5FiveFingers):
    """01-05-026 "Flat Split Baby" -- base symbol 26 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=26, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(33), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(17), pip=JointAngle(9), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(5), pip=JointAngle(8), dip=JointAngle(1)),
            ring=FingerPose(mcp=JointAngle(13), pip=JointAngle(7), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(10), pip=JointAngle(8), dip=JointAngle(8)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-027 "Claw"
@register_symbol(group=5, base_symbol_number=27)
class BaseSymbol01_05_027_Claw(SymbolGroup5FiveFingers):
    """01-05-027 "Claw" -- base symbol 27 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=27, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(48), mcp=JointAngle(48), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(25), pip=JointAngle(78), dip=JointAngle(37)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(86), dip=JointAngle(24)),
            ring=FingerPose(mcp=JointAngle(18), pip=JointAngle(87), dip=JointAngle(43)),
            pinky=FingerPose(mcp=JointAngle(18), pip=JointAngle(82), dip=JointAngle(52)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-028 "Claw Thumb Side"
@register_symbol(group=5, base_symbol_number=28)
class BaseSymbol01_05_028_ClawThumbSide(SymbolGroup5FiveFingers):
    """01-05-028 "Claw Thumb Side" -- base symbol 28 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=28, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(6), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(63), dip=JointAngle(53)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(74), dip=JointAngle(44)),
            ring=FingerPose(mcp=JointAngle(24), pip=JointAngle(67), dip=JointAngle(56)),
            pinky=FingerPose(mcp=JointAngle(26), pip=JointAngle(59), dip=JointAngle(58)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-029 "Claw No Thumb"
@register_symbol(group=5, base_symbol_number=29)
class BaseSymbol01_05_029_ClawNoThumb(SymbolGroup5FiveFingers):
    """01-05-029 "Claw No Thumb" -- base symbol 29 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=29, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(31), ip=JointAngle(43)),
            index=FingerPose(mcp=JointAngle(31), pip=JointAngle(46), dip=JointAngle(61)),
            middle=FingerPose(mcp=JointAngle(30), pip=JointAngle(62), dip=JointAngle(52)),
            ring=FingerPose(mcp=JointAngle(28), pip=JointAngle(55), dip=JointAngle(66)),
            pinky=FingerPose(mcp=JointAngle(26), pip=JointAngle(44), dip=JointAngle(70)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-030 "Claw Thumb Forward"
@register_symbol(group=5, base_symbol_number=30)
class BaseSymbol01_05_030_ClawThumbForward(SymbolGroup5FiveFingers):
    """01-05-030 "Claw Thumb Forward" -- base symbol 30 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=30, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(28), mcp=JointAngle(30), ip=JointAngle(1)),
            index=FingerPose(mcp=JointAngle(9), pip=JointAngle(23), dip=JointAngle(20)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(13), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(38), pip=JointAngle(17), dip=JointAngle(9)),
            pinky=FingerPose(mcp=JointAngle(47), pip=JointAngle(18), dip=JointAngle(6)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-031 "Hook Curlicue"
@register_symbol(group=5, base_symbol_number=31)
class BaseSymbol01_05_031_HookCurlicue(SymbolGroup5FiveFingers):
    """01-05-031 "Hook Curlicue" -- base symbol 31 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=31, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(59), mcp=JointAngle(25), ip=JointAngle(7)),
            index=FingerPose(mcp=JointAngle(36), pip=JointAngle(102), dip=JointAngle(42)),
            middle=FingerPose(mcp=JointAngle(28), pip=JointAngle(106), dip=JointAngle(27)),
            ring=FingerPose(mcp=JointAngle(30), pip=JointAngle(97), dip=JointAngle(35)),
            pinky=FingerPose(mcp=JointAngle(31), pip=JointAngle(84), dip=JointAngle(57)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-032 "Hook"
@register_symbol(group=5, base_symbol_number=32)
class BaseSymbol01_05_032_Hook(SymbolGroup5FiveFingers):
    """01-05-032 "Hook" -- base symbol 32 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=32, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(59), mcp=JointAngle(27), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(19), pip=JointAngle(90), dip=JointAngle(33)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(81), dip=JointAngle(28)),
            ring=FingerPose(mcp=JointAngle(35), pip=JointAngle(80), dip=JointAngle(34)),
            pinky=FingerPose(mcp=JointAngle(38), pip=JointAngle(64), dip=JointAngle(49)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-033 "Open Cup"
@register_symbol(group=5, base_symbol_number=33)
class BaseSymbol01_05_033_OpenCup(SymbolGroup5FiveFingers):
    """01-05-033 "Open Cup" -- base symbol 33 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=33, fill=fill, rotation=rotation)

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


# 01-05-034 "Cup"
@register_symbol(group=5, base_symbol_number=34)
class BaseSymbol01_05_034_Cup(SymbolGroup5FiveFingers):
    """01-05-034 "Cup" -- base symbol 34 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=34, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(46), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(28), pip=JointAngle(43), dip=JointAngle(29)),
            middle=FingerPose(mcp=JointAngle(22), pip=JointAngle(47), dip=JointAngle(33)),
            ring=FingerPose(mcp=JointAngle(21), pip=JointAngle(39), dip=JointAngle(49)),
            pinky=FingerPose(mcp=JointAngle(24), pip=JointAngle(20), dip=JointAngle(47)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-035 "Open Cup Thumb Side"
@register_symbol(group=5, base_symbol_number=35)
class BaseSymbol01_05_035_OpenCupThumbSide(SymbolGroup5FiveFingers):
    """01-05-035 "Open Cup Thumb Side" -- base symbol 35 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=35, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(10), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(30), pip=JointAngle(26), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(20), pip=JointAngle(31), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(13), pip=JointAngle(30), dip=JointAngle(14)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(16), dip=JointAngle(13)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-036 "Cup Thumb Side"
@register_symbol(group=5, base_symbol_number=36)
class BaseSymbol01_05_036_CupThumbSide(SymbolGroup5FiveFingers):
    """01-05-036 "Cup Thumb Side" -- base symbol 36 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=36, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(34), mcp=JointAngle(20), ip=JointAngle(13)),
            index=FingerPose(mcp=JointAngle(59), pip=JointAngle(33), dip=JointAngle(11)),
            middle=FingerPose(mcp=JointAngle(55), pip=JointAngle(35), dip=JointAngle(38)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(48), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(56), pip=JointAngle(57), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-037 "Open Cup No Thumb"
@register_symbol(group=5, base_symbol_number=37)
class BaseSymbol01_05_037_OpenCupNoThumb(SymbolGroup5FiveFingers):
    """01-05-037 "Open Cup No Thumb" -- base symbol 37 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=37, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(27), mcp=JointAngle(33), ip=JointAngle(23)),
            index=FingerPose(mcp=JointAngle(33), pip=JointAngle(21), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(23), pip=JointAngle(32), dip=JointAngle(25)),
            ring=FingerPose(mcp=JointAngle(19), pip=JointAngle(19), dip=JointAngle(51)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(6), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-038 "Cup No Thumb"
@register_symbol(group=5, base_symbol_number=38)
class BaseSymbol01_05_038_CupNoThumb(SymbolGroup5FiveFingers):
    """01-05-038 "Cup No Thumb" -- base symbol 38 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=38, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(34), ip=JointAngle(36)),
            index=FingerPose(mcp=JointAngle(36), pip=JointAngle(47), dip=JointAngle(47)),
            middle=FingerPose(mcp=JointAngle(32), pip=JointAngle(55), dip=JointAngle(47)),
            ring=FingerPose(mcp=JointAngle(29), pip=JointAngle(38), dip=JointAngle(78)),
            pinky=FingerPose(mcp=JointAngle(26), pip=JointAngle(21), dip=JointAngle(78)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-039 "Open Cup Thumb Forward"
@register_symbol(group=5, base_symbol_number=39)
class BaseSymbol01_05_039_OpenCupThumbForward(SymbolGroup5FiveFingers):
    """01-05-039 "Open Cup Thumb Forward" -- base symbol 39 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=39, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(25), mcp=JointAngle(45), ip=JointAngle(5)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(15), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(18), pip=JointAngle(22), dip=JointAngle(8)),
            ring=FingerPose(mcp=JointAngle(9), pip=JointAngle(23), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(25), pip=JointAngle(16), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-040 "Cup Thumb Forward"
@register_symbol(group=5, base_symbol_number=40)
class BaseSymbol01_05_040_CupThumbForward(SymbolGroup5FiveFingers):
    """01-05-040 "Cup Thumb Forward" -- base symbol 40 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=40, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(37), ip=JointAngle(2)),
            index=FingerPose(mcp=JointAngle(37), pip=JointAngle(56), dip=JointAngle(31)),
            middle=FingerPose(mcp=JointAngle(19), pip=JointAngle(71), dip=JointAngle(30)),
            ring=FingerPose(mcp=JointAngle(23), pip=JointAngle(65), dip=JointAngle(35)),
            pinky=FingerPose(mcp=JointAngle(33), pip=JointAngle(46), dip=JointAngle(45)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-041 "Open Curlicue"
@register_symbol(group=5, base_symbol_number=41)
class BaseSymbol01_05_041_OpenCurlicue(SymbolGroup5FiveFingers):
    """01-05-041 "Open Curlicue" -- base symbol 41 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=41, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(38), mcp=JointAngle(38), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(42), pip=JointAngle(82), dip=JointAngle(44)),
            middle=FingerPose(mcp=JointAngle(29), pip=JointAngle(105), dip=JointAngle(36)),
            ring=FingerPose(mcp=JointAngle(19), pip=JointAngle(112), dip=JointAngle(44)),
            pinky=FingerPose(mcp=JointAngle(14), pip=JointAngle(128), dip=JointAngle(38)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-042 "Curlicue"
@register_symbol(group=5, base_symbol_number=42)
class BaseSymbol01_05_042_Curlicue(SymbolGroup5FiveFingers):
    """01-05-042 "Curlicue" -- base symbol 42 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=42, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(26), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(50), pip=JointAngle(102), dip=JointAngle(32)),
            middle=FingerPose(mcp=JointAngle(35), pip=JointAngle(130), dip=JointAngle(23)),
            ring=FingerPose(mcp=JointAngle(24), pip=JointAngle(153), dip=JointAngle(16)),
            pinky=FingerPose(mcp=JointAngle(22), pip=JointAngle(148), dip=JointAngle(39)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-043 "Circle"
@register_symbol(group=5, base_symbol_number=43)
class BaseSymbol01_05_043_Circle(SymbolGroup5FiveFingers):
    """01-05-043 "Circle" -- base symbol 43 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=43, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(48), ip=JointAngle(14)),
            index=FingerPose(mcp=JointAngle(43), pip=JointAngle(80), dip=JointAngle(35)),
            middle=FingerPose(mcp=JointAngle(32), pip=JointAngle(94), dip=JointAngle(26)),
            ring=FingerPose(mcp=JointAngle(28), pip=JointAngle(85), dip=JointAngle(39)),
            pinky=FingerPose(mcp=JointAngle(28), pip=JointAngle(71), dip=JointAngle(55)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-044 "Oval"
@register_symbol(group=5, base_symbol_number=44)
class BaseSymbol01_05_044_Oval(SymbolGroup5FiveFingers):
    """01-05-044 "Oval" -- base symbol 44 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=44, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(40), mcp=JointAngle(37), ip=JointAngle(8)),
            index=FingerPose(mcp=JointAngle(57), pip=JointAngle(62), dip=JointAngle(32)),
            middle=FingerPose(mcp=JointAngle(45), pip=JointAngle(69), dip=JointAngle(21)),
            ring=FingerPose(mcp=JointAngle(40), pip=JointAngle(58), dip=JointAngle(38)),
            pinky=FingerPose(mcp=JointAngle(36), pip=JointAngle(44), dip=JointAngle(39)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-045 "Oval Thumb Side"
@register_symbol(group=5, base_symbol_number=45)
class BaseSymbol01_05_045_OvalThumbSide(SymbolGroup5FiveFingers):
    """01-05-045 "Oval Thumb Side" -- base symbol 45 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=45, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(12), ip=JointAngle(20)),
            index=FingerPose(mcp=JointAngle(81), pip=JointAngle(48), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(64), pip=JointAngle(58), dip=JointAngle(22)),
            ring=FingerPose(mcp=JointAngle(55), pip=JointAngle(61), dip=JointAngle(34)),
            pinky=FingerPose(mcp=JointAngle(45), pip=JointAngle(62), dip=JointAngle(36)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-046 "Oval No Thumb"
@register_symbol(group=5, base_symbol_number=46)
class BaseSymbol01_05_046_OvalNoThumb(SymbolGroup5FiveFingers):
    """01-05-046 "Oval No Thumb" -- base symbol 46 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=46, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(35), mcp=JointAngle(29), ip=JointAngle(6)),
            index=FingerPose(mcp=JointAngle(49), pip=JointAngle(55), dip=JointAngle(33)),
            middle=FingerPose(mcp=JointAngle(41), pip=JointAngle(61), dip=JointAngle(40)),
            ring=FingerPose(mcp=JointAngle(37), pip=JointAngle(50), dip=JointAngle(65)),
            pinky=FingerPose(mcp=JointAngle(32), pip=JointAngle(26), dip=JointAngle(60)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-047 "Oval Thumb Forward"
@register_symbol(group=5, base_symbol_number=47)
class BaseSymbol01_05_047_OvalThumbForward(SymbolGroup5FiveFingers):
    """01-05-047 "Oval Thumb Forward" -- base symbol 47 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=47, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(41), mcp=JointAngle(50), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(66), pip=JointAngle(50), dip=JointAngle(16)),
            middle=FingerPose(mcp=JointAngle(47), pip=JointAngle(57), dip=JointAngle(19)),
            ring=FingerPose(mcp=JointAngle(41), pip=JointAngle(52), dip=JointAngle(25)),
            pinky=FingerPose(mcp=JointAngle(37), pip=JointAngle(44), dip=JointAngle(28)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-048 "Open Hinge"
@register_symbol(group=5, base_symbol_number=48)
class BaseSymbol01_05_048_OpenHinge(SymbolGroup5FiveFingers):
    """01-05-048 "Open Hinge" -- base symbol 48 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=48, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(14), mcp=JointAngle(15), ip=JointAngle(21)),
            index=FingerPose(mcp=JointAngle(23), pip=JointAngle(8), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(10), pip=JointAngle(7), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(4), pip=JointAngle(7), dip=JointAngle(2)),
            pinky=FingerPose(mcp=JointAngle(17), pip=JointAngle(11), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-049 "Open Hinge Thumb Forward"
@register_symbol(group=5, base_symbol_number=49)
class BaseSymbol01_05_049_OpenHingeThumbForward(SymbolGroup5FiveFingers):
    """01-05-049 "Open Hinge Thumb Forward" -- base symbol 49 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=49, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(24), mcp=JointAngle(60), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(25), pip=JointAngle(9), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(9), pip=JointAngle(7), dip=JointAngle(0)),
            ring=FingerPose(mcp=JointAngle(6), pip=JointAngle(8), dip=JointAngle(2)),
            pinky=FingerPose(mcp=JointAngle(21), pip=JointAngle(9), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-050 "Hinge"
@register_symbol(group=5, base_symbol_number=50)
class BaseSymbol01_05_050_Hinge(SymbolGroup5FiveFingers):
    """01-05-050 "Hinge" -- base symbol 50 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=50, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(46), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(48), pip=JointAngle(15), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(36), pip=JointAngle(17), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(32), pip=JointAngle(7), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(30), pip=JointAngle(6), dip=JointAngle(21)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-051 "Small Hinge"
@register_symbol(group=5, base_symbol_number=51)
class BaseSymbol01_05_051_SmallHinge(SymbolGroup5FiveFingers):
    """01-05-051 "Small Hinge" -- base symbol 51 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=51, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(46), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(47), pip=JointAngle(33), dip=JointAngle(14)),
            middle=FingerPose(mcp=JointAngle(30), pip=JointAngle(47), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(27), pip=JointAngle(29), dip=JointAngle(49)),
            pinky=FingerPose(mcp=JointAngle(23), pip=JointAngle(12), dip=JointAngle(12)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-052 "Open Hinge Thumb Side"
@register_symbol(group=5, base_symbol_number=52)
class BaseSymbol01_05_052_OpenHingeThumbSide(SymbolGroup5FiveFingers):
    """01-05-052 "Open Hinge Thumb Side" -- base symbol 52 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=52, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(29), mcp=JointAngle(13), ip=JointAngle(27)),
            index=FingerPose(mcp=JointAngle(26), pip=JointAngle(12), dip=JointAngle(3)),
            middle=FingerPose(mcp=JointAngle(12), pip=JointAngle(10), dip=JointAngle(2)),
            ring=FingerPose(mcp=JointAngle(8), pip=JointAngle(3), dip=JointAngle(3)),
            pinky=FingerPose(mcp=JointAngle(20), pip=JointAngle(9), dip=JointAngle(2)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-053 "Hinge Thumb Side"
@register_symbol(group=5, base_symbol_number=53)
class BaseSymbol01_05_053_HingeThumbSide(SymbolGroup5FiveFingers):
    """01-05-053 "Hinge Thumb Side" -- base symbol 53 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=53, fill=fill, rotation=rotation)

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


# 01-05-054 "Open Hinge No Thumb"
@register_symbol(group=5, base_symbol_number=54)
class BaseSymbol01_05_054_OpenHingeNoThumb(SymbolGroup5FiveFingers):
    """01-05-054 "Open Hinge No Thumb" -- base symbol 54 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=54, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(22), mcp=JointAngle(31), ip=JointAngle(34)),
            index=FingerPose(mcp=JointAngle(38), pip=JointAngle(14), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(24), pip=JointAngle(15), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(16), pip=JointAngle(3), dip=JointAngle(4)),
            pinky=FingerPose(mcp=JointAngle(16), pip=JointAngle(5), dip=JointAngle(5)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-055 "Hinge No Thumb"
@register_symbol(group=5, base_symbol_number=55)
class BaseSymbol01_05_055_HingeNoThumb(SymbolGroup5FiveFingers):
    """01-05-055 "Hinge No Thumb" -- base symbol 55 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=55, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(26), mcp=JointAngle(30), ip=JointAngle(32)),
            index=FingerPose(mcp=JointAngle(56), pip=JointAngle(46), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(47), pip=JointAngle(42), dip=JointAngle(9)),
            ring=FingerPose(mcp=JointAngle(43), pip=JointAngle(32), dip=JointAngle(28)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(17), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-056 "Hinge Thumb Side Touches Index"
@register_symbol(group=5, base_symbol_number=56)
class BaseSymbol01_05_056_HingeThumbSideTouchesIndex(SymbolGroup5FiveFingers):
    """01-05-056 "Hinge Thumb Side Touches Index" -- base symbol 56 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=56, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(24), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(58), pip=JointAngle(43), dip=JointAngle(14)),
            middle=FingerPose(mcp=JointAngle(51), pip=JointAngle(48), dip=JointAngle(18)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(37), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(48), pip=JointAngle(23), dip=JointAngle(22)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-057 "Hinge Thumb Between Middle Ring"
@register_symbol(group=5, base_symbol_number=57)
class BaseSymbol01_05_057_HingeThumbBetweenMiddleRing(SymbolGroup5FiveFingers):
    """01-05-057 "Hinge Thumb Between Middle Ring" -- base symbol 57 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=57, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(45), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(60), pip=JointAngle(28), dip=JointAngle(13)),
            middle=FingerPose(mcp=JointAngle(50), pip=JointAngle(37), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(47), pip=JointAngle(23), dip=JointAngle(27)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(11), dip=JointAngle(7)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-05-058 "Angle"
@register_symbol(group=5, base_symbol_number=58)
class BaseSymbol01_05_058_Angle(SymbolGroup5FiveFingers):
    """01-05-058 "Angle" -- base symbol 58 of Group 5."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=5, base_symbol_number=58, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(30), ip=JointAngle(2)),
            index=FingerPose(mcp=JointAngle(70), pip=JointAngle(22), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(59), pip=JointAngle(31), dip=JointAngle(9)),
            ring=FingerPose(mcp=JointAngle(45), pip=JointAngle(29), dip=JointAngle(23)),
            pinky=FingerPose(mcp=JointAngle(39), pip=JointAngle(22), dip=JointAngle(17)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


