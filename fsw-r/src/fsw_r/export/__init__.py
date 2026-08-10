"""Export layer: turns ``timeline/``'s output (``tuple[PoseFrame, ...]``)
into a real, standard, tool-interoperable pose format
(``pose_format.Pose``, the ``.pose`` file format from the
``sign-language-processing`` community's `pose-format` library) instead of
this project inventing its own.

Consumes ``core/`` and ``timeline/``'s public output; modifies neither --
see this package's own task brief, Part 0, for why (a new video-generation
layer shouldn't be able to introduce doubt about whether a bug is in the
already-validated symbol/timeline layers or in this one).

Scope, this task ("bước 1-2" of the export brief): forward kinematics
(``forward_kinematics.py``) from a hand's 15 joint angles to the 21
MediaPipe Holistic hand landmarks, and packaging a full ``SignTimeline``
sample sequence into a ``.pose`` file (``pose_export.py``). Two-bone arm IK
and a static torso (step 3) and wiring Category 3 (Dynamics) timing into
frame duration (step 4) are explicitly OUT of scope here -- see
PROGRESS.md's export-layer entry and ROADMAP.md.
"""

from __future__ import annotations
