"""Handles dispatch of elements to a chunking-strategy by name.

Used by the `@add_chunking_strategy` decorator but can also be used where a level of indirection
from actual chunking functions is desired.
"""

from __future__ import annotations

import dataclasses as dc
import inspect
from typing import Any, Iterable, Optional, Protocol

from unstructured.chunking.basic import chunk_elements
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Element
from unstructured.utils import lazyproperty


class Chunker(Protocol):
    """Abstract interface for chunking functions."""

    def __call__(
        self, elements: Iterable[Element], *, max_characters: Optional[int]
    ) -> list[Element]:
        """A chunking function must have this signature.

        In particular it must minimally have an `elements` parameter and all chunkers will have a
        `max_characters` parameter (doesn't need to follow `elements` directly). All others can
        vary by chunker.
        """
        ...


@dc.dataclass(frozen=True)
class ChunkerSpec:
    """A registry entry for a chunker."""

    # NOTE(scanny): This doesn't need to be a published object yet (we could wrap `chunker` in this
    # object inside `register_chunking_strategy()`), but this option provides us headroom to add
    # additional attributes later without a breaking change.

    chunker: Chunker
    """The "chunk_by_{x}() function that implements this chunking strategy."""

    @lazyproperty
    def kw_arg_names(self) -> tuple[str, ...]:
        """Keyword arguments supported by this chunker.

        These are all arguments other than the required `elements: list[Element]` first parameter.
        """
        sig = inspect.signature(self.chunker)
        return tuple(key for key in sig.parameters if key != "elements")


_chunker_registry: dict[str, ChunkerSpec] = {
    "basic": ChunkerSpec(chunk_elements),
    "by_title": ChunkerSpec(chunk_by_title),
}


def register_chunking_strategy(name: str, chunker_spec: ChunkerSpec) -> None:
    """Make chunker available by using `name` as `chunking_strategy` arg in partitioner call."""
    _chunker_registry[name] = chunker_spec


def chunk(elements: Iterable[Element], chunking_strategy: str, **kwargs: Any) -> list[Element]:
    """Dispatch chunking of `elements` to the chunking function for `chunking_strategy`."""
    chunker_spec = _chunker_registry.get(chunking_strategy)

    if chunker_spec is None:
        raise ValueError(f"unrecognized chunking strategy {repr(chunking_strategy)}")

    # -- `kwargs` will in general be an omnibus dict of all keyword arguments, pick out and use
    # -- only those supported by this chunker.
    chunking_kwargs = {k: v for k, v in kwargs.items() if k in chunker_spec.kw_arg_names}

    return chunker_spec.chunker(elements, **chunking_kwargs)
