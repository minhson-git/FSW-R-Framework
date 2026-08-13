# fsw-r

Turns a real FSW (SignWriting/ISWA) sign string into an animated 3D pose
sequence, exportable as a real `.pose` file (the [`pose-format`](https://github.com/sign-language-processing/pose)
library's standard format). No matplotlib, no video encoding, no
visualization dependency of any kind lives in this package — see the
sibling `../fsw-r-viz` for that layer.

See `../ROADMAP.md` (phase-by-phase plan, what's left) and `../PROGRESS.md`
(full decision log, including mistakes found and fixed) for complete
context. This README is a map of the current architecture, not a history.

## Four layers, one-directional

```
core/        FSW string -> AST -> FSWR symbol objects (pose/quaternion/
             trajectory per ISWA category) -- category-agnostic dispatch
    |
timeline/    FSWR symbols -> SignTimeline (a real time axis) -> sampled
             PoseFrame sequence (MVP-1 scope, see below)
    |
export/      PoseFrame sequence -> forward kinematics (hand) + two-bone
             IK (arm) + static torso/head -> a real pose-format Pose
    |
validation/  Pose vs. ground truth -> MPJPE / anatomical-limit reports
             (used by scripts/eval_*.py, not wired into the render path)
```

Each layer only depends on the one above it; `core/` has zero knowledge of
`timeline/`, `timeline/` has zero knowledge of `export/`, etc. Adding a
capability to one layer never requires touching the others' internals —
see each section below for what's currently pluggable.

## `core/`: FSW string -> FSWR symbol objects

```
FSW sign string --[fsw_ast.py, real signwriting.formats.fsw_to_sign()]--> AST
AST             --[fswr_converter.py + registry.py]--------------------> FSWR objects
```

1. **`fsw_ast.py`** parses a *full* FSW sign string (box marker + one or
   more positioned symbols, e.g. `"M508x515S10000493x485S22a04500x500"`) by
   calling the real reference parser,
   [`signwriting.formats.fsw_to_sign.fsw_to_sign`](https://pypi.org/project/signwriting/) —
   an actual import and call, not a re-implementation.
2. **`fsw_symbol_key.py`** decodes one symbol key (e.g. `"S10000"`) into
   `base_hex`/`fill`/`rotation`. `category`/`group`/`base_symbol_number` are
   derived properties (`iswa_data.py`), never stored or reconstructed by
   hand — `base_hex` is the one key that flows through the whole pipeline
   unchanged (see `PROGRESS.md`'s "base_hex làm khoá duy nhất" entry for why
   that mattered).
3. **`registry.py`** + **`fswr_converter.py`**: `registry.build_symbol()`
   dispatches by `category_of(base_hex)` through `_CATEGORY_SYMBOL`
   (currently `{1: HandSymbol, 2: MovementSymbol, 3: DynamicsSymbol,
   4: <Category-4 dispatch, a sibling team's registration>, 5: BodySymbol}`
   — Category 6 and 7 aren't registered yet) and constructs the concrete
   `FSWRenderableSymbol`; `fswr_converter.ast_to_fswr()` runs that over every
   AST node, pairing each result with its page position
   (`PositionedSymbol`). `fswr_converter.fsw_to_fswr(fsw)` chains all three
   stages.

### Per-category symbol classes and their pose contracts

`FSWRenderableSymbol` is a marker only ("this renders to *something*");
each category's own abstract subclass in `renderable_symbol.py` declares
the ONE contract that actually makes sense for it, so a renderer built for
hands never has to branch on category or guess whether a method exists:

| Category | Symbol class | Contract (`FSW*Renderable`) | Pose type |
|---|---|---|---|
| 1. Hands (261/261) | `hand_symbol.HandSymbol` | `FSWHandRenderable` | `HandJointPose` (flexion/abduction per joint) |
| 2. Movement (242/242) | `movement_symbol.MovementSymbol` | `FSWMotionRenderable` | `MotionPath` (trajectory) + `FingerArticulation \| None` (Group 12 only) |
| 3. Dynamics (8/8) | `dynamics_symbol.DynamicsSymbol` (abstract base: `modifier_symbol.FSWModifierSymbol`) | *(none — sibling hierarchy, see below)* | `DynamicsModifier` |
| 4. Head & Face (~110) | `face_symbol.FaceSymbol` / `head_symbol.HeadSymbol` / others (dispatch table, see `registry.py`) | `FSWFaceRenderable` / `FSWHeadRenderable` | `FaceExpressionPose` (ARKit-52 blend-shapes) |
| 5. Trunk & Limb (18/18) | `body_symbol.BodySymbol` | `FSWBodyRenderable` | `BodyPose` (schematic body-diagram descriptor) |
| 6. Location (0/8) | — | — | not started |
| 7. Punctuation (0/5) | — | — | not started |

Category 3 (Dynamics) is deliberately **not** part of the
`FSWRenderableSymbol` tree — a Dynamics symbol modifies the timing/manner
of *other* symbols in the same sign, it renders nothing of its own
(`modifier_symbol.py`'s own docstring explains why).

**What's still this project's own model, not derived from any published
spec:** ISWA/FSW is a 2D notation — there is no authoritative source for a
3D wrist quaternion, per-joint flexion angle, or Category-2/3/5 numeric
value. `get_wrist_orientation()` and every `data/*.json` table's
non-Category-1 values are principled interpretations (documented inline
and in each file's `_meta`), not placeholders waiting for a "real" version
— for those categories, there is no other real version to integrate.

### `rotation`/`fill` encode hand_side and orientation — verified per category, not assumed

For **Category 1**, ISWA `rotation` (a hex digit 0-f) splits into two
halves of 8: `0`-`7` = RIGHT hand, `8`-`f` = LEFT hand (mirror), each half
giving the same `(rotation % 8) * 45°` compass angle. `fill` (0-5) is
orthogonal — the "Six Palm Facings" (which side of the hand shows × which
plane the arm reaches in), confirmed against the real ISWA chart at
[signwriting.org's Index lesson](https://www.signwriting.org/lessons/iswa/group01/01-01-001-01.html).

This does **not** generalize by assumption: measured against a real corpus
([sign-language-processing/signbank-plus](https://github.com/sign-language-processing/signbank-plus),
257,800 signs), Category 2's `rotation` does **not** predict `hand_side`
the way Category 1's does — `MovementSymbol.hand_side` returns `None`
rather than guess wrong ~28% of the time (see that class's own docstring
for the actual numbers). Each category's symbol class states its own rule.

## `timeline/`: `SignTimeline` (MVP-1 scope)

```
tuple[PositionedSymbol, ...] --[build.py]--> SignTimeline --[sample.py]--> tuple[PoseFrame, ...]
```

**MVP-1 scope, a deliberate cut, not a shortcut:** exactly 1 Category-1
(hand posture) symbol + at most 1 Category-2 (movement) symbol, no other
category. Measured on SignBank+: **6.2%** of real signs. Group 12 (Finger
Movement, 20 of Category 2's 242 base symbols) additionally covers
**16.8%** of real signs and, since the "Chuyển động khớp ngón tay" task,
oscillates the actual finger joints (not just the wrist) — see
`core/finger_articulation.py`.

- `build.py`'s `build_timeline()` raises `UnsupportedSignError` naming
  exactly why for anything outside MVP-1's scope — never a best-effort
  wrong timeline.
- `sample.py`'s `sample()` interpolates every track at a fixed FPS: SLERP
  for wrist quaternions, linear for joint angles and position. It never
  re-derives trajectory shape — that's already baked into how many
  keyframes `build.py` generated (dense enough that linear interpolation
  between them closely follows curves/circles/finger-joint oscillation
  without flattening them).
- `anchor.py` maps FSW signbox coordinates into the same body-space
  `export/` and `core/movement_paths.py` already use.

## `export/`: `.pose` output

```
tuple[PoseFrame, ...] --[pose_export.py]--> pose_format.Pose (POSE_LANDMARKS + hand landmarks)
```

- **`forward_kinematics.py`**: `HandJointPose` (angles) → 21 real
  MediaPipe-convention hand landmarks, via `bone_lengths.py`'s cited bone
  lengths (own stature-anchored scale via `anthropometry.py`, unified with
  the body's own scale — see `PROGRESS.md`'s "hand<->body scale" entry).
- **`arm_ik.py`**: closed-form two-bone IK (law of cosines + one
  orthonormal-vector combination — deliberately NOT an iterative
  solver/`scipy.optimize`, so a hyperextended elbow is structurally
  impossible) solves the elbow position from shoulder + wrist. Pole-vector
  constants are measured against real anatomical invariants (elbow never
  rises above both shoulder and wrist), not guessed — see `PROGRESS.md`'s
  "Sửa lại bất biến IK sai" entry for a real regression found and fixed
  here.
- **`body_geometry.py`**: static torso/head/eye landmarks, proportions
  cited from Drillis & Contini (1966) via Winter's *Biomechanics and Motor
  Control of Human Movement* — a few (torso length, eye placement) are
  flagged ESTIMATED where no citation was found, never silently treated as
  equally sourced.
- **`pose_export.py`**: assembles all of the above into a real
  `pose_format.Pose` per frame — `POSE_LANDMARKS` cropped at the hip
  (real sign-video framing is upper-body only; the hip made
  `PoseVisualizer` draw a dominant, unreadable filled trapezoid, see
  `PROGRESS.md`'s "khung hình demo dễ đọc hơn" entry) plus 6 eye points,
  both shoulders, and the active hand's arm. `BODY_UNITS_TO_PIXELS` /
  `VERTICAL_CENTER_OFFSET` are MEASURED (not guessed) against the standard
  demo sign's real bounding box — recalibrated 6 times across this
  project's history as the figure's own geometry changed; the module's own
  docstring keeps the full numbered history, never silently overwritten.

## `validation/`: accuracy against ground truth

Not wired into the render path — used by `scripts/eval_fk_accuracy.py` /
`scripts/eval_anatomical.py`, which write `reports/fk_accuracy.md` /
`reports/anatomical.md`.

- **`normalization.py`**: `PoseNormalizer` (Procrustes-style
  scale/translation normalization, size=150) so MPJPE compares SHAPE, not
  absolute scale.
- **`anatomical_limits.py`**: `JOINT_LIMITS` (per-joint flexion/abduction
  ranges, cited per joint from AAOS/clinical ROM references — flagged
  where estimated, see the module's own docstring) + `validate_pose()`.
  Also imported directly (not `validate_pose()`) by
  `core/finger_articulation.py` to CLAMP Group 12's oscillation at the
  source, not just report violations after the fact.

**Current numbers** (see `reports/`, regenerate with
`python scripts/eval_fk_accuracy.py` / `eval_anatomical.py`):

- **MPJPE = 48.72** (normalized scale 150), beating both baselines
  (average-pose 64.84, one-pose-per-group 60.44). Measured against
  [`sign-language-processing/3d-hands-benchmark`](https://github.com/sign-language-processing/3d-hands-benchmark) —
  the SAME source `hand_joint_poses.json` itself came from, not an
  independent ground truth.
- **224/261 (85.8%)** Category 1 symbols violate at least one
  `JOINT_LIMITS` bound — mostly thumb CMC (201/261), suspected definition
  mismatch between the benchmark's own CMC convention and the clinical
  citation, not yet verified (see `PROGRESS.md`'s Pha 6 entry — the
  recommended next investigation, not yet done).

## Layout

```
src/fsw_r/
  core/
    iswa_data.py              # category/group boundaries (all 7) + per-symbol valid (fill, rotation)
    fsw_base_symbol.py        # base_hex/fill/rotation + derived category/group/symbol_id + hand_side (abstract)
    fsw_ast.py / fsw_symbol_key.py / registry.py / fswr_converter.py   # FSW string -> FSWR pipeline (see above)
    renderable_symbol.py      # FSWRenderableSymbol + per-category FSW*Renderable contracts
    renderer.py                # HandMeshRenderer3D/HandSkeleton/HandRigProvider (Protocol) -- Category 1's
                                #   own renderer-agnostic contract, predates export/; only fsw_r.demo's own
                                #   mock rig exercises it today -- fsw-r-viz's plot_hand.py renders
                                #   independently (its own hand_geometry.py), not through this Protocol
    types.py                  # JointAngle/FingerPose/HandJointPose, MotionPath, FingerArticulation, HandSide
    pose_table.py             # generic PoseTable[PoseT] (base_hex-keyed) + every category's table instance
    hand_symbol.py / movement_symbol.py / body_symbol.py / face_symbol.py / head_symbol.py
    dynamics_symbol.py / modifier_symbol.py   # DynamicsSymbol + its abstract FSWModifierSymbol base (Category 3, no render contract)
    movement_paths.py         # MotionPath -> 3D trajectory samples (path_type x plane formula)
    finger_articulation.py    # FingerArticulation -> per-frame joint-angle oscillation (Group 12), clamped
    body_types.py / dynamics_types.py / face_types.py   # per-category pose dataclasses
  timeline/
    types.py                  # Keyframe/Track/SignTimeline/PoseFrame/TrackPose
    build.py                  # PositionedSymbol tuple -> SignTimeline (MVP-1 scope, see above)
    sample.py                 # SignTimeline -> fixed-FPS PoseFrame sequence (SLERP/lerp)
    anchor.py / classify.py / errors.py
  export/
    forward_kinematics.py     # HandJointPose -> 21 MediaPipe-convention landmarks
    bone_lengths.py           # cited hand bone lengths, stature-anchored
    arm_ik.py                 # closed-form two-bone IK for the arm
    body_geometry.py          # static torso/head/eye landmarks
    anthropometry.py          # shared stature constant (breaks a core<->export import cycle)
    pose_export.py            # PoseFrame sequence -> real pose_format.Pose
  validation/
    normalization.py          # PoseNormalizer (Procrustes-style)
    anatomical_limits.py      # JOINT_LIMITS + validate_pose()
  data/                       # every *.json is base_hex-keyed; _meta always states AUTHORED vs. measured
    hand_joint_poses.json       # Category 1, MEASURED (MediaPipe on 3d-hands-benchmark photos)
    movement_paths.json         # Category 2, generated by formula
    finger_articulations.json   # Group 12, AUTHORED (5/20 bases from real ISWA names, 15 defaulted)
    dynamics_modifiers.json     # Category 3, AUTHORED
    body_poses.json             # Category 5, AUTHORED
    face_expression_poses.json  # Category 4 (sibling team)
    iswa_valid_combinations.json  # real ISWA font cmap, all 652 base symbols
  demo.py                      # python -m fsw_r.demo
scripts/
  gen_*.py                    # regenerate data/*.json from source tables (run after editing a table)
  fetch_ground_truth.py / eval_fk_accuracy.py / eval_anatomical.py   # regenerate reports/*.md
tests/                        # 38 files, 1,475 tests
reports/
  fk_accuracy.md / anatomical.md   # regenerated, not hand-edited
```

## Setup

```bash
pip install -e ".[dev]"
```

## Run

```bash
python -m fsw_r.demo
pytest              # 1,475 tests
mypy --strict         # clean, 91 files -- src/+tests/ plus the scripts/*.py listed in pyproject.toml
                         # (scripts/export_joint_poses.py is deliberately excluded there: a frozen
                         # one-time migration record whose imports no longer resolve, see that file)
python scripts/eval_fk_accuracy.py   # regenerates reports/fk_accuracy.{json,md}
python scripts/eval_anatomical.py    # regenerates reports/anatomical.{json,md}
```

## Visualization

There is no matplotlib/video-encoding code in this package on purpose. All
rendering (static sanity-check plots AND real `.pose` → video/GIF) lives in
the sibling package `../fsw-r-viz`, which depends on `fsw-r` — never the
reverse. This package stays free of any visualization dependency.

## Adding a new category (Location/Punctuation, or extending an existing one)

Category 1 went through both the wrong pattern (261 separate classes) and
the right one (data-driven, one class + a JSON table) — do the data-driven
version from the start, following whichever existing category is closest
(Category 5's `BodySymbol`/`body_poses.json` is the simplest complete
example):

1. Design that category's own pose type in `core/types.py` (or its own
   `*_types.py` module if it needs several related dataclasses, like
   `body_types.py`/`dynamics_types.py`/`face_types.py`).
2. Add a `FSW*Renderable(FSWRenderableSymbol)` contract in
   `renderable_symbol.py` if the category renders to something (skip this
   if it's a modifier like Category 3).
3. Write `scripts/gen_<category>_poses.py` (formula-driven, like
   `gen_movement_paths.py`) or hand-author `data/<category>_poses.json`
   directly (AUTHORED, like `dynamics_modifiers.json`) — keyed by
   `base_hex` (hex string, e.g. `"22b"`), with a `symbol_id`/`name` field
   for readability, and an honest `_meta` block (`names_source`,
   `values_source`, `unverified_assumptions`).
4. In `core/pose_table.py`, add a `_parse_<category>()` function +
   `<CATEGORY>_TABLE = PoseTable[YourPoseT](...)` instance —
   `PoseTable`'s own class body never changes.
5. Write `Your CategorySymbol(FSW*Renderable)`: looks itself up in the new
   table by `self.base_hex`; `get_wrist_orientation()`/`hand_side` — don't
   assume Category 1's formulas generalize, verify against that category's
   own real ISWA names/chart first (Category 2's `hand_side` measurably
   does NOT follow Category 1's rule — see above).
6. In `core/registry.py`, add one entry to `_CATEGORY_SYMBOL`. That is the
   only change to an existing `core/` file — `fsw_symbol_key.py`,
   `fsw_base_symbol.py`, `iswa_data.py`, and `pose_table.py`'s `PoseTable`
   class are already category-agnostic.
7. If the category needs to affect `SignTimeline` (Category 3/5 currently
   don't — their symbol layer is done but not wired in, see
   `../ROADMAP.md`), that's a separate `timeline/build.py` change, not part
   of the symbol-layer work above.

## Notes / open items

See `../ROADMAP.md` for the full, current list (kept there instead of
duplicated here so it can't drift out of sync) — highlights:

- **Category 3/5 are done at the symbol layer but not wired into
  `SignTimeline`** — `DEFAULT_SIGN_DURATION` is still a placeholder
  constant, and torso pose is still static (`body_geometry.py`'s own
  constants), not driven by a real Category 5 `BodyPose`.
- **MVP-2** (signs with >1 hand/movement symbol, ~20.9% of real signs, plus
  handshape interpolation between two same-side Category 1 symbols in one
  sign, ~12.8%) needs track-assignment logic MVP-1 deliberately doesn't
  have yet.
- **Thumb CMC investigation** (highest-priority recommendation from the
  validation numbers above) — not started.
- Categories 6 (Location, 8 base symbols) and 7 (Punctuation, 5) haven't
  been started at all.
- Written and tested against Python 3.10 (the environment available
  locally); nothing here uses a 3.10-only feature.
