# fsw-r-viz

Everything that turns `fsw-r`'s pose/quaternion/trajectory data into
something visible — from quick matplotlib sanity-check plots up to real
`.pose` → video/GIF output. This is a **separate package** from `fsw-r`:
`fsw-r` (the core symbol/timeline/export library) has no dependency on this
package or on matplotlib/pose-format's visualizer — it only exposes the
public types this package consumes. This package depends on `fsw-r`, never
the other way around.

See `../PROGRESS.md`/`../ROADMAP.md` for full context; this README maps
what's here and why each renderer exists.

## Two kinds of renderer here

**Debugging aids** (matplotlib, static images or simple animated GIFs) —
one per ISWA category with a 3D pose, so a `fsw_r` symbol's numbers can be
checked by eye without a real rig/mesh:

| Module | Renders | Category |
|---|---|---|
| `hand_geometry.py` + `plot_hand.py` | stick-figure hand (forward kinematics from `HandJointPose`) | 1 (Hands) |
| `plot_movement.py` / `animate_movement.py` | 3D trajectory (static / marker-along-path animated) | 2 (Movement) |
| `face_geometry.py` + `plot_face.py` / `animate_face.py` | schematic 2D face (static / facial-movement animated) | 4 (Head & Face) |
| `plot_head.py` / `animate_head.py` | simple 3D head orientation (static / head-movement animated) | 4 (Head & Face) |
| `plot_mesh_head.py` | real offscreen 3D head via pyvista/VTK, ARKit-52 driven (ears/hair/neck/teeth) | 4 (Head & Face) |
| `plot_glyph.py` | the real 2D ISWA glyph itself, via the reference `signwriting` font renderer | any (universal fallback) |
| `render_timeline.py` | numbered PNG sequence sampling a `SignTimeline` | MVP-1 (Category 1+2 combined) |

None of these reimplement pose math — each one takes an already-built
`fsw_r` object (`HandJointPose`, `MotionPath`, `FaceExpressionPose`, a
`SignTimeline`, ...) and only adds the matplotlib/pyvista drawing calls.
They stay debugging aids on purpose, not the final renderer.

**Real video, through the standard format** (`pose-format`'s
`PoseVisualizer`, not matplotlib) — this is the actual deliverable, not a
sanity check:

| Module | Produces |
|---|---|
| `render_pose_video.py` | full-body video/GIF (posture + trajectory) from `fsw_r.export.pose_export.frames_to_pose` |
| `render_hand_closeup.py` | zoomed-in, single-hand video/GIF (handshape + finger joints), same `.pose` data, re-projected for readability — see below |

## Why two videos, not one

At the full-body video's native frame scale, a hand's own MCP joints sit a
few pixels apart — well under `PoseVisualizer`'s own line thickness at that
frame size, so fingers blend into one blob. The full-body video is never
"fixed" for this — it does its own job (showing posture/trajectory)
correctly. `render_hand_closeup.py` adds a second, purely display-layer
video instead: crops to one hand's component, re-centers every frame on
its own wrist (so the hand holds still while its internal joints keep
articulating — the trajectory is already shown by the other video), and
magnifies by a scale derived from `HAND_CLOSEUP_TARGET_FRACTION` and the
hand's OWN measured size (not the wrist's travel distance — anchoring on
hand size alone gives a meaningfully larger, more readable zoom).

