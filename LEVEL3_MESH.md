# Level 3 — full face mesh for the feature-reference symbols

## Goal

The ~15 Category-4 symbols that reference anatomical **features** (teeth,
ears, hair, neck) are not deformations of a neutral face -- ARKit-52
blend-shapes can't express them. To make them recognisable (and to give the
77 modelled face symbols a fuller render than the 2D schematic), they need a
real **3D head mesh**.

## What's built now (no face asset)

`fsw-r-viz/plot_mesh_head.py`: a **procedural** 3D head rendered **offscreen
with pyvista/VTK** (proper depth-sorting, so the head is solid and the
features occlude correctly), driven by ARKit-52 blend-shapes, carrying head
+ ears + hair (a cap that doesn't cover the face) + neck + teeth in an open
mouth. So:
- every `FaceSymbol` / `FaceMovementSymbol` renders on a solid head (smile
  curves the lips, jaw opens showing teeth, eyes blink, brows/gaze move), and
- the feature-reference annotation symbols (teeth/ears/hair/neck) are shown
  and highlighted.

It's still a hand-built approximation, not a research face model -- but it is
now on a real 3D renderer, not a flat schematic.

## Production path (the pipeline is already ready)

The whole framework already emits **ARKit-52** (all 66 `FaceSymbol` +
`FaceMovementSymbol`, and eyegaze/gaze-paths). ARKit-52 is exactly the
control space these meshes use, so driving a real mesh is a rendering job,
not a data job:

| Mesh | Licence | Fit |
|---|---|---|
| **MediaPipe canonical face mesh** (468 verts) | Apache-2.0 (free) | **ARKit-52-native** (MediaPipe FaceLandmarker outputs exactly these blendshapes); recommended first step |
| **FLAME** | non-commercial research | full head; hair/teeth are separate add-on assets |
| **SMPL-X** | non-commercial research | full body+head; overkill for face-only |

This project is for **scientific research (non-commercial)**, so the FLAME /
SMPL-X research licences are acceptable.

### Proposed architecture (future work)

- `MeshFaceRenderer(mesh, arkit_to_mesh)`: load a neutral mesh + its
  ARKit-52 → vertex-offset mapping (MediaPipe ships this; FLAME needs a
  blendshape->expression-basis fit), take a `FaceExpressionPose`, deform,
  render (trimesh + pyrender / pytorch3d -- none installed here).
- `HeadMeshRenderer`: apply `HeadSymbol.get_head_orientation()` /
  `HeadMovementSymbol.orientation_at(t)` as a rigid transform of the head
  mesh -- trivial once a mesh exists.
- Teeth/ears/hair: MediaPipe's mesh has a mouth interior (teeth region);
  hair and detailed teeth need extra assets on top of FLAME.

## Ceiling -- be honest

Even with a full mesh, the remaining airflow / breath / contact / annotation
marks (~14 symbols) are **inherently non-geometric** -- there is nothing to
deform. The 2D ISWA glyph (already rendered, `plot_glyph.py`) is their
correct and permanent form. So the realistic 3D ceiling is **~96/110**,
never 110; the rest are, and should stay, glyphs.

## Current state

77/110 modelled (55 static face + 11 face movements + 5 head orientations +
6 head movements) + 33 faithful glyphs. The procedural mesh head covers the
teeth/ears/hair/neck recognisability now; a MediaPipe/FLAME renderer is the
next, asset-dependent step.
