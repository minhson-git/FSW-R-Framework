"""signbox (x, y) -> body-space 3D coordinate.

Measured on 60,000 signs of SignBank+:

    x range: 278-705, median 489
    y range: 276-809, median 494
    head/face (Category 4) symbols' median y: 483
    hand (Category 1) symbols' median y:      496

The head sits ABOVE the hands on the body. Head's median y (483) is
SMALLER than hands' (496). So ``y`` increases DOWNWARD -- screen
coordinates, not math coordinates. Getting this sign wrong flips every
gesture upside down while every other test still passes (nothing else
would look "obviously broken" the way a mirrored left/right would) -- see
``tests/test_anchor.py``'s ``test_smaller_y_gives_a_higher_position``, the
single most important test in this package.

The z axis has no signbox equivalent -- Category 2's ``MotionPath.plane``
supplies it instead (WALL: motion stays near z=0; FLOOR: motion has a real
z component). ``core/movement_paths.py``'s ``sample_trajectory()`` already
handles this -- ``build.py`` reuses it rather than reimplementing.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

SIGNBOX_CENTER = 500.0
SIGNBOX_HALF_SCALE = 250.0

# UNVERIFIED ASSUMPTION: converts MotionPath.amplitude's own units (its
# generated default is 10.0, see scripts/gen_movement_paths.py) into
# anchor()'s roughly -1..+1 body-space units. Not calibrated against any
# real body/rig -- see PROGRESS.md's Phase 3 entry.
SIGNBOX_TO_BODY_SCALE = 0.1


def anchor(x: int, y: int) -> NDArray[np.float64]:
    """signbox (x, y) -> body-space (u, v, 0). u: positive = the signer's
    right. v: positive = up -- INVERTED from y (see module docstring)."""
    u = (x - SIGNBOX_CENTER) / SIGNBOX_HALF_SCALE
    v = (SIGNBOX_CENTER - y) / SIGNBOX_HALF_SCALE
    return np.array([u, v, 0.0])
