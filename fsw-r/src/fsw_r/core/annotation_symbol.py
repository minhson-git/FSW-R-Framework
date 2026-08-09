"""A symbol that is present in a sign but this framework represents as a
labelled marker, not a modelled pose -- the honest home for ISWA symbols
that are not (yet) a hand pose, a motion path, or a facial-expression
blend-shape.

Used for the parts of Category 4 (Head & Face) that aren't ARKit-52 facial
deformations: teeth / ears / hair / neck / airflow / breath / annotation
marks (genuinely not facial deformations), the facial *movements* (blinks,
flutter, jaw/tongue/teeth movements -- these need an expression-over-time
model that doesn't exist yet), the head symbols (a head glyph's fill/rotation
-> 3D orientation could not be confirmed from the glyph the way eyegaze's
gaze direction could, so it is NOT guessed), and the "dreamy"/angled brows
(a continuous angled brow line whose left/right ARKit mapping the glyph does
not disambiguate).

This is deliberately the least-capable renderable: it carries the symbol's
identity (``symbol_id``/``base_hex``/``fill``/``rotation``) and nothing
else. When a real model for one of these families is verified later (the way
eyegaze went from deferred to a real ``FaceSymbol`` once its glyph
convention was confirmed), that family graduates out of here into its own
symbol class -- see ``registry.py``'s Category 4 dispatch.
"""

from __future__ import annotations

from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.core.types import HandSide


class AnnotationSymbol(FSWRenderableSymbol):
    def __init__(self, base_hex: int, fill: int, rotation: int) -> None:
        super().__init__(base_hex=base_hex, fill=fill, rotation=rotation)

    @property
    def hand_side(self) -> HandSide | None:
        """A marker symbol encodes no performing hand."""
        return None
