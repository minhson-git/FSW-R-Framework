"""Immutable data type for a Category 5 (Trunk & Limb / "Body") symbol's
pose -- ISWA Group 27 (Trunk, 9 base symbols, 0x36d-0x375) and Group 28
(Limb, 9 base symbols, 0x376-0x37e).

Verified on signbank.org (``iswa/36d_sg.html`` and ``iswa/376_sg.html``,
the real ISWA 2010 HTML reference -- fetched, not guessed, see
PROGRESS.md's Category 5 entry): this category is NOT 18 independent
biomechanical poses the way Category 1's 261 hand joint poses are. Group
27's real names read as a torso-movement vocabulary (stretch / bend / twist
/ tilt / move / positions, all anchored on one compound reference symbol,
"Shoulder Hip Spine"); Group 28's real names ("Limb Combinations", "Limb
Length 1".."Limb Length 7", "Fingers") read as building blocks for a
schematic stick-figure limb of varying length, not 9 separate anatomical
joints. ``BodyPose`` reflects that structure honestly instead of forcing it
into a rig/joint-angle shape it doesn't have.

IMPORTANT -- like ``FaceExpressionPose`` (Category 4) and ``MotionPath``
(Category 2), every numeric value here is AUTHORED, not measured -- there is
no dataset keying ISWA body symbols to 3D poses. Unlike those two,
``motion_type``/``limb_length_units`` are directly TRACEABLE to the verified
real name (not invented), while ``trunk_rotation``/``shoulder_offset`` are
constant placeholders (identity / zero) across all 9 Trunk symbols: this
project has no basis yet for assigning a specific numeric angle/offset to
"Torso Curved Bend Wall" vs. "Upper Body Tilts" that would be more than a
guess, and guessing a specific number would be worse than being explicit
about not knowing it yet (same reasoning as ``MovementSymbol.hand_side``
returning ``None`` instead of a wrong rule). See ``core/pose_table.py`` and
``scripts/gen_body_poses.py`` for where these values are assembled, and
PROGRESS.md's Category 5 entry / "giả định chưa kiểm chứng" list.

Also UNVERIFIED: what ``fill``/``rotation`` mean for this category at all.
Measured on SignBank+ (257,800 signs, ``sign-language-processing/
signbank-plus``): 92.5% of Category 5 tokens use fill=0 and 88.7% use
rotation 0-7 -- both far more skewed than Category 1 (fill spans its full
6-value "Six Palm Facings" range roughly evenly) or even Category 2's
already-noisy hand_side correlation. Not enough signal to guess a formula,
so ``BodyPose`` does not vary by fill/rotation at all (keyed by ``base_hex``
only, exactly like ``HandJointPose``) -- see ``BodySymbol.hand_side``'s
docstring for the same finding stated from the corpus side.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation


class BodyPart(Enum):
    """Which of Category 5's two groups a base symbol belongs to -- see
    ``core/iswa_data.py``'s ``GROUP_START`` (group 27 = Trunk, group 28 =
    Limb, both under category 5, "trunk & limb" per the real
    ``fsw-structure.js`` category array)."""

    TRUNK = "trunk"  # Group 27, 0x36d-0x375
    LIMB = "limb"  # Group 28, 0x376-0x37e


@dataclass(frozen=True)
class BodyPose:
    """A Category 5 symbol's schematic body-diagram descriptor -- NOT a
    rigged joint-angle pose (``HandJointPose``) or a trajectory
    (``MotionPath``). See module docstring for what is/isn't verified here.

    ``part`` and ``motion_type`` are directly traceable to the symbol's
    real, verified ISWA name. ``limb_length_units`` (Group 28 only) is
    parsed straight out of the "Limb Length N" naming (0 for "Limb
    Combinations" and "Fingers", which aren't a fixed length). Turning any
    of this into an actual 3D anchor point/skeleton for a scene is
    deliberately out of this task's scope (symbol layer only, see this
    project's Category 3/5 task brief Part 0) -- left for the pha that also
    wires Category 5 into ``timeline/`` (see ROADMAP.md).
    """

    part: BodyPart
    motion_type: str
    trunk_rotation: Rotation | None  # Group 27 only; constant placeholder (identity) -- see module docstring
    shoulder_offset: NDArray[np.float64] | None  # Group 27 only; constant placeholder (zeros)
    limb_length_units: int | None  # Group 28 only; from "Limb Length N" naming (0 = Combinations/Fingers)
