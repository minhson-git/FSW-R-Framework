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

# How far, in fsw_r body-space units, the edge of the signbox's normalized
# half-range (|x-500| = 250) sits from the body's centre line. Set to the
# body's own SHOULDER half-width -- ``body_geometry.SHOULDER_WIDTH_MM *
# HAND_MM_TO_BODY_UNITS / 2`` = 0.259 x 1700 x 0.01 / 2 ~= 2.20 -- so a hand at
# the edge of the signbox reaches the shoulder line and two hands land at their
# real separation.
#
# Kept as a plain constant (not imported from body_geometry) so ``timeline/``
# stays self-contained -- ``export/`` consumes ``timeline/``, not the reverse;
# this mirrors how ``pose_export.BODY_UNITS_TO_PIXELS`` is a documented
# calibration constant, verified by rendering, rather than a live import. If
# the body's stature/shoulder fraction ever changes, re-derive this to match.
#
# BEFORE this (MVP-1 -> MVP-2): ``anchor`` normalized the signbox to +-1 while
# the stature-derived body spanned +-2.2, an unreconciled ~2.2x mismatch. With
# one central hand (MVP-1) it only made the hand sit small and central; with
# two hands (MVP-2) it collapsed both into a tiny box so they overlapped and
# the arms reached awkwardly inward. See PROGRESS.md's Pha 17.
SIGNBOX_BODY_HALF_EXTENT = 2.20

# UNVERIFIED ASSUMPTION: converts MotionPath.amplitude's own units (its
# generated default is 10.0, see scripts/gen_movement_paths.py) into a
# body-space movement size. Left as a LOCAL-gesture scale, separate from the
# position scale above (a movement is a local wiggle around the hand's placed
# position, not a signbox-wide displacement). Not calibrated against any real
# body/rig -- see PROGRESS.md's Phase 3 entry.
SIGNBOX_TO_BODY_SCALE = 0.1


def anchor(x: int, y: int) -> NDArray[np.float64]:
    """signbox (x, y) -> body-space (u, v, 0), scaled so the signbox spans the
    body (see ``SIGNBOX_BODY_HALF_EXTENT``). u: positive = the signer's right.
    v: positive = up -- INVERTED from y (see module docstring)."""
    u = (x - SIGNBOX_CENTER) / SIGNBOX_HALF_SCALE * SIGNBOX_BODY_HALF_EXTENT
    v = (SIGNBOX_CENTER - y) / SIGNBOX_HALF_SCALE * SIGNBOX_BODY_HALF_EXTENT
    return np.array([u, v, 0.0])
