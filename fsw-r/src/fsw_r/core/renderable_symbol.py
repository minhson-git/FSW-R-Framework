"""The fsw-r layer's render contract -- split per category, not
one-size-fits-all.

``FSWRenderableSymbol`` is a marker only: "this symbol renders to
*something* in 3D." It does NOT say what -- Category 1 (Hands) renders to
a ``HandJointPose``, Category 2 (Movement) to a ``MotionPath`` (a
trajectory description, not a set of joint angles), and Category 4
(Head & Face) to a ``FaceExpressionPose`` (ARKit-52 blend-shapes). Each
category's own abstract subclass below (``FSWHandRenderable``,
``FSWMotionRenderable``, ``FSWFaceRenderable``) declares the one
``get_*()`` contract that actually makes sense for it -- so a renderer built
for hands (``HandMeshRenderer3D``) can require ``FSWHandRenderable``
specifically and never has to branch on category or guess whether
``get_joint_pose()`` exists on whatever object it was handed.

This used to be a single class with ``get_joint_pose() -> HandJointPose``
as its one abstract method -- which meant a Category 2 symbol (no joint
angles at all) literally could not have inherited it. Splitting this was
the first thing done for Category 2, before any ``MovementSymbol`` code --
see PROGRESS.md's Phase 2 entry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from scipy.spatial.transform import Rotation

from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.fsw_base_symbol import FSWBaseSymbol
from fsw_r.core.types import HandJointPose, MotionPath


class FSWRenderableSymbol(FSWBaseSymbol, ABC):
    """Marker only: this symbol renders to *something* in 3D. Says nothing
    about what that is -- see ``FSWHandRenderable`` / ``FSWMotionRenderable``
    / ``FSWFaceRenderable`` for the actual per-category contracts."""


class FSWHandRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_joint_pose(self) -> HandJointPose:
        """Flexion/abduction angles for all five fingers, for forward
        kinematics on a rigged 3D hand."""
        raise NotImplementedError

    @abstractmethod
    def get_wrist_orientation(self) -> Rotation:
        """Wrist/hand orientation derived from fill/rotation (ISWA) -- see
        ``FSWBaseSymbol._default_wrist_orientation()`` for the shared
        formula. Declared here, not on the base, because a face has no
        rigid orientation to expose."""
        raise NotImplementedError


class FSWMotionRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_motion_path(self) -> MotionPath:
        """The trajectory (path type, plane, curvature, ...) this Category
        2 (Movement) symbol describes -- not a static pose."""
        raise NotImplementedError

    @abstractmethod
    def get_wrist_orientation(self) -> Rotation:
        """Orientation the movement is performed in (reuses Category 1's
        fill/rotation formula, unverified for Movement -- see
        ``MovementSymbol.get_wrist_orientation``)."""
        raise NotImplementedError


class FSWFaceRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_expression(self) -> FaceExpressionPose:
        """ARKit-52 blend-shape weights for this Category 4 (Head & Face)
        facial-expression symbol -- a face is deformed by morph targets, not
        a rigid skeleton of joint angles."""
        raise NotImplementedError


class FSWHeadRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_head_orientation(self) -> Rotation:
        """Rigid 3D orientation of the head (pitch/yaw/roll) for a Category 4
        Group 22 head symbol -- a head is oriented as a whole, not deformed
        (that's ``get_expression``) -- see ``head_symbol.py``."""
        raise NotImplementedError
