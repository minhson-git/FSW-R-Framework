"""Bone-segment lengths for the forward-kinematics chain in
``forward_kinematics.py``. The repo has no such data before this module --
``core/hand_joint_poses.json`` stores JOINT ANGLES only (from
3d-hands-benchmark's MediaPipe-on-real-photos measurement), never bone
LENGTHS, and ``fsw-r-viz/hand_geometry.py``'s stick-figure numbers are its
own author's un-cited, debug-only estimate. This is a NEW assumption for the
project -- see PROGRESS.md's export-layer entry / "giả định chưa kiểm chứng"
list.

**Cited source for the RELATIVE finger shape** (proximal/middle/distal
phalanx lengths per finger; thumb proximal/distal): Wicaksono et al.,
"Radiological analysis of finger length ratio and dimensional profile of
finger anatomy morphology", Journal of Musculoskeletal Surgery and Research
-- https://journalmsr.com/radiological-analysis-of-finger-length-ratio-and-dimensional-profile-of-finger-anatomy-morphology/
(Indonesian adult population, radiological/X-ray measurement). Kept as the
``_RAW_*`` values below; only their RELATIVE proportions matter here (this
task changes the hand's overall SCALE, not its relative shape).

**Overall SCALE anchored to a single stature** (this task, Part A1). Before
this, the ``_RAW_*`` millimetre values stood on their own, un-anchored, and
described a hand ~1.5x too small relative to the body ``body_geometry.py``
derives from ``ASSUMED_STATURE_MM`` (measured: palm/shoulder 0.15 vs
anthropometric ~0.24). Now every length is ``_RAW_* x _HAND_SCALE``, where
``_HAND_SCALE`` anchors the hand's extended length to ``ASSUMED_STATURE_MM``
via ``HAND_LENGTH_TO_STATURE`` -- so hand and body derive from ONE height.

**Why HAND_LENGTH_TO_STATURE = 0.1197, not the anthropometric 0.108**: this
hand's palm/finger proportion is ~0.43 (palm = wrist->middle-MCP = the
metacarpal, itself a derived "MC ~= 1.5 x proximal phalanx" estimate flagged
below), vs the anthropometric ~0.50 (palm ~= half of hand). At the
anthropometric 0.108 the palm would be ~0.18 of shoulder width, below the
invariant floor in ``tests/test_hand_body_scale.py``. 0.1197 is the value
that jointly satisfies all three scale invariants (palm/shoulder,
palm/forearm, hand/stature) GIVEN the hand's fixed relative shape -- it lands
near the top of B3's [0.10, 0.12] and the bottom of B1's [0.20, 0.28], a
deliberately tight fit that is a direct symptom of the ~0.43-vs-0.50
metacarpal discrepancy the brief puts OUT OF SCOPE (see
``body_geometry.py``'s "18% difference" note). Fixing THAT (rederiving the
metacarpal so palm ~= half hand) would change the hand's relative shape and
therefore MPJPE -- out of scope here.

**Relative-shape estimates NOT from Wicaksono (flagged, unchanged by this
task -- these are ratios inside the raw shape, kept as-is):**
- Each finger's METACARPAL length -- the study reports only phalanx lengths
  but proposes "MC ~= 1.5 x proximal phalanx"; used per finger. An
  extrapolation the study suggests, not a measurement.
- The thumb's metacarpal -- same "MC ~= 1.5 x PP", WEAKER (a thumb's
  metacarpal is anatomically shorter relative to its proximal phalanx than a
  finger's; no thumb-specific ratio found). The shakiest value here.
- Lateral knuckle spacing across the palm -- no citation found; a plain
  authored estimate.
"""

from __future__ import annotations

from fsw_r.export.anthropometry import ASSUMED_STATURE_MM, HAND_MM_TO_BODY_UNITS

