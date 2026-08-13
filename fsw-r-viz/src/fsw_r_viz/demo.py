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

3. timeline/frame_NNN.png -- a numbered PNG sequence sampling a moving
   MVP-1 SignTimeline (one real Category 1 hand symbol + one real
   Category 2 movement symbol) at 25 fps -- the first visual evidence the
   framework produces MOTION, not just a static pose.
6. ../demo/mvp1_sign.mp4 (or .gif, see render_pose_video.py's fallback) --
   the same MVP-1 sign, this time through the real export layer
   (fsw_r.export -> .pose -> PoseVisualizer), committed to the repo (not
   gitignored like output/) as this project's first real video evidence.
   As of the "scale + thân tĩnh + two-bone IK" task, this is a full
   SIGNER figure (static torso/head + two-bone-IK arm around the hand),
   not just a hand -- see mvp1_sign_1_before_scale.gif / _2_after_scale.gif
   / _3_after_body.gif for the 3-stage progression, then
   _4_unified_scale.gif (the hand<->body scale-unification task: the hand
   now derives from the SAME assumed stature as the body, so it is no
   longer ~1.5x too small relative to the torso), then
   _5_readable_frame.gif (the "khung hình demo dễ đọc hơn" task: cropped
   at the hip so PoseVisualizer's closed shoulder-hip-hip trapezoid no
   longer dominates the frame, plus eyes so the head has real shape), then
   _6_arm_ik_fix.gif (the "sửa bug hướng xoay IK + chỉnh khung hình demo"
   task: shoulders no longer span 81% of the frame width -- kept; but that
   task's own elbow recalibration, meant to fix the elbow swinging ~160px
   below both the shoulder and wrist, itself rested on a WRONG invariant
   and flattened the arm into a near-straight line, see arm_ik.py's module
   docstring), then _7_elbow_invariant_fix.gif (the "sửa lại bất biến IK
   sai" task: reverted that wrong invariant/pole recalibration -- the
   elbow droops below the shoulder-wrist line again, correctly this time,
   forming a natural V, while keeping _6's frame-width fix).
7. ../demo/mvp1_sign_8_hand_closeup.mp4 (or .gif) -- the "video cận cảnh
   bàn tay" task: a SECOND video, not a replacement for #6 above. At
   mvp1_sign.gif's own full-body scale, this sign's hand MCP joints sit
   only ~8.4px apart, under PoseVisualizer's 3px line thickness -- the
   fingers blend into one blob, unreadable as a handshape. This close-up
   (see render_hand_closeup.py) crops to just the hand, re-centers every
   frame on its own wrist, and magnifies ~3.6x by the hand's OWN measured
   size (not the wrist's movement trajectory -- that inflates the zoom
   less and isn't what this video is for), so individual fingers/joints
   are readable. mvp1_sign_7 (#6 above) is UNCHANGED by this task -- it
   still does its own job, showing posture/trajectory.
8. ../demo/mvp1_sign_9_finger_movement.mp4 (or .gif) -- the "Chuyển động
   khớp ngón tay" (Group 12) task: a DIFFERENT sign from #6/#7 above (Index
   handshape + 0x221 "Hinge Movement, Up Down Large", the leading Group 12
   base symbol, 38.2% of real Group 12 token usage), rendered through the
   same hand-close-up pipeline as #7. Before this task, EVERY moving
   sign's joint_pose was byte-identical across all keyframes (a rigid hand
   dragged along a trajectory) -- Group 12 signs now oscillate the
   relevant finger joints over time (see core/finger_articulation.py in
   fsw-r), which #6/#7's own sign (Straight Wall Plane movement, not Group
   12) still does NOT do, by design (D2 -- no regression for non-Group-12
   signs).

Run with: python -m fsw_r_viz.demo
"""

from __future__ import annotations

from pathlib import Path

from fsw_r.core.face_movement import FaceMovementSymbol
from fsw_r.core.face_symbol import FaceSymbol
from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.core.hand_symbol import HandSymbol
from fsw_r.core.head_movement import HeadMovementSymbol
from fsw_r.core.head_symbol import HeadSymbol
from fsw_r.core.movement_symbol import MovementSymbol
from fsw_r.core.registry import symbol_from_fsw
from fsw_r.timeline.build import build_timeline
from fsw_r_viz.animate_face import render_face_movement_filmstrip
from fsw_r_viz.animate_head import render_head_movement_filmstrip
from fsw_r_viz.animate_movement import animate_movement_to_gif, render_movement_filmstrip
from fsw_r_viz.plot_face import render_faces_grid
from fsw_r_viz.plot_glyph import render_glyphs_grid
from fsw_r_viz.plot_hand import render_symbols_grid
from fsw_r_viz.plot_head import render_heads_grid
from fsw_r_viz.plot_mesh_head import render_mesh_head_to_file
from fsw_r_viz.plot_movement import render_movements_grid
from fsw_r_viz.render_hand_closeup import fsw_to_hand_closeup_video
from fsw_r_viz.render_pose_video import fsw_to_video
from fsw_r_viz.render_timeline import render_timeline_to_pngs


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


def _render_timeline_demo(output_dir: Path) -> None:
    # A real, MVP-1-scoped FSW sign: Index (01-01-001, base 0x100) at
    # signbox (480, 480), plus a real Category 2 movement symbol --
    # Straight Wall Plane (02-13-002, base 0x22a) -- fill=0, rotation=0.
    fsw = "M500x500S10010480x480S22a10500x500"
    positioned_symbols = fsw_to_fswr(fsw)
    timeline = build_timeline(positioned_symbols)

    timeline_dir = output_dir / "timeline"
    paths = render_timeline_to_pngs(timeline, str(timeline_dir))
    print(f"Saved {len(paths)} frames to {timeline_dir} (from FSW {fsw!r})")


def _render_pose_video_demo(demo_dir: Path) -> None:
    # First visual evidence of the export layer (fsw_r.export -> .pose ->
    # real video/GIF), not just a numbered PNG sequence: a real MVP-1 sign
    # (Index + Straight Wall Plane movement, same sign core/demo signs use
    # elsewhere in this file) run all the way through
    # SignTimeline -> pose_export.frames_to_pose -> PoseVisualizer. Written
    # to demo/ (NOT output/, which is gitignored) so this artifact gets
    # committed -- see this package's export-layer task brief, Part F.
    fsw = "M508x515S10000493x485S22a04500x500"
    video_path = demo_dir / "mvp1_sign.mp4"
    written = fsw_to_video(fsw, video_path)
    print(f"Saved: {written} (from FSW {fsw!r})")


def _render_hand_closeup_demo(demo_dir: Path) -> None:
    # SECOND video, alongside (not replacing) _render_pose_video_demo's
    # full-body one -- see render_hand_closeup.py's own module docstring
    # for why the full-body video's native scale can't show handshape
    # (MCP joints ~8.4px apart, under PoseVisualizer's 3px line
    # thickness). Same demo sign as the full-body video, so the two are
    # directly comparable frame-for-frame.
    fsw = "M508x515S10000493x485S22a04500x500"
    video_path = demo_dir / "mvp1_sign_hand_closeup.mp4"
    written = fsw_to_hand_closeup_video(fsw, video_path)
    print(f"Saved: {written} (from FSW {fsw!r})")


def _render_finger_movement_demo(demo_dir: Path) -> None:
    # "Chuyển động khớp ngón tay" task -- a Group 12 (Finger Movement)
    # sign, DIFFERENT from _render_pose_video_demo's/_render_hand_closeup_
    # demo's own sign (Straight Wall Plane movement, not Group 12 -- see
    # this file's own module docstring, point 8). Index handshape + 0x221
    # ("Hinge Movement, Up Down Large", the leading Group 12 base symbol,
    # 38.2% of real Group 12 token usage -- see PROGRESS.md's entry for
    # this task). Rendered through the same hand-close-up pipeline as
    # mvp1_sign_hand_closeup, since that's what makes finger articulation
    # actually visible.
    fsw = "M508x515S10000493x485S22100500x500"
    video_path = demo_dir / "mvp1_sign_9_finger_movement.mp4"
    written = fsw_to_hand_closeup_video(fsw, video_path)
    print(f"Saved: {written} (from FSW {fsw!r})")


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    demo_dir = Path(__file__).resolve().parent.parent.parent / "demo"
    demo_dir.mkdir(exist_ok=True)
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
    _render_timeline_demo(output_dir)
    _render_pose_video_demo(demo_dir)
    _render_hand_closeup_demo(demo_dir)
    _render_finger_movement_demo(demo_dir)


if __name__ == "__main__":
    main()
