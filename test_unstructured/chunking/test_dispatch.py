# pyright: reportPrivateUsage=false

"""Unit-test suite for the `unstructured.chunking.dispatch` module."""

from __future__ import annotations

from typing import Iterable, Optional

import pytest

from unstructured.chunking.dispatch import ChunkerSpec, chunk, register_chunking_strategy
from unstructured.documents.elements import CompositeElement, Element


class Describe_chunk:
    """Unit-test suite for `unstructured.chunking.dispatch.chunk()` function."""

    def it_dispatches_to_the_chunker_registered_for_the_chunking_strategy(self):

        def chunk_by_something_else(
            elements: Iterable[Element], max_characters: Optional[int] = None
        ) -> list[Element]:
            es = list(elements)
            return [CompositeElement(f"chunked {len(es)} elements with hard-max {max_characters}")]

        register_chunking_strategy("chunk_by_something_else", ChunkerSpec(chunk_by_something_else))
        kwargs = {
            "max_characters": 750,
            # -- unused kwargs shouldn't cause a problem; in general `kwargs` will contain all
            # -- keyword arguments used in the partitioning call.
            "foo": "bar",
        }

        chunks = chunk([], "chunk_by_something_else", **kwargs)

        assert chunks == [CompositeElement("chunked 0 elements with hard-max 750")]

    def it_raises_when_the_requested_chunking_strategy_is_not_registered(self):
        with pytest.raises(
            ValueError,
            match="unrecognized chunking strategy 'foobar'",
        ):
            chunk(elements=[], chunking_strategy="foobar")
