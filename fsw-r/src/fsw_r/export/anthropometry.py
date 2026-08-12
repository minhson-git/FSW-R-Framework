"""The two base scale constants the hand geometry (``bone_lengths.py``) and
the body geometry (``body_geometry.py``) both anchor to, kept in one place so
BOTH can derive from a single assumed stature without importing each other.

Before this module, ``ASSUMED_STATURE_MM`` lived in ``body_geometry.py`` and
``HAND_MM_TO_BODY_UNITS`` in ``bone_lengths.py``, and ``body_geometry`` had to
import from ``bone_lengths``. Anchoring the HAND to the same stature (this
task) would have meant ``bone_lengths`` importing ``body_geometry`` back --
an import cycle. Extracting both constants here breaks that: ``bone_lengths``
and ``body_geometry`` each import from this leaf module, neither from the
other. See the task brief, Part A1.
"""

from __future__ import annotations

# Commonly-cited round approximate adult stature -- NOT a specific population
# statistic, just the single height every derived body AND hand dimension is
# scaled from (Drillis-Contini's body fractions in ``body_geometry.py``, and
# the hand-length fraction in ``bone_lengths.py``). Flagged as an assumption.
ASSUMED_STATURE_MM = 1700.0

# UNVERIFIED: real-world millimetres -> fsw_r.timeline body-space units.
# ``timeline/`` body-space has no established real-world calibration
# (``timeline/anchor.py``'s own ``SIGNBOX_TO_BODY_SCALE`` is itself flagged
# unverified), so there is nothing to calibrate "real mm" against. Chosen so
# a real hand's length lands in the same order of magnitude as a typical
# movement trajectory's displacement, not calibrated. Applied identically to
# the hand and the body, so the two share one consistent scale. See
# PROGRESS.md's "giả định chưa kiểm chứng" list.
HAND_MM_TO_BODY_UNITS = 0.01