__all__ = [
    "HAND_MM_TO_BODY_UNITS",  # re-exported from anthropometry for the FK chain
    "HAND_LENGTH_TO_STATURE",
    "HAND_LENGTH_MM",
    "HAND_SCALE",
    "FINGER_PHALANX_LENGTHS_MM",
    "FINGER_METACARPAL_LENGTH_MM",
    "THUMB_PHALANX_LENGTHS_MM",
    "THUMB_METACARPAL_LENGTH_MM",
    "KNUCKLE_LATERAL_SPACING_MM",
]

# --- Cited RAW shape (Wicaksono et al.) -- relative proportions only ---
# (proximal, middle, distal) phalanx length in mm, per finger.
_RAW_FINGER_PHALANX_MM: dict[str, tuple[float, float, float]] = {
    "index": (39.18, 21.34, 15.30),
    "middle": (43.63, 25.80, 16.23),
    "ring": (40.97, 24.49, 16.64),
    "pinky": (31.85, 17.05, 14.88),
}
# (proximal, distal) for the thumb (only 2 phalanges).
_RAW_THUMB_PHALANX_MM: tuple[float, float] = (29.79, 20.85)
_RAW_KNUCKLE_LATERAL_SPACING_MM: float = 8.0
_METACARPAL_TO_PROXIMAL = 1.5  # "MC ~= 1.5 x proximal phalanx" (derived, see docstring)

# Raw extended wrist->middle-fingertip chain length (middle metacarpal + its
# 3 phalanges), the raw shape's own length before anchoring.
_RAW_HAND_LENGTH_MM: float = (
    _METACARPAL_TO_PROXIMAL * _RAW_FINGER_PHALANX_MM["middle"][0] + sum(_RAW_FINGER_PHALANX_MM["middle"])
)

# --- Overall scale, anchored to ONE stature (this task) ---
# Hand's extended length as a fraction of stature. See docstring for why this
# is 0.1197 and not the anthropometric 0.108.
HAND_LENGTH_TO_STATURE: float = 0.1197
HAND_LENGTH_MM: float = HAND_LENGTH_TO_STATURE * ASSUMED_STATURE_MM
_HAND_SCALE: float = HAND_LENGTH_MM / _RAW_HAND_LENGTH_MM

# Public alias of the single uniform scale factor. ``forward_kinematics.py``
# has ONE piece of hand geometry that is NOT a bone_lengths constant -- the
# thumb's CMC base offset ``_THUMB_BASE_OFFSET_MM`` (where the thumb attaches
# to the palm) -- and it must scale by the SAME factor as every bone, or the
# thumb's attachment point stays put while its bones grow, which changes the
# hand's RELATIVE shape and therefore MPJPE (validation/ normalizes away
# overall scale but NOT relative shape -- see reports/fk_accuracy.md and
# tests/test_hand_body_scale.py). Exported so that offset stays uniform too.
HAND_SCALE: float = _HAND_SCALE

# --- Public scaled lengths (uniform _HAND_SCALE preserves relative shape) ---
FINGER_PHALANX_LENGTHS_MM: dict[str, tuple[float, float, float]] = {
    finger: (raw[0] * _HAND_SCALE, raw[1] * _HAND_SCALE, raw[2] * _HAND_SCALE)
    for finger, raw in _RAW_FINGER_PHALANX_MM.items()
}
FINGER_METACARPAL_LENGTH_MM: dict[str, float] = {
    finger: _METACARPAL_TO_PROXIMAL * raw[0] * _HAND_SCALE for finger, raw in _RAW_FINGER_PHALANX_MM.items()
}
THUMB_PHALANX_LENGTHS_MM: tuple[float, float] = (
    _RAW_THUMB_PHALANX_MM[0] * _HAND_SCALE,
    _RAW_THUMB_PHALANX_MM[1] * _HAND_SCALE,
)
THUMB_METACARPAL_LENGTH_MM: float = _METACARPAL_TO_PROXIMAL * _RAW_THUMB_PHALANX_MM[0] * _HAND_SCALE
KNUCKLE_LATERAL_SPACING_MM: float = _RAW_KNUCKLE_LATERAL_SPACING_MM * _HAND_SCALE
