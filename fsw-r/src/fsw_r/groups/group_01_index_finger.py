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
    """01-01-007 "Index Bent" -- base symbol 7 of Group 1.

    Angles are real data (same source/method as the group docstring), from
    dataset symbol "01-01-007", all five digits independently -- unlike an
    earlier version of this class, the other four fingers are NOT borrowed
    from the "Index" (01-01-001) template: the measured differences there
    (e.g. pinky pip 118 vs. 140, dip 58 vs. 30) are too large to dismiss as
    photo-to-photo noise, so this symbol gets its own full measurement like
    every other of the 261 base symbols, rather than a partial override.
    """

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(39), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(32), pip=JointAngle(46), dip=JointAngle(69)),
            middle=FingerPose(mcp=JointAngle(65), pip=JointAngle(114), dip=JointAngle(51)),
            ring=FingerPose(mcp=JointAngle(69), pip=JointAngle(120), dip=JointAngle(71)),
            pinky=FingerPose(mcp=JointAngle(65), pip=JointAngle(118), dip=JointAngle(58)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-002 "Index on Circle"
@register_symbol(group=1, base_symbol_number=2)
class BaseSymbol01_01_002_IndexOnCircle(SymbolGroup1IndexFinger):
    """01-01-002 "Index on Circle" -- base symbol 2 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=2, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(37), mcp=JointAngle(27), ip=JointAngle(22)),
            index=FingerPose(mcp=JointAngle(10), pip=JointAngle(8), dip=JointAngle(4)),
            middle=FingerPose(mcp=JointAngle(43), pip=JointAngle(73), dip=JointAngle(26)),
            ring=FingerPose(mcp=JointAngle(42), pip=JointAngle(79), dip=JointAngle(46)),
            pinky=FingerPose(mcp=JointAngle(36), pip=JointAngle(75), dip=JointAngle(53)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-003 "Index on Cup"
@register_symbol(group=1, base_symbol_number=3)
class BaseSymbol01_01_003_IndexOnCup(SymbolGroup1IndexFinger):
    """01-01-003 "Index on Cup" -- base symbol 3 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=3, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(23), mcp=JointAngle(32), ip=JointAngle(17)),
            index=FingerPose(mcp=JointAngle(10), pip=JointAngle(15), dip=JointAngle(14)),
            middle=FingerPose(mcp=JointAngle(25), pip=JointAngle(41), dip=JointAngle(24)),
            ring=FingerPose(mcp=JointAngle(25), pip=JointAngle(36), dip=JointAngle(36)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(24), dip=JointAngle(36)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-004 "Index on Oval"
@register_symbol(group=1, base_symbol_number=4)
class BaseSymbol01_01_004_IndexOnOval(SymbolGroup1IndexFinger):
    """01-01-004 "Index on Oval" -- base symbol 4 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=4, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(51), mcp=JointAngle(41), ip=JointAngle(3)),
            index=FingerPose(mcp=JointAngle(19), pip=JointAngle(6), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(54), pip=JointAngle(51), dip=JointAngle(19)),
            ring=FingerPose(mcp=JointAngle(47), pip=JointAngle(50), dip=JointAngle(24)),
            pinky=FingerPose(mcp=JointAngle(44), pip=JointAngle(40), dip=JointAngle(29)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-005 "Index on Hinge"
@register_symbol(group=1, base_symbol_number=5)
class BaseSymbol01_01_005_IndexOnHinge(SymbolGroup1IndexFinger):
    """01-01-005 "Index on Hinge" -- base symbol 5 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=5, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(32), mcp=JointAngle(45), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(20), pip=JointAngle(9), dip=JointAngle(8)),
            middle=FingerPose(mcp=JointAngle(53), pip=JointAngle(30), dip=JointAngle(5)),
            ring=FingerPose(mcp=JointAngle(47), pip=JointAngle(20), dip=JointAngle(11)),
            pinky=FingerPose(mcp=JointAngle(52), pip=JointAngle(9), dip=JointAngle(9)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-006 "Index on Angle"
@register_symbol(group=1, base_symbol_number=6)
class BaseSymbol01_01_006_IndexOnAngle(SymbolGroup1IndexFinger):
    """01-01-006 "Index on Angle" -- base symbol 6 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=6, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(50), mcp=JointAngle(35), ip=JointAngle(10)),
            index=FingerPose(mcp=JointAngle(14), pip=JointAngle(10), dip=JointAngle(9)),
            middle=FingerPose(mcp=JointAngle(53), pip=JointAngle(37), dip=JointAngle(11)),
            ring=FingerPose(mcp=JointAngle(53), pip=JointAngle(27), dip=JointAngle(17)),
            pinky=FingerPose(mcp=JointAngle(51), pip=JointAngle(16), dip=JointAngle(11)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-008 "Index Bent on Circle"
@register_symbol(group=1, base_symbol_number=8)
class BaseSymbol01_01_008_IndexBentOnCircle(SymbolGroup1IndexFinger):
    """01-01-008 "Index Bent on Circle" -- base symbol 8 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=8, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(41), ip=JointAngle(9)),
            index=FingerPose(mcp=JointAngle(17), pip=JointAngle(27), dip=JointAngle(58)),
            middle=FingerPose(mcp=JointAngle(46), pip=JointAngle(67), dip=JointAngle(31)),
            ring=FingerPose(mcp=JointAngle(49), pip=JointAngle(63), dip=JointAngle(42)),
            pinky=FingerPose(mcp=JointAngle(54), pip=JointAngle(57), dip=JointAngle(39)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-009 "Index Bent on Fist, Thumb Under"
@register_symbol(group=1, base_symbol_number=9)
class BaseSymbol01_01_009_IndexBentOnFistThumbUnder(SymbolGroup1IndexFinger):
    """01-01-009 "Index Bent on Fist, Thumb Under" -- base symbol 9 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=9, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(33), mcp=JointAngle(52), ip=JointAngle(39)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(22), dip=JointAngle(83)),
            middle=FingerPose(mcp=JointAngle(56), pip=JointAngle(99), dip=JointAngle(29)),
            ring=FingerPose(mcp=JointAngle(60), pip=JointAngle(111), dip=JointAngle(33)),
            pinky=FingerPose(mcp=JointAngle(51), pip=JointAngle(112), dip=JointAngle(35)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-010 "Index Cup"
@register_symbol(group=1, base_symbol_number=10)
class BaseSymbol01_01_010_IndexCup(SymbolGroup1IndexFinger):
    """01-01-010 "Index Cup" -- base symbol 10 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=10, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(58), ip=JointAngle(37)),
            index=FingerPose(mcp=JointAngle(46), pip=JointAngle(120), dip=JointAngle(10)),
            middle=FingerPose(mcp=JointAngle(52), pip=JointAngle(127), dip=JointAngle(80)),
            ring=FingerPose(mcp=JointAngle(50), pip=JointAngle(135), dip=JointAngle(74)),
            pinky=FingerPose(mcp=JointAngle(34), pip=JointAngle(154), dip=JointAngle(46)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-011 "Index Cup"
@register_symbol(group=1, base_symbol_number=11)
class BaseSymbol01_01_011_IndexCup(SymbolGroup1IndexFinger):
    """01-01-011 "Index Cup" -- base symbol 11 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=11, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(42), ip=JointAngle(11)),
            index=FingerPose(mcp=JointAngle(36), pip=JointAngle(34), dip=JointAngle(56)),
            middle=FingerPose(mcp=JointAngle(62), pip=JointAngle(122), dip=JointAngle(50)),
            ring=FingerPose(mcp=JointAngle(67), pip=JointAngle(129), dip=JointAngle(61)),
            pinky=FingerPose(mcp=JointAngle(51), pip=JointAngle(135), dip=JointAngle(47)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-012 "Index Hinge"
@register_symbol(group=1, base_symbol_number=12)
class BaseSymbol01_01_012_IndexHinge(SymbolGroup1IndexFinger):
    """01-01-012 "Index Hinge" -- base symbol 12 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=12, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(39), mcp=JointAngle(57), ip=JointAngle(15)),
            index=FingerPose(mcp=JointAngle(39), pip=JointAngle(8), dip=JointAngle(6)),
            middle=FingerPose(mcp=JointAngle(54), pip=JointAngle(127), dip=JointAngle(29)),
            ring=FingerPose(mcp=JointAngle(61), pip=JointAngle(120), dip=JointAngle(47)),
            pinky=FingerPose(mcp=JointAngle(49), pip=JointAngle(135), dip=JointAngle(29)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-013 "Index Hinge Low"
@register_symbol(group=1, base_symbol_number=13)
class BaseSymbol01_01_013_IndexHingeLow(SymbolGroup1IndexFinger):
    """01-01-013 "Index Hinge Low" -- base symbol 13 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=13, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(36), mcp=JointAngle(64), ip=JointAngle(19)),
            index=FingerPose(mcp=JointAngle(58), pip=JointAngle(24), dip=JointAngle(20)),
            middle=FingerPose(mcp=JointAngle(59), pip=JointAngle(119), dip=JointAngle(27)),
            ring=FingerPose(mcp=JointAngle(59), pip=JointAngle(125), dip=JointAngle(49)),
            pinky=FingerPose(mcp=JointAngle(39), pip=JointAngle(144), dip=JointAngle(26)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()


# 01-01-014 "Index Hinge on Circle"
@register_symbol(group=1, base_symbol_number=14)
class BaseSymbol01_01_014_IndexHingeOnCircle(SymbolGroup1IndexFinger):
    """01-01-014 "Index Hinge on Circle" -- base symbol 14 of Group 1."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=14, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(46), mcp=JointAngle(46), ip=JointAngle(4)),
            index=FingerPose(mcp=JointAngle(34), pip=JointAngle(14), dip=JointAngle(5)),
            middle=FingerPose(mcp=JointAngle(39), pip=JointAngle(76), dip=JointAngle(26)),
            ring=FingerPose(mcp=JointAngle(39), pip=JointAngle(73), dip=JointAngle(34)),
            pinky=FingerPose(mcp=JointAngle(37), pip=JointAngle(69), dip=JointAngle(40)),
        )

    def get_wrist_orientation(self) -> Rotation:
        return self._default_wrist_orientation()
