"""The contract for a symbol that modifies OTHER symbols in a sign instead
of rendering a pose of its own -- currently just Category 3 (Dynamics:
tempo/emphasis).

Deliberately NOT part of the ``FSWRenderableSymbol`` tree
(``core/renderable_symbol.py``): that whole hierarchy exists to answer "this
symbol renders to *something* in 3D, here's what" -- ``FSWHandRenderable``,
``FSWMotionRenderable``, ``FSWFaceRenderable``, ``FSWHeadRenderable``,
``FSWBodyRenderable`` all declare a ``get_*() -> <pose type>`` contract.
A Dynamics symbol has no pose of its own at all; forcing it to answer
``get_joint_pose()``-shaped questions (or adding a
``FSWDynamicsRenderable`` with a `get_dynamics_modifier()` next to the
others) would misrepresent it as "one more thing that renders," when its
actual job is changing how OTHER symbols in the same sign are interpreted
(speed/repeat/tension/alternation) -- a cross-cutting annotation, not a
shape. ``FSWModifierSymbol`` is a sibling hierarchy directly under
``FSWBaseSymbol`` instead, matching what the symbol actually is.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from fsw_r.core.dynamics_types import DynamicsModifier
from fsw_r.core.fsw_base_symbol import FSWBaseSymbol


class FSWModifierSymbol(FSWBaseSymbol, ABC):
    @abstractmethod
    def get_modifier(self) -> DynamicsModifier:
        """This symbol's authored effect on the sign's timing/manner -- see
        ``DynamicsModifier``'s own docstring."""
        raise NotImplementedError
