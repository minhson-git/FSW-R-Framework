"""The fsw-r layer's new contract: joint pose for 3D rigging."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fsw_r.core.fsw_base_symbol import FSWBaseSymbol
from fsw_r.core.types import HandJointPose


class FSWRenderableSymbol(FSWBaseSymbol, ABC):
    @abstractmethod
    def get_joint_pose(self) -> HandJointPose:
        """Flexion/abduction angles for all five fingers, for forward
        kinematics on a rigged 3D hand."""
        raise NotImplementedError
