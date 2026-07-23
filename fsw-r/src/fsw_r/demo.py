"""Demo, in two parts:

1. Parse four *real* FSW symbol keys for Base Symbol 1 ("Index", 01-01-001)
   -- three in the 0-7 (RIGHT hand) half and one in the 8-15 (LEFT hand)
   half -- via symbol_from_fsw(), and confirm:
     - joint pose stays identical regardless of rotation/hand_side.
     - wrist orientation changes with rotation.
     - hand_side is decoded correctly and the renderer picks the matching
       rig (RIGHT vs LEFT), rather than mirroring a single rig via rotation.

2. Parse a full, real *FSW sign string* (box marker + two positioned
   symbols -- a two-handed sign) through the whole pipeline: the real
   sutton-signwriting parser (fsw_ast.parse_fsw_to_ast) produces an AST,
   which fswr_converter.ast_to_fswr converts into actual FSWRenderableSymbol
   instances, each still carrying its page position.

Run with: python -m fsw_r.demo
"""

from __future__ import annotations

from scipy.spatial.transform import Rotation

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.renderer import HandMeshRenderer3D, HandSkeleton
from fsw_r.core.types import HandJointPose, HandSide

# Importing this populates the registry that symbol_from_fsw() and
# fsw_to_fswr() look up -- see core/registry.py.
import fsw_r.groups.group_01_index_finger  # noqa: F401


class _MockRig:
    """Stand-in for a real rigged mesh (e.g. in Blender/Open3D)."""

    def __init__(self, label: str) -> None:
        self._label = label

    def apply_wrist_orientation(self, rotation: Rotation) -> None:
        print(f"  [{self._label}] wrist quat (x,y,z,w):", rotation.as_quat())

    def apply_joint_pose(self, pose: HandJointPose) -> None:
        print(f"  [{self._label}] joint pose:", pose)


class _MockRigProvider:
    """Two genuinely separate rigs -- not one rig mirrored via rotation."""

    def __init__(self) -> None:
        self._right = _MockRig("RIGHT rig")
        self._left = _MockRig("LEFT rig")

    def get_rig(self, hand_side: HandSide) -> HandSkeleton:
        return self._right if hand_side == HandSide.RIGHT else self._left


def main() -> None:
    # Real FSW symbol keys for "Index" (base 0x100), fill=1: "S100" + fill + rotation.
    idx_front = symbol_from_fsw("S10010")  # rotation=0, RIGHT, palm facing out
    idx_side = symbol_from_fsw("S10012")  # rotation=2, RIGHT, side facing
    idx_back = symbol_from_fsw("S10014")  # rotation=4, RIGHT, back of hand facing out
    idx_mirrored = symbol_from_fsw("S1001a")  # rotation=10 (0xa) -> LEFT hand

    renderer = HandMeshRenderer3D(_MockRigProvider())
    symbols = (idx_front, idx_side, idx_back, idx_mirrored)
    for sym in symbols:
        print(f"--- Rendering {sym.symbol_id}, rotation={sym.rotation}, hand_side={sym.hand_side.value} ---")
        renderer.render(sym)

    poses = [sym.get_joint_pose() for sym in symbols]
    assert all(pose == poses[0] for pose in poses)
    print("\nOK: joint pose identical across all rotations/hand_sides, only wrist orientation + rig differ.")

    assert idx_front.hand_side == HandSide.RIGHT
    assert idx_side.hand_side == HandSide.RIGHT
    assert idx_back.hand_side == HandSide.RIGHT
    assert idx_mirrored.hand_side == HandSide.LEFT
    print("OK: hand_side decoded correctly (0-7 -> RIGHT, 8-15 -> LEFT).")

    print()
    print("--- Part 2: full FSW sign string -> AST -> FSWR (two-handed sign) ---")
    # A box marker ("M") + two positioned symbols: Index (RIGHT) and Index
    # Bent (LEFT, rotation=10=0xa) side by side -- real FSW sign syntax.
    fsw_sign = "M500x500S10010480x480S1061a520x520"
    positioned_symbols = fsw_to_fswr(fsw_sign)
    assert len(positioned_symbols) == 2
    for positioned in positioned_symbols:
        print(
            f"  {positioned.symbol.symbol_id} at ({positioned.x}, {positioned.y}), "
            f"hand_side={positioned.symbol.hand_side.value}"
        )
    print("OK: one real FSW sign string -> two positioned FSWRenderableSymbol instances.")


if __name__ == "__main__":
    main()
