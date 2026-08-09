"""Renders comparison grids covering every category fsw_r currently
supports, as a visual sanity-check:

1. index_finger_rotations.png -- "Index" (01-01-001) at a fixed fill across
   four rotations (three RIGHT, one LEFT), so the finger-pointing sweep and
   the RIGHT/LEFT mirroring are both visible.
2. index_finger_fills.png -- the same symbol across all 6 fills, the "Six
   Palm Facings", distinct from rotation's effect.
3. mouth_expressions.png / 4. brow_eye_expressions.png -- Category 4
   (Head & Face) blend-shape expressions (mouth/tongue, brows, eye-openness).
5. movement_trajectories.png -- Category 2 (Movement): one symbol per
   PathType (contact/finger/straight/curved/circle), each drawn as its 3D
   trajectory (start green, end red).

Run with: python -m fsw_r_viz.demo
"""

from __future__ import annotations

from pathlib import Path

from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.core.face_movement import FaceMovementSymbol
from fsw_r.core.head_movement import HeadMovementSymbol
from fsw_r.core.head_symbol import HeadSymbol
from fsw_r.core.registry import symbol_from_fsw
from fsw_r_viz.animate_face import render_face_movement_filmstrip
from fsw_r_viz.animate_head import render_head_movement_filmstrip
from fsw_r_viz.animate_movement import animate_movement_to_gif, render_movement_filmstrip
from fsw_r_viz.plot_mesh_head import render_mesh_head_to_file
from fsw_r_viz.plot_face import render_faces_grid
from fsw_r_viz.plot_glyph import render_glyphs_grid
from fsw_r_viz.plot_hand import render_symbols_grid
from fsw_r_viz.plot_head import render_heads_grid
from fsw_r_viz.plot_movement import render_movements_grid


def _render_rotation_sweep(output_dir: Path) -> None:
    symbols = [
        # base_hex, fill, rotation
        (HandSymbol(0x107, fill=0, rotation=0), "01-01-012 rotation=3 (RIGHT, finger up)"),  # Index Hinge
        (HandSymbol(0x107, fill=0, rotation=5), "01-08-002 rotation=2 (RIGHT, finger sideways)"),  # Index Ring Baby on Circle
        (HandSymbol(0x101, fill=0, rotation=2), "01-01-002 rotation=2 (RIGHT, finger down)"),  # Index on Circle
        (HandSymbol(0x1CD, fill=0, rotation=12), "01-09-001 rotation=12 (LEFT, mirrored)"),  # Middle Ring Baby
    ]
    output_path = output_dir / "index_finger_rotations.png"
    render_symbols_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_fill_sweep(output_dir: Path) -> None:
    fill_titles = [
        (0, "Palm, Wall"),
        (1, "Side, Wall"),
        (2, "Back, Wall"),
        (3, "Palm, Floor"),
        (4, "Side, Floor"),
        (5, "Back, Floor"),
    ]
    symbols = [
        (HandSymbol(0x100, fill=fill, rotation=0), f"01-01-001 fill={fill} ({label})")  # Index
        for fill, label in fill_titles
    ]
    output_path = output_dir / "index_finger_fills.png"
    render_symbols_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_mouth_expressions(output_dir: Path) -> None:
    # Category 4 Group 25 (Mouth/Lips): a few distinct authored expressions,
    # rendered as schematic faces so the blend-shapes are visible.
    symbols = [
        (FaceSymbol(0x33B, fill=0, rotation=0), "04-25-001 Mouth Closed Neutral"),
        (FaceSymbol(0x33E, fill=0, rotation=0), "04-25-004 Mouth Smile"),
        (FaceSymbol(0x341, fill=0, rotation=0), "04-25-007 Mouth Frown"),
        (FaceSymbol(0x344, fill=0, rotation=0), "04-25-010 Mouth Open Circle"),
        (FaceSymbol(0x34D, fill=0, rotation=0), "04-25-019 Mouth Kiss"),
        (FaceSymbol(0x359, fill=0, rotation=0), "04-26-001 Tongue Sticks Out Far"),
    ]
    output_path = output_dir / "mouth_expressions.png"
    render_faces_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_brow_eye_expressions(output_dir: Path) -> None:
    # Category 4 Group 23 (Brow/Eyes): brows and eye-openness.
    symbols = [
        (FaceSymbol(0x30A, fill=0, rotation=0), "04-23-001 Eyebrows Straight Up"),
        (FaceSymbol(0x30C, fill=0, rotation=0), "04-23-003 Eyebrows Straight Down"),
        (FaceSymbol(0x316, fill=0, rotation=0), "04-23-013 Eyes Closed"),
        (FaceSymbol(0x31A, fill=0, rotation=0), "04-23-017 Eyes Wide Open"),
        (FaceSymbol(0x31D, fill=0, rotation=0), "04-23-020 Eye Wink"),
    ]
    output_path = output_dir / "brow_eye_expressions.png"
    render_faces_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_eyegaze(output_dir: Path) -> None:
    # Category 4 eyegaze (0x321): rotation is gaze direction (glyph-verified)
    # -- rot 0 up, 2 viewer-left, 4 down, 6 viewer-right. Watch the pupils.
    symbols = [
        (FaceSymbol(0x321, fill=0, rotation=0), "Eyegaze rot=0 (up)"),
        (FaceSymbol(0x321, fill=0, rotation=2), "Eyegaze rot=2 (viewer-left)"),
        (FaceSymbol(0x321, fill=0, rotation=4), "Eyegaze rot=4 (down)"),
        (FaceSymbol(0x321, fill=0, rotation=6), "Eyegaze rot=6 (viewer-right)"),
    ]
    output_path = output_dir / "eyegaze_directions.png"
    render_faces_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_movement_trajectories(output_dir: Path) -> None:
    # Category 2 (Movement): one symbol per PathType, so the 5 movement
    # primitives (contact/finger/straight/curved/circle) are visibly distinct.
    symbols = [
        (MovementSymbol(0x205, fill=0, rotation=0), "02-11-001 Contact"),
        (MovementSymbol(0x216, fill=0, rotation=0), "02-12-001 Finger Movement"),
        (MovementSymbol(0x22A, fill=0, rotation=0), "02-13-001 Straight"),
        (MovementSymbol(0x288, fill=0, rotation=0), "02-16-001 Curved"),
        (MovementSymbol(0x2E3, fill=0, rotation=0), "02-20-001 Circle"),
    ]
    output_path = output_dir / "movement_trajectories.png"
    render_movements_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_movement_animation(output_dir: Path) -> None:
    # Play a Movement symbol back over time: a marker travelling the path.
    # A filmstrip (viewable as one image) + a real animated GIF, for Circle.
    circle = MovementSymbol(0x2E3, fill=0, rotation=0)  # 02-20-001 Circle
    filmstrip = output_dir / "movement_circle_filmstrip.png"
    render_movement_filmstrip(circle, str(filmstrip))
    print(f"Saved: {filmstrip}")
    gif = output_dir / "movement_circle.gif"
    animate_movement_to_gif(circle, str(gif))
    print(f"Saved: {gif}")


