# fsw-r

Renders ISWA/FSW (SignWriting) hand symbols in 3D by adding a joint-pose layer
on top of real FSW symbol-key parsing.

## FSW -> AST -> FSWR: a real parser, then a converter

Three stages, each its own module:

```
FSW sign string  --[fsw_ast.py, real signwriting.formats.fsw_to_sign()]-->  AST (FSWSignAST)
AST              --[fswr_converter.py + registry.py]---------------------> FSWR objects (PositionedSymbol)
```

1. **`core/fsw_ast.py`** parses a *full* FSW sign string (box marker +
   position + one or more positioned symbols, e.g.
   `"M500x500S10010480x480S1061a520x520"` -- a two-handed sign) by calling
   the real reference parser: `signwriting.formats.fsw_to_sign.fsw_to_sign`,
   from the [`signwriting`](https://pypi.org/project/signwriting/) PyPI
   package (the installable Python port of
   [sutton-signwriting/core](https://github.com/sutton-signwriting/core)).
   This is an actual import and call, not a re-implementation -- the AST
   (`FSWSignAST`) is this project's typed wrapper around that library's
   return value, nothing more.
2. **`core/fsw_symbol_key.py`** decodes one already-extracted symbol key
   (e.g. `"S10010"`, one AST node) into `base_hex`/`fill`/`rotation` --
   `base_hex` flows through unchanged from the key; `category`/`group`/
   `base_symbol_number` are derived properties (`core/iswa_data.py`), never
   stored or reconstructed by hand. The key-slicing technique
   (`base = key[:4]`, etc.) mirrors what the reference library itself does
   internally in `signwriting.utils.mirror.mirror_symbol` -- there's no
   public library function for this specific decomposition, so this module
   does it the same way the reference implementation does. This parser only
   validates the full ISWA range (`0x100`-`0x38b`, all 7 categories) -- it
   does NOT block by category; a real Category 2 (Movement) key parses
   fine here, see `core/registry.py` for where "is this category actually
   supported" is decided instead. The *group*/*category* boundaries are
   ISWA facts sourced from that project's `src/fsw/fsw-structure.js`
   (`group` array, 30 entries; `category` array, 7 entries) -- the Hands
   group boundaries cross-checked against the 14 base symbols listed at
   [signwriting.org's Group 1 page](https://www.signwriting.org/lessons/iswa/group01/),
   whose own links confirm base_symbol_number 1 = "Index" and 7 = "Index Bent".
3. **`core/registry.py`** + **`core/fswr_converter.py`** are the "AST -> FSWR"
   converter: `registry.build_symbol()` dispatches by
   `category_of(base_hex)` through `_CATEGORY_SYMBOL` (currently
   `{1: HandSymbol}` -- adding a category is one more dict entry, see
   "Adding a new category" below) and constructs the concrete
   `FSWRenderableSymbol`; `fswr_converter.ast_to_fswr()` runs that over
   every node in an `FSWSignAST`, pairing each resulting object with its
   page position (`PositionedSymbol`). `fswr_converter.fsw_to_fswr(fsw)`
   chains all three stages for the common case of starting from a raw
   string. `registry.symbol_from_fsw(key)` remains as a convenience for the
   single-symbol case.

**What's still our own model, not derived from any published spec:** ISWA/FSW
is a 2D notation -- there is no authoritative source for a 3D wrist
quaternion or per-joint flexion angles. `get_wrist_orientation()` and the
`_default_joint_pose()` templates are this project's own principled
interpretation (documented inline), not something "mocked until the real
version is dropped in" -- there is no other "real" version of that part to
integrate.

## Architecture

```
FSWBaseSymbol                     base_hex/fill/rotation
                                   category/group/base_symbol_number/symbol_id (derived properties)
                                   + hand_side (abstract -- per-category, see below)
                                   + get_wrist_orientation() (abstract)
    |
FSWRenderableSymbol (abstract)    + get_joint_pose() contract
    |
HandSymbol (Category 1, all 261 base symbols)
                                   get_joint_pose() looks itself up in pose_table.py by base_hex
                                   hand_side: rotation-based (see below)
```

(A future `MovementSymbol` for Category 2 would sit alongside `HandSymbol`
here, with its own `hand_side` rule -- see below for why it can't reuse
Category 1's.)

`HandMeshRenderer3D` depends only on `FSWRenderableSymbol` and `HandRigProvider`
(both abstract) -- it never imports a specific category or symbol class, so
adding new ones never touches the renderer (it does have one defensive
branch: it raises a clear error if `symbol.hand_side` is `None`, since that
means the category doesn't tell you which hand to render).

### `rotation` encodes hand_side, not just an angle -- but only for Category 1

ISWA `rotation` is a hex digit 0-f (16 values). For **Category 1 (Hands)**,
it is split into two halves of 8:

| rotation | direction | angle | hand_side |
|---|---|---|---|
| `0`-`7` | counter-clockwise | `(rotation % 8) * 45°` | `RIGHT` |
| `8`-`f` | clockwise (mirror of the 0-7 half) | `(rotation % 8) * 45°` | `LEFT` |

16 rotation values exist -- not 8 -- precisely because `hand_side` is encoded
in *which half* `rotation` falls into, for Hands; ISWA has no separate
left/right field. `FSWBaseSymbol.hand_side` is **abstract** (returns
`HandSide | None`) -- `HandSymbol.hand_side` implements the table above for
Category 1 specifically. This is deliberately NOT assumed to generalize:
measured against a real sign-language corpus
([sign-language-processing/signbank-plus](https://github.com/sign-language-processing/signbank-plus),
257,800 signs), Category 2 (Movement)'s `rotation` does **not** predict
hand_side the same way -- see `ROADMAP.md`'s Phase 2 section for the actual
numbers. Each category's symbol class states its own rule; none is
inherited by accident.

**Why the renderer doesn't mirror a right hand into a left hand:** a left
hand is not a right hand rotated by some angle -- it's the opposite
chirality (mirror image), which a rotation operator cannot produce. So
`HandMeshRenderer3D` takes a `HandRigProvider` and asks it for the rig
matching `symbol.hand_side` -- two genuinely separate rigs/meshes -- and only
then applies `get_wrist_orientation()` + `get_joint_pose()` to whichever rig
came back.

### `fill` is the "Six Palm Facings" -- not the same thing as `rotation`

Confirmed against the real chart at
[signwriting.org's Index lesson](https://www.signwriting.org/lessons/iswa/group01/01-01-001-01.html)
(`ISWA2010_Symbol_Charts/01-01-001-ISWA_Chart.jpg`): `rotation` sweeps which
way the extended finger points on the page (0=up, 90=side, 180=down, ...).
`fill` (0-5) never changes that -- it changes which side of the hand is
presented, as two combined components:

| fill | facing (fill % 3) | plane (fill // 3) |
|---|---|---|
| 0 | Palm of Hand | Wall Plane (front view, arm reaching forward) |
| 1 | Side of Hand | Wall Plane |
| 2 | Back of Hand | Wall Plane |
| 3 | Palm of Hand | Floor Plane (top view, arm reaching down) |
| 4 | Side of Hand | Floor Plane |
| 5 | Back of Hand | Floor Plane |

`FSWBaseSymbol._fill_facing_degrees()` (0/-90/-180, about the wrist-to-
fingertip axis -- the same axis `rotation` deliberately does *not* use, see
above) and `_fill_plane_degrees()` (0/-90, about the spread axis) implement
this. The sign on facing (negative, not positive) is a concrete correction:
fill=1 (Side of Hand)'s palm normal must point to -x, not +x -- not
derivable from the chart's 2D photo alone (no depth cue says which edge of
the hand faces the camera), confirmed directly instead. Back of Hand
(fill%3=2, a half turn) lands in the same place either sign, so only Side
of Hand is actually affected. `_default_wrist_orientation()` composes all
three components as
`compass * plane * facing` -- **facing must be applied before plane, not
after**: pitching into the Floor Plane first rotates the palm-normal vector
onto the same axis facing rotates around, so a later facing rotation can't
change it at all (Palm and Back would collapse onto the same orientation --
this was a real bug, caught by inspection against the chart, see
`test_fill_palm_faces_up_in_floor_plane` /
`test_fill_back_faces_down_in_floor_plane`). Base symbols with no quirks of
their own just return `_default_wrist_orientation()` from
`get_wrist_orientation()`.

## Layout

```
src/fsw_r/
  core/
    iswa_data.py             # ISWA structure (category/group boundaries, all 7 categories)
                              #   + per-symbol valid (fill, rotation) combinations
    fsw_base_symbol.py       # base_hex/fill/rotation + category/group/base_symbol_number/symbol_id (derived)
                              #   + hand_side (abstract, per-category) + get_wrist_orientation() (abstract)
    fsw_ast.py                # FSW sign string -> AST, via the real signwriting.formats.fsw_to_sign
    fsw_symbol_key.py          # decodes one symbol key -> base_hex/fill/rotation (full ISWA range, not just Cat 1)
    pose_table.py                # generic PoseTable[PoseT] (base_hex-keyed) + HAND_POSE_TABLE, the Category 1 instance
    hand_symbol.py                 # HandSymbol -- the one class for all 261 Category 1 base symbols
    registry.py                     # build_symbol() / symbol_from_fsw() -- dispatches by category
    fswr_converter.py                # AST -> FSWR: ast_to_fswr() / fsw_to_fswr()
    types.py                          # JointAngle, FingerPose, ThumbPose, HandJointPose, HandSide
    renderable_symbol.py               # FSWRenderableSymbol
    renderer.py                         # HandMeshRenderer3D, HandSkeleton, HandRigProvider (Protocol)
  data/
    iswa_valid_combinations.json  # from the real ISWA font's cmap, all 652 base symbols
    hand_joint_poses.json          # real, dataset-derived joint poses, Category 1's 261, keyed by base_hex
  demo.py                      # python -m fsw_r.demo
tests/
  test_iswa_structure.py
  test_iswa_data.py
  test_pose_table.py
  test_hand_symbol.py
  test_wrist_orientation.py
  test_hand_side.py
  test_fsw_symbol_key.py
  test_fsw_ast.py
  test_registry.py
  test_fswr_converter.py
```

Category 1 (Hands) is complete: all 261 base symbols, data-driven through
`HandSymbol` + `pose_table.py` (real-named, joint-pose-derived from real
data -- see "Notes / open items" below) -- not 261 separate classes. See
`ROADMAP.md` for the plan for the other 6 ISWA categories (Movement,
Dynamics, Head & Face, Trunk & Limb, Location, Punctuation -- 7 categories
total, not 8; see `ROADMAP.md`'s category table for why), not yet started.
Adding one is now "one more `_CATEGORY_SYMBOL` entry in `registry.py`" +
that category's own new pose type/symbol class/data file -- see "Adding a
new category" below.

## Setup

```bash
pip install -e ".[dev]"
```

## Run

```bash
python -m fsw_r.demo
pytest
mypy --strict
```

## Visualization

There is no matplotlib/3D-plotting code in this package on purpose. A visual
sanity-check renderer (stick-figure hand via matplotlib) lives in the
sibling package `../fsw-r-viz`, which depends on `fsw-r` -- not the reverse.
This package stays free of any visualization dependency.

## Adding a new category

Category 1 (Hands) went through both the wrong pattern and the right one,
worth knowing before starting Category 2: it began as 261 separate
`FSWRenderableSymbol` subclasses (one per base symbol, each registered via
a `@register_symbol` decorator), then got refactored to the data-driven
design described above once it became clear 96% of those classes only
differed by 15 numbers, not behavior (see `PROGRESS.md`'s "Refactor tang
Group sang data-driven" entry). Do the data-driven version from the start
for a new category:

1. Design that category's own pose type (e.g. a "motion path" for
   Category 2 -- a keyframe sequence, not a static `HandJointPose`) in
   `core/types.py` or its own module.
2. Write a script (like `scripts/export_joint_poses.py`/
   `scripts/gen_valid_combinations.py`) or hand-author
   `data/<category>_poses.json`, keyed by `base_hex` (hex string, e.g.
   `"22b"`), with the pose fields plus a `name`/`symbol_id` field for
   readability -- follow `hand_joint_poses.json`'s shape.
3. In `core/pose_table.py` (or a new module), instantiate a
   `PoseTable[YourPoseT]("data/<category>_poses.json", your_parse_fn,
   expected_count=N)` -- `PoseTable`'s own class body never needs to
   change; it doesn't know what `HandJointPose` is.
4. Write `YourCategorySymbol(FSWRenderableSymbol)`, analogous to
   `HandSymbol`: `get_joint_pose()` looks itself up in your new table by
   `self.base_hex`; `get_wrist_orientation()` -- don't assume Category 1's
   fill/rotation formula generalizes, verify against that category's own
   chart/spec first (see `ROADMAP.md`'s risk note); `hand_side` -- don't
   assume Category 1's `rotation`-based rule generalizes either (it
   measurably doesn't for Category 2, see `ROADMAP.md`'s Phase 2 section)
   -- return `None` if the category doesn't encode a hand at all.
5. In `core/registry.py`, add one entry:
   `_CATEGORY_SYMBOL[2] = YourCategorySymbol`. That's the only change to an
   existing `core/` file -- `fsw_symbol_key.py`, `fsw_base_symbol.py`,
   `iswa_data.py`, `renderer.py`, and `pose_table.py`'s `PoseTable` class
   are already category-agnostic.

## Notes / open items

- All 261 of ISWA Category 1's base symbols are registered (`HandSymbol`
  covers all of them via `pose_table.py`, keyed by `base_hex`).
  `symbol_from_fsw()` / `fsw_to_fswr()` raise a clear `ValueError` naming
  the unsupported category for any key outside Category 1 -- see
  `../ROADMAP.md` for the other 6 ISWA categories, not yet started.
- Joint angles for all 261 registered base symbols are derived from real
  data, not guessed: median 3D hand keypoints (MediaPipe v0.10.3, 48 crops)
  from
  [sign-language-processing/3d-hands-benchmark](https://github.com/sign-language-processing/3d-hands-benchmark),
  a real photographed hand posing all 261 ISWA Category-1 shapes at 6
  orientations. Flexion = angle between consecutive bone vectors
  (wrist->mcp->pip->dip->tip). This is MediaPipe's own pose *estimate* on a
  real photo, not verified motion-capture ground truth (that benchmark
  doesn't claim otherwise either) -- but it's real photographed data, not
  an invented number. `abduction` (finger spread) isn't measured by this
  method and is still a guess.
- `fill`'s "Floor Plane" component (`_fill_plane_degrees`) pitches the whole
  hand 90 degrees, matching the chart's *description* ("top view, arm
  reaching down") -- but the chart itself shows this from a camera looking
  down from above, and neither `fsw-r` nor `fsw-r-viz` change the camera to
  match. So the quaternion is internally consistent (pinned by
  `test_fill_plane_differs_between_wall_and_floor`) but hasn't been visually
  cross-checked against the chart's top-view photos the way the rotation
  and facing behavior were -- worth another look once a real rig exists.
- `JointAngle.abduction`'s sign may need flipping for the LEFT hand,
  depending on your 3D rig's convention -- not handled yet, since no real rig
  exists to verify against.
- `data/hand_joint_poses.json` is an internal data source (`base_hex` ->
  joint pose), not a public export API -- it has no wrist quaternion
  (that's a function of fill/rotation, computed at render time, not
  precomputed data). If the final render target ends up being a web viewer
  (three.js) rather than Blender/Open3D, add a `to_dict()`/`asdict()` based
  exporter for a symbol's `HandJointPose` + computed wrist `Rotation`
  quaternion -- the core layer doesn't need to change for that.
- Written and tested against Python 3.10 (the environment available locally);
  the design brief called for 3.11+ but nothing here uses a 3.11-only
  feature, so it also runs unmodified on 3.11/3.12.
