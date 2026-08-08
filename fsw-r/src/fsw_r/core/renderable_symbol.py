"""The fsw-r layer's render contract -- split per category, not
one-size-fits-all.

``FSWRenderableSymbol`` is a marker only: "this symbol renders to
*something* in 3D." It does NOT say what -- Category 1 (Hands) renders to
a ``HandJointPose``, Category 2 (Movement) to a ``MotionPath`` (a
trajectory description, not a set of joint angles), and future categories
will have their own pose types again (e.g. Head & Face's blend-shapes).
Each category's own abstract subclass below (``FSWHandRenderable``,
``FSWMotionRenderable``) declares the one ``get_*()`` contract that
actually makes sense for it -- so a renderer built for hands
(``HandMeshRenderer3D``) can require ``FSWHandRenderable`` specifically and
never has to branch on category or guess whether ``get_joint_pose()``
exists on whatever object it was handed.

This used to be a single class with ``get_joint_pose() -> HandJointPose``
as its one abstract method -- which meant a Category 2 symbol (no joint
angles at all) literally could not have inherited it. Splitting this was
the first thing done for Category 2, before any ``MovementSymbol`` code --
see PROGRESS.md's Phase 2 entry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from fsw_r.core.fsw_base_symbol import FSWBaseSymbol
from fsw_r.core.types import HandJointPose, MotionPath


class FSWRenderableSymbol(FSWBaseSymbol, ABC):
    """Marker only: this symbol renders to *something* in 3D. Says nothing
    about what that is -- see ``FSWHandRenderable`` / ``FSWMotionRenderable``
    for the actual per-category contracts."""


class FSWHandRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_joint_pose(self) -> HandJointPose:
        """Flexion/abduction angles for all five fingers, for forward
        kinematics on a rigged 3D hand."""
        raise NotImplementedError


class FSWMotionRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_motion_path(self) -> MotionPath:
        """The trajectory (path type, plane, curvature, ...) this Category
        2 (Movement) symbol describes -- not a static pose."""
        raise NotImplementedError
