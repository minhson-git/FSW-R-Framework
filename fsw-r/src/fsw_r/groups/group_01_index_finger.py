"""Symbol Group 1 -- Index Finger.

ASL handshape "1": index finger extended straight, the other three fingers
curled into the fist, thumb pressed against the side of the hand.

The angle values below are a starting baseline only -- they will need
tuning against the actual rig/mesh once one is available.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import replace

from scipy.spatial.transform import Rotation

from fsw_r.core.registry import register_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import FingerPose, HandJointPose, JointAngle, ThumbPose


class SymbolGroup1IndexFinger(FSWRenderableSymbol, ABC):
    def _default_joint_pose(self) -> HandJointPose:
        curled_into_fist = FingerPose(
            mcp=JointAngle(flexion=90),
            pip=JointAngle(flexion=100),
            dip=JointAngle(flexion=80),
        )
        straight = FingerPose(
            mcp=JointAngle(flexion=0),
            pip=JointAngle(flexion=0),
            dip=JointAngle(flexion=0),
        )
        return HandJointPose(
            thumb=ThumbPose(cmc=JointAngle(20), mcp=JointAngle(15), ip=JointAngle(10)),
            index=straight,
            middle=curled_into_fist,
            ring=curled_into_fist,
            pinky=curled_into_fist,
        )

    # Default: base symbols that don't need a distinct pose use the group template as-is.
    def get_joint_pose(self) -> HandJointPose:
        return self._default_joint_pose()


@register_symbol(group=1, base_symbol_number=1)
class BaseSymbol01_01_001_Index(SymbolGroup1IndexFinger):
    """01-01-001 "Index". "Six Palm Facings" -- rotation selects one of six
    wrist orientations; the joint pose itself never changes."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=1, fill=fill, rotation=rotation)

    def get_wrist_orientation(self) -> Rotation:
        # TODO: replace with the real logic already present in the system's FSWBaseSymbol.
        # Mock: ISWA `rotation` spins the glyph in the plane of the page --
        # like a clock hand, 0/45/.../315 degrees -- it does not tilt the hand
        # out of the page. The axis perpendicular to the page (the one
        # pointing at the viewer) is z in this frame, so the rotation must be
        # about z, not y. Rotating about y would tip the hand into depth,
        # which is what looked wrong.
        return Rotation.from_euler("z", self._rotation_angle_degrees(), degrees=True)


@register_symbol(group=1, base_symbol_number=7)
class BaseSymbol01_01_007_IndexBent(SymbolGroup1IndexFinger):
    """01-01-007 "Index Bent". Illustrates why the default joint template
    lives on the group while the override lives on the base symbol: this
    variant only differs from "Index" in the index finger's PIP flexion."""

    def __init__(self, fill: int, rotation: int) -> None:
        super().__init__(category=1, group=1, base_symbol_number=7, fill=fill, rotation=rotation)

    def get_joint_pose(self) -> HandJointPose:
        base = self._default_joint_pose()
        bent_index = FingerPose(
            mcp=JointAngle(flexion=0),
            pip=JointAngle(flexion=90),
            dip=JointAngle(flexion=0),
        )
        return replace(base, index=bent_index)

    def get_wrist_orientation(self) -> Rotation:
        return Rotation.from_euler("z", self._rotation_angle_degrees(), degrees=True)
