# Copyright (c) 2024 Microsoft Corporation.

"""Class for LLM composite event handling."""

import asyncio
from collections.abc import Sequence
from typing import Any

from fnllm.events.base import LLMEvents
from fnllm.limiting.base import Manifest
from fnllm.types.metrics import LLMMetrics, LLMUsageMetrics


class LLMCompositeEvents(LLMEvents):
    """Provide support for different events at the same time."""

    def __init__(self, handlers: Sequence[LLMEvents]) -> None:
        """Create a new LLMCompositeEvents."""
        self._handlers = handlers

    async def on_execute_llm(
            self,
    ) -> None:
        """Hook called before the actual LLM call."""
        print("composite.py on_execute_llm() start...")
        print(f"{self._handlers=}")
        await asyncio.gather(*[handler.on_execute_llm() for handler in self._handlers])

    async def on_error(
            self,
            error: BaseException | None,
            traceback: str | None = None,
            arguments: dict[str, Any] | None = None,
    ) -> None:
        """An unhandled error that happens during the LLM call (called by the LLM base)."""
        print("composite.py on_error() start...")
        await asyncio.gather(*[
            handler.on_error(error, traceback, arguments) for handler in self._handlers
        ])

    async def on_usage(self, usage: LLMUsageMetrics) -> None:
        """Called when there is any LLM usage."""
        print("composite.py on_usage() start...")
        await asyncio.gather(*[handler.on_usage(usage) for handler in self._handlers])

    async def on_limit_acquired(self, manifest: Manifest) -> None:
        """Called when limit is acquired for a request (does not include post limiting)."""
        print("composite.py on_limit_acquired() start...")
        print(f"{self._handlers=}")
        await asyncio.gather(*[
            handler.on_limit_acquired(manifest) for handler in self._handlers
        ])

    async def on_limit_released(self, manifest: Manifest) -> None:
        """Called when limit is released for a request (does not include post limiting)."""
        print("composite.py on_limit_released() start...")
        await asyncio.gather(*[
            handler.on_limit_released(manifest) for handler in self._handlers
        ])

    async def on_post_limit(self, manifest: Manifest) -> None:
        """Called when post request limiting is triggered (called by the rate limiting LLM)."""
        print("composite.py on_post_limit() start...")
        await asyncio.gather(*[
            handler.on_post_limit(manifest) for handler in self._handlers
        ])

    async def on_success(
            self,
            metrics: LLMMetrics,
    ) -> None:
        """Called when a request goes through (called by the retrying LLM)."""
        print("composite.py on_success() start...")
        await asyncio.gather(*[
            handler.on_success(metrics) for handler in self._handlers
        ])

    async def on_cache_hit(self, cache_key: str, name: str | None) -> None:
        """Called when there is a cache hit."""
        print("composite.py on_cache_hit() start...")
        await asyncio.gather(*[
            handler.on_cache_hit(cache_key, name) for handler in self._handlers
        ])

    async def on_cache_miss(self, cache_key: str, name: str | None) -> None:
        """Called when there is a cache miss."""
        print("composite.py on_cache_miss() start...")
        await asyncio.gather(*[
            handler.on_cache_miss(cache_key, name) for handler in self._handlers
        ])

    async def on_try(self, attempt_number: int) -> None:
        """Called every time a new try to call the LLM happens."""
        print("composite.py on_try() start...")
        await asyncio.gather(*[
            handler.on_try(attempt_number) for handler in self._handlers
        ])

    async def on_retryable_error(
            self, error: BaseException, attempt_number: int
    ) -> None:
        """Called when retryable errors happen."""
        print("composite.py on_retryable_error() start...")
        await asyncio.gather(*[
            handler.on_retryable_error(error, attempt_number)
            for handler in self._handlers
        ])
