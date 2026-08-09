"""SignTimeline -- the time axis FSW itself doesn't have.

FSW describes a sign as a 2D spatial layout (a list of symbols + (x, y)
page positions) -- ``core/fswr_converter.py`` already turns that into
``tuple[PositionedSymbol, ...]``. A renderer needs a *sequence of poses
over time* instead. This package is the translation layer between the two:

    tuple[PositionedSymbol, ...]  --[build_timeline]-->  SignTimeline  --[sample]-->  pose sequence at N fps
       (core/fswr_converter.py)      (this package)                       (this package)

This package only CONSUMES ``core/``'s output -- it does not modify any
file in ``core/``. See ``build.py``'s module docstring for MVP-1's exact
scope (which signs this can build a timeline for) and why that scope was
chosen.
"""
