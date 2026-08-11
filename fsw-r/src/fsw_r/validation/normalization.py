"""Puts a set of 21 MediaPipe hand landmarks into a canonical reference
frame (translation/rotation/scale removed), so landmarks from two different
sources become comparable at all.

**Why this has to happen before any error is measured** (Part B of this
package's task brief, called "chỗ dễ sai nhất"): the ground truth
(``sign-language-processing/3d-hands-benchmark``, real photographed hands)
and this project's forward-kinematics output (``export/
forward_kinematics.py``, an authored rig at an arbitrary wrist
position/orientation/scale) live in completely different coordinate
systems. Comparing their raw landmark coordinates would measure "how
differently were these two things positioned in space," not "how
differently shaped are these two hands" -- the actual question. Skip this
step and every error number downstream is meaningless.

**Uses the EXACT SAME normalization
``sign-language-processing/synthetic-signwriting``'s own ``hands.py`` uses
to build the ground truth this project's eval script compares against**
(verified by reading that module's real source, not guessed): a plane
through ``(WRIST, PINKY_MCP, INDEX_FINGER_MCP)``, a line from ``WRIST`` to
``MIDDLE_FINGER_MCP``, scaled to size 150. Using a different normalization
here would silently reintroduce exactly the apples-to-oranges problem this
module exists to prevent, even though both sides would individually look
"normalized."

**A real, verified problem found in ``PoseNormalizer`` itself, and how this
module resolves it:** the plane's normal has two mathematically valid
directions (+N and -N); ``PoseNormalizer.get_normal()`` picks one via a
raw cross product with no fixed sign convention. For most inputs this is
harmless, but when the 3 plane points already lie flat in a plane (exactly
what happens to an ALREADY-normalized pose, since normalizing puts those 3
points at z=0 by construction), the cross product's sign becomes a
coin-flip driven by floating-point noise in that specific input -- **this
project's own normalizer, called through this exact PoseNormalizer config,
is NOT idempotent on its own**: empirically confirmed on real ground truth
data (not just this project's own FK output, so it is not a bug specific to
this project's forward kinematics) -- see
``tests/test_normalization.py``/PROGRESS.md's evaluation-layer entry for
the measurement.

That ambiguity is not just a test-hygiene problem -- it also means two
INDEPENDENTLY normalized poses (ground truth from real photos vs. this
project's FK output) can land on OPPOSITE sides of that flip purely by
chance, for reasons unrelated to how similarly shaped the two hands
actually are. ``normalize_landmarks()`` below fixes this deterministically
by choosing a canonical sign after calling ``PoseNormalizer``: it enforces
that the mean z of the 5 fingertips (a point set far from the ambiguous
plane, so its sign is a robust, not-near-zero signal -- unlike the plane
points themselves) is >= 0, flipping the whole pose's z axis if it isn't.
This is an ADDITION on top of the library's exact hands.py configuration,
not a deviation from it -- the plane/line/size all stay identical.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from numpy import ma
from numpy.typing import NDArray
from pose_format import Pose
from pose_format.numpy import NumPyPoseBody
from pose_format.pose_header import PoseHeader, PoseHeaderDimensions
from pose_format.utils.holistic import HAND_POINTS, holistic_hand_component
from pose_format.utils.normalization_3d import PoseNormalizer

# Matches sign-language-processing/synthetic-signwriting's hands.py exactly
# -- see module docstring.
NORMALIZATION_SIZE = 150.0

# The 5 fingertips, used only as a robust sign-canonicalization anchor (see
# module docstring) -- far from the (WRIST, PINKY_MCP, INDEX_FINGER_MCP)
# plane for essentially every real or authored hand pose, so their mean z
# is a stable, non-near-zero signal even where the plane points themselves
# (z=0 by construction) obviously can't be used for this.
_FINGERTIP_NAMES = ("THUMB_TIP", "INDEX_FINGER_TIP", "MIDDLE_FINGER_TIP", "RING_FINGER_TIP", "PINKY_TIP")
_FINGERTIP_INDICES = [HAND_POINTS.index(name) for name in _FINGERTIP_NAMES]


def _single_hand_header() -> PoseHeader:
    """A minimal header with only RIGHT_HAND_LANDMARKS (21 points) -- just
    enough for ``header.normalization_info()`` to resolve point NAMES to
    the correct integer indices, the same way hands.py's own
    ``get_hand_normalizer()`` does (not hardcoded here)."""
    return PoseHeader(
        version=0.1,
        dimensions=PoseHeaderDimensions(width=1, height=1, depth=1),
        components=[holistic_hand_component("RIGHT_HAND_LANDMARKS")],
    )


@lru_cache(maxsize=1)
def get_hand_normalizer() -> PoseNormalizer:
    header = _single_hand_header()
    plane = header.normalization_info(
        p1=("RIGHT_HAND_LANDMARKS", "WRIST"),
        p2=("RIGHT_HAND_LANDMARKS", "PINKY_MCP"),
        p3=("RIGHT_HAND_LANDMARKS", "INDEX_FINGER_MCP"),
    )
    line = header.normalization_info(
        p1=("RIGHT_HAND_LANDMARKS", "WRIST"),
        p2=("RIGHT_HAND_LANDMARKS", "MIDDLE_FINGER_MCP"),
    )
    return PoseNormalizer(plane=plane, line=line, size=NORMALIZATION_SIZE)


def landmarks_dict_to_array(landmarks: dict[str, NDArray[np.float64]]) -> NDArray[np.float64]:
    """``forward_kinematics.hand_to_landmarks()``'s dict -> a ``(21, 3)``
    array in ``HAND_POINTS`` order (the order every function in this module
    assumes)."""
    return np.stack([landmarks[name] for name in HAND_POINTS])


def normalize_landmarks(landmarks: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalizes a batch of hand landmark sets.

    ``landmarks``: shape ``(n, 21, 3)`` (or just ``(21, 3)`` for a single
    hand -- reshaped internally). Returns the same shape, in the canonical
    frame described in the module docstring.
    """
    single = landmarks.ndim == 2
    batch = landmarks[np.newaxis] if single else landmarks
    n = batch.shape[0]

    # PoseNormalizer expects (frames, people, joints, dims).
    as_frames: ma.MaskedArray[tuple[int, ...], np.dtype[np.float64]] = ma.masked_array(  # type: ignore[no-untyped-call]
        batch.reshape(n, 1, 21, 3)
    )
    normalized = get_hand_normalizer()(as_frames)
    result: NDArray[np.float64] = ma.getdata(normalized).reshape(n, 21, 3)  # type: ignore[no-untyped-call]
    result = _canonicalize_z_sign(result)
    return result[0] if single else result


