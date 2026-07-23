# fsw-r-viz

Matplotlib-based 3D stick-figure renderer used to sanity-check `fsw-r`
joint poses and wrist orientations visually, without needing a real rig/mesh.

This is a **separate package** from `fsw-r`. `fsw-r` (the core symbol/pose
library) has no dependency on this package or on matplotlib -- it only
exposes the public types (`FSWRenderableSymbol`, `HandJointPose`, ...) that
`fsw-r-viz` consumes. This package depends on `fsw-r`, never the other way
around.

## Setup

`fsw-r` is an unpublished local sibling package, so install it first, then
install this package:

```bash
pip install -e ../fsw-r
pip install -e ".[dev]"
```

## Run

```bash
python -m fsw_r_viz.demo   # saves output/index_finger_rotations.png
pytest
mypy --strict
```

## Layout

```
src/fsw_r_viz/
  hand_geometry.py   # approximate bone lengths/positions + forward kinematics + mirror_for_left_hand
  plot_hand.py        # matplotlib 3D rendering (render_symbol_to_file, render_symbols_grid)
  demo.py             # python -m fsw_r_viz.demo
tests/
  test_hand_geometry.py
  test_plot_hand.py
```

## Left-hand rendering

`fsw-r`'s `symbol.hand_side` comes from ISWA's `rotation` encoding (0-7 ->
`RIGHT`, 8-15 -> `LEFT`; see `fsw-r`'s README for the full rule). A left hand
is a *mirror image* of a right hand, not a rotation of one -- `fsw-r`'s real
renderer models this by picking a genuinely separate rig per `hand_side`
(`HandRigProvider`), never by rotating a single rig.

This package has no real rig -- `hand_geometry.py` only knows how to build a
RIGHT-hand stick figure from bone lengths and forward kinematics. So the
equivalent "pick the other rig" step here is `mirror_for_left_hand()`: it
flips the x axis (the pinky<->thumb spread axis) of the RIGHT-hand geometry
*before* the wrist orientation is applied, whenever `symbol.hand_side ==
HandSide.LEFT`. This is a debug-visualization stand-in, not what a real rig
integration would do -- a real integration should still load a distinct
LEFT-hand mesh/skeleton rather than mirroring coordinates.