def _render_face_movements(output_dir: Path) -> None:
    # Category 4 facial movements over time (filmstrip: t = 0..1).
    for base, name in [(0x317, "blink"), (0x368, "jaw"), (0x35A, "tongue_lick")]:
        symbol = FaceMovementSymbol(base, fill=0, rotation=0)
        output_path = output_dir / f"face_movement_{name}.png"
        render_face_movement_filmstrip(symbol, str(output_path))
        print(f"Saved: {output_path}")


def _render_head_movements(output_dir: Path) -> None:
    # Category 4 head movements over time (filmstrip): a nod and a circle.
    for base, name in [(0x301, "nod"), (0x306, "circle")]:
        symbol = HeadMovementSymbol(base, fill=0, rotation=0)
        output_path = output_dir / f"head_movement_{name}.png"
        render_head_movement_filmstrip(symbol, str(output_path))
        print(f"Saved: {output_path}")


def _render_mesh_heads(output_dir: Path) -> None:
    # Procedural 3D head (Level 3 stand-in): expressions rendered on a real
    # head, and the feature-reference annotation symbols made recognisable.
    smile = FaceSymbol(0x33E, fill=0, rotation=0).get_expression().blendshapes
    items = [
        (smile, "Mouth Smile", None),
        ({"jawOpen": 0.6}, "Jaw open (teeth)", "teeth"),
        ({}, "04-26-009 Teeth", "teeth"),
        ({}, "04-24-007 Ears", "ears"),
        ({}, "04-26-019 Hair", "hair"),
        ({}, "04-26-018 Neck", "neck"),
    ]
    output_path = output_dir / "mesh_heads.png"
    render_mesh_head_to_file(items, str(output_path))
    print(f"Saved: {output_path}")


def _render_annotation_glyphs(output_dir: Path) -> None:
    # The universal fallback: symbols we don't model in 3D (teeth/ears/hair/
    # neck/airflow/head) still render faithfully as their real ISWA glyph.
    symbols = [
        (symbol_from_fsw("S2ff00"), "04-22-001 Head"),
        (symbol_from_fsw("S36100"), "04-26-009 Teeth"),
        (symbol_from_fsw("S33000"), "04-24-007 Ears"),
        (symbol_from_fsw("S36b00"), "04-26-019 Hair"),
        (symbol_from_fsw("S36a00"), "04-26-018 Neck"),
        (symbol_from_fsw("S33500"), "04-24-012 Air Blowing Out"),
    ]
    output_path = output_dir / "annotation_glyphs.png"
    render_glyphs_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def _render_head_orientations(output_dir: Path) -> None:
    # Category 4 head "Nose Up or Down" (0x308): rotation points the nose,
    # mapped to pitch/yaw per Lessons in SignWriting Lesson 10.
    symbols = [
        (HeadSymbol(0x308, fill=0, rotation=0), "Nose up (look up)"),
        (HeadSymbol(0x308, fill=0, rotation=4), "Nose down (look down)"),
        (HeadSymbol(0x308, fill=0, rotation=2), "Nose viewer-left (turn)"),
        (HeadSymbol(0x309, fill=0, rotation=2), "Tilting (roll)"),
    ]
    output_path = output_dir / "head_orientations.png"
    render_heads_grid(symbols, str(output_path))
    print(f"Saved: {output_path}")


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    _render_rotation_sweep(output_dir)
    _render_fill_sweep(output_dir)
    _render_mouth_expressions(output_dir)
    _render_brow_eye_expressions(output_dir)
    _render_eyegaze(output_dir)
    _render_movement_trajectories(output_dir)
    _render_movement_animation(output_dir)
    _render_head_orientations(output_dir)
    _render_face_movements(output_dir)
    _render_head_movements(output_dir)
    _render_mesh_heads(output_dir)
    _render_annotation_glyphs(output_dir)


if __name__ == "__main__":
    main()
