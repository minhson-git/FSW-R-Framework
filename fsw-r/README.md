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
   (e.g. `"S10010"`, one AST node) into category/group/base_symbol_number/
   fill/rotation. The key-slicing technique (`base = key[:4]`, etc.) mirrors
   what the reference library itself does internally in
   `signwriting.utils.mirror.mirror_symbol` -- there's no public library
   function for this specific decomposition, so this module does it the
   same way the reference implementation does. The *group* boundaries
   (which of the 10 ASL-counting hand groups a base code falls into) are
   ISWA facts sourced from that project's `src/fsw/fsw-structure.js`
   (`ranges.hand = [0x100, 0x204]`, and the `group` array's first 10
   entries) -- cross-checked against the 14 base symbols listed at
   [signwriting.org's Group 1 page](https://www.signwriting.org/lessons/iswa/group01/),
   whose own links confirm base_symbol_number 1 = "Index" and 7 = "Index Bent".
3. **`core/registry.py`** + **`core/fswr_converter.py`** are the "AST -> FSWR"
   converter: `registry.build_symbol()` looks up the `(group,
   base_symbol_number)` in a table populated by `@register_symbol` and
   constructs the concrete `FSWRenderableSymbol` subclass;
   `fswr_converter.ast_to_fswr()` runs that over every node in an
   `FSWSignAST`, pairing each resulting object with its page position
   (`PositionedSymbol`). `fswr_converter.fsw_to_fswr(fsw)` chains all three
   stages for the common case of starting from a raw string.
   `registry.symbol_from_fsw(key)` remains as a convenience for the
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
FSWBaseSymbol                     category/group/base/fill/rotation
                                   + hand_side (concrete, derived from rotation)
                                   + get_wrist_orientation() (abstract)
    |
FSWRenderableSymbol (abstract)    + get_joint_pose() contract
    |
SymbolGroupN (abstract, per group 1..10)   default joint-angle template for the group
    |
BaseSymbolX                        uses the template as-is, or overrides get_joint_pose()
```

`HandMeshRenderer3D` depends only on `FSWRenderableSymbol` and `HandRigProvider`
(both abstract) -- it never imports a specific group or base symbol, so adding
new ones never touches the renderer.

### `rotation` encodes hand_side, not just an angle

ISWA `rotation` is a hex digit 0-f (16 values). It is split into two halves of 8:

| rotation | direction | angle | hand_side |
|---|---|---|---|
| `0`-`7` | counter-clockwise | `(rotation % 8) * 45°` | `RIGHT` |
| `8`-`f` | clockwise (mirror of the 0-7 half) | `(rotation % 8) * 45°` | `LEFT` |

16 rotation values exist -- not 8 -- precisely because `hand_side` is encoded
in *which half* `rotation` falls into; ISWA has no separate left/right field.
`FSWBaseSymbol.hand_side` is a concrete property computed purely from
`rotation` (`rotation >= 8 -> LEFT`). It lives once, at the base of the
hierarchy, and is never overridden by any `SymbolGroupN` or `BaseSymbolX` --
the rule is identical for every symbol in every group, so subclassing per
hand_side would just double the number of classes for no benefit.

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
    fsw_base_symbol.py      # category/group/base/fill/rotation + hand_side + get_wrist_orientation() (abstract)
    fsw_ast.py                # FSW sign string -> AST, via the real signwriting.formats.fsw_to_sign
    fsw_symbol_key.py          # decodes one symbol key -> category/group/base_symbol_number/fill/rotation
    registry.py                 # @register_symbol + build_symbol() / symbol_from_fsw()
    fswr_converter.py            # AST -> FSWR: ast_to_fswr() / fsw_to_fswr()
    types.py                     # JointAngle, FingerPose, ThumbPose, HandJointPose, HandSide
    renderable_symbol.py          # FSWRenderableSymbol
    renderer.py                   # HandMeshRenderer3D, HandSkeleton, HandRigProvider (Protocol)
  groups/
    group_01_index_finger.py            # 14/14 base symbols registered
    group_02_index_middle_fingers.py     # 16/16 base symbols registered
    group_03_index_middle_thumb.py       # 38/38 base symbols registered
    group_04_four_fingers.py             # 8/8 base symbols registered
    group_05_five_fingers.py             # 58/58 base symbols registered
    group_06_baby_finger.py              # 30/30 base symbols registered
    group_07_ring_finger.py              # 22/22 base symbols registered
    group_08_middle_finger.py            # 19/19 base symbols registered
    group_09_index_thumb.py              # 40/40 base symbols registered
    group_10_thumb.py                    # 16/16 base symbols registered
  demo.py                      # python -m fsw_r.demo
tests/
  test_group_01.py .. test_group_10.py    # one per group
  test_hand_side.py
  test_fsw_symbol_key.py
  test_fsw_ast.py
  test_registry.py
  test_fswr_converter.py
```

All 10 Hands groups are now complete: all 261 of ISWA Category 1's base
symbols are registered, real-named, and joint-pose-derived from real data
(see "Notes / open items" below) -- see `ROADMAP.md` for the plan for the
other 7 ISWA categories (Movement, Dynamics, Head & Face, Trunk, Limb,
Location, Punctuation), not yet started.

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

## Adding a new group

Group 2 ("Index & Middle Fingers", ASL handshape "2") is a worked example of
this in `groups/group_02_index_middle_fingers.py`. The steps, in general:

1. Find the group's real name and base symbol names/numbers at
   `https://www.signwriting.org/lessons/iswa/groupNN/` (don't guess these --
   they're checkable).
2. Create `src/fsw_r/groups/group_0N_<name>.py`.
3. Define `SymbolGroupN<Name>(FSWRenderableSymbol, ABC)` with a
   `_default_joint_pose()` giving the group's baseline hand shape, and a
   default `get_joint_pose()` that returns it.
4. For each base symbol in the group (0N-0N-001, 0N-0N-002, ...), define a
   class inheriting `SymbolGroupN<Name>`, decorated with
   `@register_symbol(group=N, base_symbol_number=M)`, that calls
   `super().__init__(category=1, group=N, base_symbol_number=M, fill=fill, rotation=rotation)`
   in its `__init__(self, fill: int, rotation: int)`, implements
   `get_wrist_orientation()` (typically just `return
   self._default_wrist_orientation()` -- the rotation/fill formula is
   generic, not group-specific, see "`fill` is the Six Palm Facings" above),
   and only overrides `get_joint_pose()` if that particular base symbol
   needs a distinct pose (e.g.
   `dataclasses.replace(self._default_joint_pose(), middle=...)`).
5. To find that base symbol's real FSW key for testing: base hex code =
   the group's start boundary (see `_HAND_GROUP_START` in
   `fsw_symbol_key.py`) + `(base_symbol_number - 1)`. E.g. group 2 starts at
   `0x10e`, so base_symbol_number 1 is `0x10e` -- key `"S10e" + fill + rotation`,
   e.g. `"S10e10"` for fill=1, rotation=0.
6. Import the new module somewhere it'll run before you call
   `symbol_from_fsw`/`fsw_to_fswr` (a test file's top-level import is
   enough) -- registration happens at import time.

No other file needs to change -- `renderer.py`, `types.py`,
`renderable_symbol.py`, `fsw_ast.py`, `fsw_symbol_key.py`, `registry.py`,
and `fswr_converter.py` are group-agnostic by design, and `hand_side` is
already handled once and for all in `FSWBaseSymbol`. This is the pattern to
repeat for the remaining ~9 groups / ~650 base symbols in ISWA Category 1 --
each one becomes parseable via `symbol_from_fsw()` / `fsw_to_fswr()` the
moment its module is imported and its class is `@register_symbol`'d.

## Notes / open items

- `symbol_from_fsw()` and `fsw_to_fswr()` only know about base symbols whose
  module has been imported somewhere (registration happens via the
  `@register_symbol` decorator at import time). If you call either without
  importing `fsw_r.groups.group_01_index_finger` first, they'll raise
  `ValueError` even for `"S10011"`.
- All 261 of ISWA Category 1's base symbols are now registered (all 10
  groups complete). `symbol_from_fsw()` / `fsw_to_fswr()` raise a clear
  `ValueError` naming the missing `(group, base_symbol_number)` only for
  keys outside Category 1 (Hands) -- see `../ROADMAP.md` for the other 7
  ISWA categories, not yet started.
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
- No JSON export exists yet. If the final render target ends up being a web
  viewer (three.js) rather than Blender/Open3D, add a `to_dict()`/`asdict()`
  based exporter for `HandJointPose` + the wrist `Rotation` quaternion --
  the core layer doesn't need to change for that.
- Written and tested against Python 3.10 (the environment available locally);
  the design brief called for 3.11+ but nothing here uses a 3.11-only
  feature, so it also runs unmodified on 3.11/3.12.
