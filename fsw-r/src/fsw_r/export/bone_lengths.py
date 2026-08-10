"""Bone-segment lengths for the forward-kinematics chain in
``forward_kinematics.py``. The repo has no such data before this module --
``core/hand_joint_poses.json`` stores JOINT ANGLES only (from
3d-hands-benchmark's MediaPipe-on-real-photos measurement), never bone
LENGTHS, and ``fsw-r-viz/hand_geometry.py``'s stick-figure numbers are its
own author's un-cited, debug-only estimate (see that module's docstring:
"arbitrary units"). This is a NEW assumption for the project -- see
PROGRESS.md's export-layer entry / "giả định chưa kiểm chứng" list.

**Cited source for phalanx lengths** (index/middle/ring/pinky proximal,
middle, distal; thumb proximal, distal): Wicaksono et al., "Radiological
analysis of finger length ratio and dimensional profile of finger anatomy
morphology", Journal of Musculoskeletal Surgery and Research --
https://journalmsr.com/radiological-analysis-of-finger-length-ratio-and-dimensional-profile-of-finger-anatomy-morphology/
(Indonesian adult population, radiological/X-ray measurement). Reported as
mean length in millimeters per finger per phalanx.

**NOT covered by that source, so estimated/derived separately (flagged
individually below):**
- Each finger's METACARPAL length (the WRIST-to-MCP-knuckle segment) --
  the cited study reports only phalanx lengths, but states its own
  proposed relationship "MC ~= 1.5 x proximal phalanx length" without
  giving that as measured data. Used here, applied to each finger's own
  measured proximal-phalanx length -- an extrapolation the study itself
  suggests, not a direct measurement.
- The thumb's metacarpal length -- same "MC ~= 1.5 x PP" relationship
  applied to the thumb's own proximal phalanx, WEAKER than the finger
  case above: a thumb's metacarpal is anatomically shorter relative to its
  own proximal phalanx than a finger's is (a well-known qualitative fact),
  and no source found gives a thumb-specific ratio. Used anyway as the
  least-arbitrary available number, explicitly flagged here as the
  shakiest value in this module.
- Lateral knuckle spacing (how far apart the 4 fingers' MCP knuckles sit
  across the palm) -- the cited study is about finger LENGTH, not palm
  BREADTH; no citation was found for this specific measurement. A plain
  authored estimate, not derived from any study.
- The thumb's attachment offset/rotation relative to the palm -- no
  citation covers 3D attachment angle, only lengths. Reuses the same
  qualitative convention already visually verified in
  ``fsw-r-viz/hand_geometry.py`` (``_THUMB_BASE_ROTATION``), which is
  itself an authored estimate, not a new one invented from scratch here.
- The millimeter-to-body-space-unit scale factor -- ``timeline/``'s
  body-space coordinates have no established real-world calibration
  (``timeline/anchor.py``'s own ``SIGNBOX_TO_BODY_SCALE`` is itself
  flagged unverified), so there is nothing to convert "real mm" against.
  Chosen so a real hand's length lands in the same order of magnitude as
  a typical movement trajectory's displacement, not calibrated.
"""

from __future__ import annotations

# (proximal, middle, distal) phalanx length in mm, per finger -- cited,
# see module docstring.
FINGER_PHALANX_LENGTHS_MM: dict[str, tuple[float, float, float]] = {
    "index": (39.18, 21.34, 15.30),
    "middle": (43.63, 25.80, 16.23),
    "ring": (40.97, 24.49, 16.64),
    "pinky": (31.85, 17.05, 14.88),
}

# WRIST -> MCP knuckle offset magnitude in mm, per finger. Derived, not
# measured -- see module docstring ("MC ~= 1.5 x proximal phalanx").
FINGER_METACARPAL_LENGTH_MM: dict[str, float] = {
    finger: 1.5 * lengths[0] for finger, lengths in FINGER_PHALANX_LENGTHS_MM.items()
}

# (proximal, distal) phalanx length in mm for the thumb -- cited (the thumb
# has only 2 phalanges, no middle phalanx).
THUMB_PHALANX_LENGTHS_MM: tuple[float, float] = (29.79, 20.85)

# CMC -> MCP (thumb metacarpal) offset magnitude in mm. Derived, WEAKER than
# the finger case -- see module docstring.
THUMB_METACARPAL_LENGTH_MM: float = 1.5 * THUMB_PHALANX_LENGTHS_MM[0]

# Estimated spacing between adjacent MCP knuckles across the palm row, mm --
# NOT from the cited study (see module docstring). A plausible adult value,
# not measured or calibrated.
KNUCKLE_LATERAL_SPACING_MM: float = 8.0

# UNVERIFIED: real-world millimeters -> fsw_r.timeline body-space units.
# Chosen so a real hand (wrist to middle fingertip: metacarpal + all 3
# phalanges =~ 65 + 44 + 26 + 16 =~ 151 mm) occupies roughly the same order
# of magnitude as a typical movement trajectory's own displacement
# (core/movement_paths.py's default amplitude=10.0 combined with
# timeline/anchor.py's SIGNBOX_TO_BODY_SCALE=0.1 gives displacements on the
# order of 1 body unit) -- not calibrated against any real reference. See
# PROGRESS.md's "giả định chưa kiểm chứng" list.
HAND_MM_TO_BODY_UNITS: float = 0.01
