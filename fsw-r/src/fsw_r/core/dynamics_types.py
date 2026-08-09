"""Immutable data type for a Category 3 (Dynamics) symbol's meaning --
tempo/emphasis that modifies OTHER symbols in the same sign, not a pose of
its own. See ``core/modifier_symbol.py`` for why this category has no
``get_*() -> <pose type>`` render contract at all.

Verified on signbank.org (``iswa/2f7_sg.html``, the real ISWA 2010 HTML
reference -- see PROGRESS.md's Category 3 entry): all 8 base symbols and
their real names --

    0x2f7 Fast                    0x2fb Same Time
    0x2f8 Slow                    0x2fc Same Time Alternating
    0x2f9 Tense                   0x2fd Every Other Time
    0x2fa Relaxed                 0x2fe Gradual

Two structurally different groups, confirmed by each base's own valid
(fill, rotation) range (``iswa_valid_combinations.json``, the real ISWA font
cmap -- not this project's own reading): Fast/Tense/Relaxed vary by `fill`
(1-4) with rotation fixed; Slow/Same Time family/Gradual vary by `rotation`
(1-8) with fill fixed. What that intra-base variation actually MEANS (e.g.
"Fast" fill 1 vs. fill 4 -- four fine-grained speed levels? something else
entirely?) is NOT decoded here -- ``DynamicsModifier`` is keyed by
``base_hex`` only, same reasoning as ``BodyPose`` not varying by
fill/rotation. See PROGRESS.md's "giả định chưa kiểm chứng" list.

IMPORTANT -- like ``FaceExpressionPose``/``BodyPose``, every field value is
AUTHORED (a human reading of the real name), not measured. No dataset maps
ISWA Dynamics symbols to numeric timing coefficients.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DynamicsModifier:
    """A Category 3 symbol's authored effect on the sign's timing/manner.

    ``speed``: a duration multiplier, 1.0 = unmodified (matches
    ``timeline.build.DEFAULT_SIGN_DURATION``'s own convention: less than
    1.0 is faster/shorter, greater than 1.0 is slower/longer).
    ``repeat``: number of repetitions if this symbol specifies one,
    ``None`` if it doesn't (most bases don't -- only "Every Other Time"
    does, see ``scripts/gen_dynamics_modifiers.py``).
    ``tension``: ``True`` for "Tense", ``False`` otherwise -- including for
    "Relaxed", which is a real, distinct, explicitly-named symbol, not the
    absence of one (a sign with no Category 3 symbol at all has no
    ``DynamicsModifier`` object, so ``False`` here is unambiguous).
    ``alternating``: ``True`` for "Same Time Alternating" and "Every Other
    Time" (both explicitly name alternation between two hands/repeats).
    """

    speed: float
    repeat: int | None
    tension: bool
    alternating: bool
