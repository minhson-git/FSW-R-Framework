"""Maps (group, base_symbol_number) to the concrete FSWRenderableSymbol
subclass that implements it, so a real, already-decoded FSW symbol can be
turned directly into the correctly-typed object -- e.g. a decoded "Index,
fill=1, rotation=1" becomes a ``BaseSymbol01_01_001_Index`` instance, not a
bag of raw ints.

This module stays group-agnostic, exactly like ``renderer.py``: it knows
nothing about Group 1 or "Index" specifically. Each ``groups/groupNN_*.py``
module registers its own base symbol classes via ``@register_symbol`` when
imported -- so the registry is only populated for base symbols whose module
has actually been imported somewhere (e.g. by ``demo.py`` or the test
suite).

This is the "converter" half of the FSW -> AST -> FSWR pipeline (see
``fsw_ast.py`` for the AST half, ``fswr_converter.py`` for the version that
converts a whole parsed sign at once). ``symbol_from_fsw`` is kept here as a
convenience for the common single-key case.
"""

from __future__ import annotations

from typing import Callable, TypeVar

from fsw_r.core.fsw_symbol_key import ParsedFSWSymbol, parse_fsw_symbol_key
from fsw_r.core.renderable_symbol import FSWRenderableSymbol

# A registered class's constructor -- every concrete base symbol takes just
# (fill, rotation); group/base_symbol_number are baked into the subclass.
_Constructor = Callable[..., FSWRenderableSymbol]
_ClassT = TypeVar("_ClassT", bound=_Constructor)

_REGISTRY: dict[tuple[int, int], _Constructor] = {}


def register_symbol(group: int, base_symbol_number: int) -> Callable[[_ClassT], _ClassT]:
    def decorator(cls: _ClassT) -> _ClassT:
        key = (group, base_symbol_number)
        if key in _REGISTRY:
            raise ValueError(f"base symbol {key} is already registered to {_REGISTRY[key]}")
        _REGISTRY[key] = cls
        return cls

    return decorator


def build_symbol(parsed: ParsedFSWSymbol) -> FSWRenderableSymbol:
    """Look up the registered class for an already-decoded FSW symbol and
    instantiate it with the decoded fill/rotation.

    Raises ``ValueError`` if no class is registered for that
    (group, base_symbol_number) -- this prototype only implements a couple
    of Group 1 base symbols out of ISWA's ~650, so most real symbols will
    hit this until more groups/base symbols are added.
    """
    registry_key = (parsed.group, parsed.base_symbol_number)
    cls = _REGISTRY.get(registry_key)
    if cls is None:
        raise ValueError(
            f"no base symbol class registered for group={parsed.group}, "
            f"base_symbol_number={parsed.base_symbol_number}"
        )
    return cls(fill=parsed.fill, rotation=parsed.rotation)


def symbol_from_fsw(key: str) -> FSWRenderableSymbol:
    """Decode a single, bare real FSW symbol key (e.g. ``"S10011"``) and
    instantiate the matching registered base symbol class.

    Convenience wrapper around ``parse_fsw_symbol_key`` + ``build_symbol``
    for the common case of a single symbol, not a full multi-symbol sign --
    for that, see ``fswr_converter.fsw_to_fswr``.
    """
    return build_symbol(parse_fsw_symbol_key(key))