def _canonicalize_z_sign(poses: NDArray[np.float64]) -> NDArray[np.float64]:
    """See module docstring's ``PoseNormalizer`` sign-ambiguity finding.
    ``poses``: shape ``(n, 21, 3)``. Flips z per-pose (not globally) so
    each pose independently satisfies "mean fingertip z >= 0"."""
    mean_tip_z = poses[:, _FINGERTIP_INDICES, 2].mean(axis=1)
    sign = np.where(mean_tip_z < 0, -1.0, 1.0)
    canonicalized = poses.copy()
    canonicalized[:, :, 2] *= sign[:, np.newaxis]
    return canonicalized


def hands_to_pose(hands: NDArray[np.float64]) -> Pose:
    """Wraps a raw landmark array into a real ``pose_format.Pose`` -- same
    shape ``hands.py`` builds internally (``hands_to_pose``), useful for
    saving/inspecting intermediate ground-truth data with standard
    tooling. ``hands``: shape ``(..., 21, 3)``."""
    header = _single_hand_header()
    data = hands.reshape((-1, 1, 21, 3)).astype(np.float32)
    confidence = np.ones(data.shape[:-1], dtype=np.float32)
    body = NumPyPoseBody(fps=1, data=data, confidence=confidence)
    return Pose(header, body)
