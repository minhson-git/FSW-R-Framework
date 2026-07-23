"""Maps (group, base_symbol_number) to the concrete FSWRenderableSymbol
subclass that implements it, so a real FSW symbol key can be turned directly
into the correctly-typed object -- e.g. ``symbol_from_fsw("S10011")``
returns a ``BaseSymbol01_01_001_Index`` instance, not a bag of raw ints.

This module stays group-agnostic, exactly like ``renderer.py``: it knows
nothing about Group 1 or "Index" specifically. Each ``groups/groupNN_*.py``
module registers its own base symbol classes via ``@register_symbol`` when
imported -- so the registry is only populated for base symbols whose module
has actually been imported somewhere (e.g. by ``demo.py`` or the test
suite).
"""

from __future__ import annotations

from typing import Callable, TypeVar

from fsw_r.core.fsw_symbol_key import parse_fsw_symbol_key
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


def symbol_from_fsw(key: str) -> FSWRenderableSymbol:
    """Parse a real FSW symbol key and instantiate the matching registered
    base symbol class with the key's fill/rotation.

    Raises ``ValueError`` if the key is malformed, outside ISWA Category 1
    (Hands), or names a (group, base_symbol_number) that has no registered
    class yet -- this prototype only implements a couple of Group 1 base
    symbols out of ISWA's ~650, so most real keys will hit this until more
    groups/base symbols are added.
    """
    parsed = parse_fsw_symbol_key(key)
    registry_key = (parsed.group, parsed.base_symbol_number)
    cls = _REGISTRY.get(registry_key)
    if cls is None:
        raise ValueError(
            f"no base symbol class registered for group={parsed.group}, "
            f"base_symbol_number={parsed.base_symbol_number} (from key {key!r})"
        )
    return cls(fill=parsed.fill, rotation=parsed.rotation)
