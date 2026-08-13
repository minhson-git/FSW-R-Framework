"""The fsw-r layer's render contract -- split per category, not
one-size-fits-all.

``FSWRenderableSymbol`` is a marker only: "this symbol renders to
*something* in 3D." It does NOT say what -- Category 1 (Hands) renders to
a ``HandJointPose``, Category 2 (Movement) to a ``MotionPath`` (a
trajectory description, not a set of joint angles), Category 4
(Head & Face) to a ``FaceExpressionPose`` (ARKit-52 blend-shapes), and
Category 5 (Trunk & Limb / Body) to a ``BodyPose`` (a schematic
body-diagram descriptor). Each category's own abstract subclass below
(``FSWHandRenderable``, ``FSWMotionRenderable``, ``FSWFaceRenderable``,
``FSWBodyRenderable``) declares the one ``get_*()`` contract that actually
makes sense for it -- so a renderer built for hands (``HandMeshRenderer3D``)
can require ``FSWHandRenderable`` specifically and never has to branch on
category or guess whether ``get_joint_pose()`` exists on whatever object it
was handed.

Category 3 (Dynamics) is deliberately NOT part of this tree at all --
``FSWModifierSymbol`` (``core/modifier_symbol.py``) is a sibling hierarchy
directly under ``FSWBaseSymbol``, because a Dynamics symbol (tempo/emphasis
for OTHER symbols in the same sign) renders to nothing of its own. See that
module's docstring.

This used to be a single class with ``get_joint_pose() -> HandJointPose``
as its one abstract method -- which meant a Category 2 symbol (no joint
angles at all) literally could not have inherited it. Splitting this was
the first thing done for Category 2, before any ``MovementSymbol`` code --
see PROGRESS.md's Phase 2 entry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from scipy.spatial.transform import Rotation

from fsw_r.core.body_types import BodyPose
from fsw_r.core.face_types import FaceExpressionPose
from fsw_r.core.fsw_base_symbol import FSWBaseSymbol
from fsw_r.core.types import FingerArticulation, HandJointPose, MotionPath


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

    @abstractmethod
    def get_finger_articulation(self) -> FingerArticulation | None:
        """How the finger JOINTS move over time, for a Group 12 (Finger
        Movement, ``PathType.FINGER``) symbol -- ``None`` for every other
        path type (this project's own "khớp ngón" task, see
        ``core/finger_articulation.py``). Declared as its own abstract
        method (required on every ``FSWMotionRenderable``, not just Group
        12's) rather than a separate contract class: ``MotionPath`` itself
        stays the one required per-symbol trajectory description for ALL
        of Category 2, and ``FingerArticulation`` is the (usually absent)
        EXTRA per-symbol detail specific to one ``path_type`` -- same
        shape as ``get_wrist_orientation()`` already being one required
        method shared across all of Category 2 regardless of path_type."""
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


class FSWBodyRenderable(FSWRenderableSymbol, ABC):
    @abstractmethod
    def get_body_pose(self) -> BodyPose:
        """Schematic body-diagram descriptor for a Category 5 (Trunk &
        Limb) symbol -- not joint angles (``FSWHandRenderable``), not a
        trajectory (``FSWMotionRenderable``), and not a rigid single-part
        orientation (``FSWHeadRenderable``) -- see ``BodyPose``'s own
        docstring for why this category's real structure doesn't fit any
        of those."""
        raise NotImplementedError
