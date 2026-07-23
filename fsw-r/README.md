# fsw-r

Renders ISWA/FSW (SignWriting) hand symbols in 3D by adding a joint-pose layer
on top of real FSW symbol-key parsing.

## Real FSW parsing, not invented data

`core/fsw_symbol_key.py` parses actual ISWA/FSW symbol keys (e.g. `"S10011"`)
using the same key format and category/group ranges as the reference
implementation, [sutton-signwriting/core](https://github.com/sutton-signwriting/core)
(cross-checked against its installable Python port, the
[`signwriting`](https://pypi.org/project/signwriting/) PyPI package, which
this project depends on for `fsw_to_sign`-compatible parsing). The category
(Hands, `0x100`-`0x204`) and 10-group boundaries come directly from that
project's `src/fsw/fsw-structure.js`; group 1 (`0x100`-`0x10d`, 14 symbols)
matches the 14 base symbols listed at
[signwriting.org's Group 1 page](https://www.signwriting.org/lessons/iswa/group01/),
whose own links confirm base_symbol_number 1 = "Index" and 7 = "Index Bent".

`core/registry.py` maps `(group, base_symbol_number)` to the concrete
`FSWRenderableSymbol` subclass that implements it; `symbol_from_fsw("S10012")`
parses the real key and returns an actual `BaseSymbol01_01_001_Index`
instance -- not a hand-rolled stand-in.

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

## Layout

```
src/fsw_r/
  core/
    fsw_base_symbol.py      # category/group/base/fill/rotation + hand_side + get_wrist_orientation() (abstract)
    fsw_symbol_key.py        # real FSW symbol-key parsing (sourced from sutton-signwriting/core)
    registry.py               # @register_symbol + symbol_from_fsw() factory
    types.py                  # JointAngle, FingerPose, ThumbPose, HandJointPose, HandSide
    renderable_symbol.py       # FSWRenderableSymbol
    renderer.py                # HandMeshRenderer3D, HandSkeleton, HandRigProvider (Protocol)
  groups/
    group_01_index_finger.py  # SymbolGroup1IndexFinger + its base symbols (@register_symbol'd)
  demo.py                      # python -m fsw_r.demo
tests/
  test_group_01.py
  test_hand_side.py
  test_fsw_symbol_key.py
  test_registry.py
```

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

## Adding a new group (e.g. Group 2 -- Middle Finger)

1. Create `src/fsw_r/groups/group_02_middle_finger.py`.
2. Define `SymbolGroup2MiddleFinger(FSWRenderableSymbol, ABC)` with a
   `_default_joint_pose()` giving the group's baseline hand shape, and a
   default `get_joint_pose()` that returns it.
3. For each base symbol in the group (01-02-001, 01-02-002, ...), define a
   class inheriting `SymbolGroup2MiddleFinger`, decorated with
   `@register_symbol(group=2, base_symbol_number=N)`, that calls
   `super().__init__()` with the right `base_symbol_number`, implements
   `get_wrist_orientation()`, and only overrides `get_joint_pose()` if that
   symbol needs a distinct pose (e.g.
   `dataclasses.replace(self._default_joint_pose(), middle=...)`).

No other file needs to change -- `renderer.py`, `types.py`,
`renderable_symbol.py`, `fsw_symbol_key.py`, and `registry.py` are
group-agnostic by design, and `hand_side` is already handled once and for
all in `FSWBaseSymbol`. This is the pattern to repeat for the remaining ~9
groups / ~650 base symbols in ISWA Category 1 -- each one becomes parseable
via `symbol_from_fsw()` the moment its module is imported and its class is
`@register_symbol`'d.

## Notes / open items

- `symbol_from_fsw()` only knows about base symbols whose module has been
  imported somewhere (registration happens via the `@register_symbol`
  decorator at import time). If you call it without importing
  `fsw_r.groups.group_01_index_finger` first, it'll raise `ValueError` even
  for `"S10011"`.
- Only 2 of ISWA's ~652 Category-1 base symbols are registered so far
  ("Index" and "Index Bent"). `symbol_from_fsw()` raises a clear
  `ValueError` naming the missing `(group, base_symbol_number)` for anything
  else -- that's expected until more groups are added, not a bug.
- Joint angles in `group_01_index_finger.py` are a baseline guess, not
  measured from a real rig/mesh -- expect to tune them once one is available.
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
