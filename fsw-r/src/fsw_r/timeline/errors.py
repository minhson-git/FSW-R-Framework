"""Errors raised by the ``timeline`` package."""

from __future__ import annotations


class UnsupportedSignError(ValueError):
    """A sign falls outside MVP-1's supported scope -- see ``build.py``'s
    module docstring for exactly what that scope is and why. Raised
    instead of guessing and returning a wrong timeline."""
