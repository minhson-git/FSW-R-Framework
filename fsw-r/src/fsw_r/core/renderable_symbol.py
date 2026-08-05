"""Marker for "a symbol that some category's renderer can consume".

This used to declare an abstract ``get_joint_pose() -> HandJointPose``, but
that pose type is hand-specific -- a facial-expression symbol has no joint
pose (it's a blend-shape), and a movement symbol has a motion path. So the
concrete pose accessor now lives on each category's own subclass
(``HandSymbol.get_joint_pose()``, future ``FaceSymbol.get_expression()``,
``HeadSymbol.get_head_orientation()``), not here -- see ``PHASE4_PLAN.md``
(Bước 0). ``registry.build_symbol()`` and ``fswr_converter`` type against
this marker; each category's renderer narrows to its own concrete class.
"""

from __future__ import annotations

from abc import ABC

from fsw_r.core.fsw_base_symbol import FSWBaseSymbol


class FSWRenderableSymbol(FSWBaseSymbol, ABC):
    """A renderable ISWA symbol. Still abstract via ``FSWBaseSymbol``'s
    ``hand_side``; carries no pose contract of its own (pose shape is
    per-category)."""
