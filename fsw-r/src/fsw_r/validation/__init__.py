"""Evaluation layer: measures how well this framework's outputs match
reality, instead of only verifying it does what it was designed to do.

This is a MEASURING task, not a fixing one -- nothing here changes
``core/``, ``timeline/``, or ``export/`` (confirmed by ``git diff --stat``
on every commit, see PROGRESS.md's evaluation-layer entry). Two questions
this package exists to answer with real numbers instead of estimates:

1. How much does the joint-angle round trip (real landmarks -> angles ->
   forward kinematics -> landmarks again) actually lose? See
   ``scripts/eval_fk_accuracy.py``.
2. How much of Category 1's 261 hand poses violate real anatomical joint
   limits, and by how much? See ``anatomical_limits.py`` and
   ``scripts/eval_anatomical.py``.

``normalization.py`` is shared infrastructure both need: landmarks from two
different sources (real photos vs. this project's forward kinematics) are
only comparable after being put in the same reference frame -- see that
module's own docstring for why, and why it must be exactly the same
normalization ``sign-language-processing/synthetic-signwriting`` used to
build its own ground truth (else the comparison is apples to oranges before
a single error is even measured).
"""

from __future__ import annotations