**3/4 view (`view_angle_deg` / `HAND_CLOSEUP_VIEW_ANGLE_DEG`):**
`PoseVisualizer` projects orthogonally onto XY only — Z is used solely for
paint order, never position. A joint that flexes mostly in Z (which this
project's own Group 12 finger-articulation data does) is nearly invisible
head-on: the arc a flexing finger sweeps flattens into what looks like
simple shortening, not bending. `hand_closeup_pose()` can rotate the hand
about Y, **before** the wrist-anchor/scale step, turning part of that
invisible Z motion into visible X. `view_angle_deg` defaults to `0.0` on
every public function (the original straight-on view, exactly reproduced —
this was a deliberate, tested choice: defaulting to the 3/4 angle instead
silently broke pre-existing straight-on renders/tests the first time it was
tried) — pass `HAND_CLOSEUP_VIEW_ANGLE_DEG` explicitly for the 3/4 view.
Rotation always happens before the bounding-box measurement that derives
the zoom factor, never after (computing the zoom from the un-rotated
extent would size the hand for a box that doesn't match what's actually
drawn).

Both real-video renderers use the same save/fallback pattern: try
`PoseVisualizer.save_video()` (needs the optional `vidgear` package + a
real ffmpeg binary), and if that's not available, fall back to
`save_gif()` (Pillow only), printing a clear message explaining why —
never silently, never a corrupt/empty file. As of this writing the
development environment has neither `vidgear` nor ffmpeg, so every
committed demo GIF in `demo/` went through that fallback path.

## Setup

`fsw-r` is an unpublished local sibling package, so install it first, then
install this package:

```bash
pip install -e ../fsw-r
pip install -e ".[dev]"
```

## Run

```bash
python -m fsw_r_viz.demo   # renders every debugging-aid image/GIF into output/,
                             # plus the real videos into demo/ (committed, not gitignored)
pytest                      # 42 tests
mypy --strict                 # 4 pre-existing errors, unrelated (FuncAnimation type stubs,
                               # one missing ndarray generic) -- everything else clean
```

## Layout

```
src/fsw_r_viz/
  hand_geometry.py       # bone lengths/positions + forward kinematics + mirror_for_left_hand
  plot_hand.py             # Category 1 stick-figure (static)
  face_geometry.py       # schematic face point layout
  plot_face.py             # Category 4 face (static) / animate_face.py (facial movement over time)
  plot_head.py              # Category 4 head orientation (static) / animate_head.py (head movement over time)
  plot_mesh_head.py           # Category 4 real 3D head (pyvista/VTK, ARKit-52 driven)
  plot_movement.py          # Category 2 trajectory (static) / animate_movement.py (marker along path)
  plot_glyph.py               # real 2D ISWA glyph, any category (reference signwriting font renderer)
  render_timeline.py          # SignTimeline -> numbered PNG sequence
  render_pose_video.py         # .pose -> full-body video/GIF (PoseVisualizer)
  render_hand_closeup.py        # .pose -> zoomed single-hand video/GIF, optional 3/4 view rotation
  demo.py                      # python -m fsw_r_viz.demo -- renders everything above once
tests/                         # 14 files, 42 tests
demo/                          # COMMITTED (not gitignored) real-video evidence -- see below
output/                        # gitignored -- debugging-aid images/GIFs from demo.py
```

## `demo/`: committed video evidence, not scratch output

Unlike `output/` (gitignored, regenerated freely), `demo/` is committed —
it's this project's visual evidence trail, one numbered stage per rendering
task, always on the same standard demo sign
(`M508x515S10000493x485S22a04500x500`, Index handshape + Straight Wall
Plane movement) so stages are directly comparable:

- `mvp1_sign_1_before_scale.gif` → `_4_unified_scale.gif`: hand-only → full
  body → unified hand/body anthropometric scale.
- `_5_readable_frame.gif` → `_7_elbow_invariant_fix.gif`: frame cropped at
  the hip (no more dominant torso trapezoid) + eyes added, then two rounds
  of arm-IK pole-vector fixes (`_6` introduced a regression by satisfying a
  wrong test invariant, `_7` reverted it — see `PROGRESS.md` for the full
  story, kept as an honest record, not silently corrected out of history).
- `_8_hand_closeup.gif` / `mvp1_sign_hand_closeup.gif`: the zoomed single-
  hand video (numbered stage + canonical "latest" file).
- `_9_finger_movement.gif`: a Group 12 (Finger Movement) sign — the first
  demo where the handshape itself changes across frames, not just the
  wrist position.
- `_10_closeup_front.gif` / `_10_closeup_3q.gif`: the same Group 12 sign at
  0° and 60° (the 3/4 view), side by side — the 3/4 view visibly shows an
  arc/bend where the front view only shows shortening.

`mvp1_sign.gif` (full body) and `mvp1_sign_hand_closeup.gif` (close-up,
0°) are the canonical "latest" files `demo.py`'s own `main()` regenerates
every run — always verified byte-identical to their matching numbered
stage before being committed.

## Left/right hand mirroring (debugging-aid renderers only)

`fsw-r`'s `symbol.hand_side` comes from ISWA's `rotation` encoding for
Category 1 (0-7 → `RIGHT`, 8-15 → `LEFT`; see `fsw-r`'s README). A left
hand is a *mirror image* of a right hand, not a rotation of one — but
`hand_geometry.py` (used by `plot_hand.py`/`render_timeline.py`) has no
real distinct rig, only a RIGHT-hand stick figure built from bone lengths
and forward kinematics. So the debugging-aid equivalent of "pick the other
rig" is `mirror_for_left_hand()`: flips the x axis (pinky↔thumb spread
axis) of the RIGHT-hand geometry *before* the wrist orientation is applied,
whenever `symbol.hand_side == HandSide.LEFT`. `fsw_r.export.forward_kinematics`
(the real video pipeline) uses the same mirroring technique independently,
in its own layer (flips local x before applying wrist orientation) — the
two aren't shared code, but neither package models a genuinely distinct
LEFT-hand chirality/mesh; both treat LEFT as a mirrored RIGHT.
