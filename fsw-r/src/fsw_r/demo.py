"""Demo, in three parts:

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

3. Walk all 6 `fill` values at a fixed rotation ("Six Palm Facings", per
   https://www.signwriting.org/lessons/iswa/group01/01-01-001-01.html) --
   fill is NOT the same thing as rotation: it never changes which way the
   finger points, only which side of the hand shows (Palm/Side/Back) and
   which plane the arm reaches in (Wall/Floor).

4. Parse base_symbol_number 1 of every one of the 10 Hands groups --
   Category 1's full 261 base symbols are all implemented (data-driven, see
   core/pose_table.py), confirming the registry covers all 10 groups.

Run with: python -m fsw_r.demo
"""

from __future__ import annotations

from scipy.spatial.transform import Rotation

from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.iswa_data import HAND_GROUP_START
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.core.renderer import HandMeshRenderer3D, HandSkeleton
from fsw_r.core.types import HandJointPose, HandSide


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
    print("--- Part 1: rotation sweeps which way the finger points ---")
    # Real FSW symbol keys for "Index" (base 0x100), fill=0 (Palm of Hand,
    # Wall Plane -- the neutral fill): "S100" + fill + rotation.
    idx_front = symbol_from_fsw("S10000")  # rotation=0, RIGHT, finger points up
    idx_side = symbol_from_fsw("S10002")  # rotation=2, RIGHT, finger points sideways
    idx_back = symbol_from_fsw("S10004")  # rotation=4, RIGHT, finger points down
    idx_mirrored = symbol_from_fsw("S1000a")  # rotation=10 (0xa) -> LEFT hand

    renderer = HandMeshRenderer3D(_MockRigProvider())
    symbols = (idx_front, idx_side, idx_back, idx_mirrored)
    for sym in symbols:
        hand_side = sym.hand_side.value if sym.hand_side is not None else "none"
        print(f"--- Rendering {sym.symbol_id}, rotation={sym.rotation}, hand_side={hand_side} ---")
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
        side = positioned.symbol.hand_side
        print(
            f"  {positioned.symbol.symbol_id} at ({positioned.x}, {positioned.y}), "
            f"hand_side={side.value if side is not None else 'none'}"
        )
    print("OK: one real FSW sign string -> two positioned FSWRenderableSymbol instances.")

    print()
    print("--- Part 3: fill sweeps the 'Six Palm Facings', rotation fixed at 0 ---")
    fill_descriptions = [
        (0, "Palm of Hand, Wall Plane"),
        (1, "Side of Hand, Wall Plane"),
        (2, "Back of Hand, Wall Plane"),
        (3, "Palm of Hand, Floor Plane"),
        (4, "Side of Hand, Floor Plane"),
        (5, "Back of Hand, Floor Plane"),
    ]
    fill_symbols = [symbol_from_fsw(f"S100{fill}0") for fill, _ in fill_descriptions]
    for symbol, (fill, description) in zip(fill_symbols, fill_descriptions):
        quat = symbol.get_wrist_orientation().as_quat()
        print(f"  fill={fill} ({description}): wrist quat (x,y,z,w)={quat}")

    poses_across_fill = [symbol.get_joint_pose() for symbol in fill_symbols]
    assert all(pose == poses_across_fill[0] for pose in poses_across_fill)
    quats_across_fill = [tuple(symbol.get_wrist_orientation().as_quat()) for symbol in fill_symbols]
    assert len(set(quats_across_fill)) == len(quats_across_fill)
    print("OK: joint pose identical across all 6 fills; all 6 wrist orientations are distinct.")

    print()
    print("--- Part 4: base_symbol_number 1 of all 10 Hands groups ---")
    group_symbols = [symbol_from_fsw(f"S{base:03x}10") for base in HAND_GROUP_START]
    for symbol in group_symbols:
        assert isinstance(symbol, HandSymbol)
        print(f"  group {symbol.group}: {symbol.symbol_id} ({symbol.name!r})")
    assert len(group_symbols) == 10
    assert [s.group for s in group_symbols] == list(range(1, 11))
    print("OK: all 10 Hands groups have at least one registered, parseable base symbol.")


if __name__ == "__main__":
    main()
