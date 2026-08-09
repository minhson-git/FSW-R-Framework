"""A single class for all 18 Category 5 (Trunk & Limb / "Body") base
symbols -- the Category 5 analogue of ``hand_symbol.py``'s ``HandSymbol``
and ``movement_symbol.py``'s ``MovementSymbol``. Looks its own body pose up
in ``core/pose_table.py``'s ``BODY_POSE_TABLE`` by ``base_hex``, same
pattern as those two.
"""

from __future__ import annotations

from fsw_r.core.body_types import BodyPose
from fsw_r.core.pose_table import BODY_POSE_TABLE
from fsw_r.core.renderable_symbol import FSWBodyRenderable
from fsw_r.core.types import HandSide


class BodySymbol(FSWBodyRenderable):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        """Deliberately ``None`` -- a trunk/limb symbol describes the body
        as a whole (or a generic limb, not tied to a specific hand), not a
        performing hand. Measured on sign-language-processing/
        signbank-plus (257,800 signs): Category 5's fill/rotation
        distribution (92.5% fill=0, 88.7% rotation 0-7) is far more skewed
        than either Category 1's (where rotation cleanly splits RIGHT/LEFT)
        or Category 2's (which at least splits ~60/40) -- there is no
        comparable signal here to even guess a hand-side rule from, unlike
        Category 2 where a real (if noisy) correlation exists. See
        ``BodyPose``'s module docstring for the same finding from the pose
        side."""
        return None

    def get_body_pose(self) -> BodyPose:
        return BODY_POSE_TABLE[self.base_hex]
