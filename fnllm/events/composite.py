# Copyright (c) 2024 Microsoft Corporation.

"""Class for LLM composite event handling."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from fnllm.events.base import LLMEvents

if TYPE_CHECKING:
    from collections.abc import Sequence

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
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_execute_llm() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_execute_llm() invoke `handler.on_execute_llm() for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_execute_llm() {self._handlers=}")
        await asyncio.gather(*[handler.on_execute_llm() for handler in self._handlers])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_execute_llm() invoke `handler.on_execute_llm() for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_execute_llm() end...")
        print()

    async def on_error(
            self,
            error: BaseException | None,
            traceback: str | None = None,
            arguments: dict[str, Any] | None = None,
    ) -> None:
        """An unhandled error that happens during the LLM call (called by the LLM base)."""
        print("fnllm/events/composite.py LLMCompositeEvents.on_error() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_error() invoke `handler.on_error(error, traceback, arguments) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_error() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_error() {error=}")
        await asyncio.gather(*[
            handler.on_error(error, traceback, arguments) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_error() invoke `handler.on_error(error, traceback, arguments) for handler in self._handlers` end...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_error() end...")
        print()

    async def on_usage(self, usage: LLMUsageMetrics) -> None:
        """Called when there is any LLM usage."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_usage() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_usage() invoke `handler.on_usage(usage) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_usage() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_usage() {usage=}")
        await asyncio.gather(*[handler.on_usage(usage) for handler in self._handlers])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_usage() invoke `handler.on_usage(usage) for handler in self._handlers` end...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_usage() end...")
        print()

    async def on_limit_acquired(self, manifest: Manifest) -> None:
        """Called when limit is acquired for a request (does not include post limiting)."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_limit_acquired() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_limit_acquired() invoke `handler.on_limit_acquired(manifest) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_limit_acquired() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_limit_acquired() {manifest=}")
        await asyncio.gather(*[
            handler.on_limit_acquired(manifest) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_limit_acquired() invoke `handler.on_limit_acquired(manifest) for handler in self._handlers` end...")

        print("fnllm/events/composite.py LLMCompositeEvents.on_limit_acquired() end...")
        print()

    async def on_limit_released(self, manifest: Manifest) -> None:
        """Called when limit is released for a request (does not include post limiting)."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_limit_released() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_limit_released() invoke `handler.on_limit_released(manifest) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_limit_released() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_limit_released() {manifest}")
        await asyncio.gather(*[
            handler.on_limit_released(manifest) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_limit_released() invoke `handler.on_limit_released(manifest) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_limit_released() end...")
        print()

    async def on_post_limit(self, manifest: Manifest) -> None:
        """Called when post request limiting is triggered (called by the rate limiting LLM)."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_post_limit() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_post_limit() invoke `handler.on_post_limit(manifest) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_post_limit() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_post_limit() {manifest=}")

        await asyncio.gather(*[
            handler.on_post_limit(manifest) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_post_limit() invoke `handler.on_post_limit(manifest) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_post_limit() end...")
        print()

    async def on_success(
            self,
            metrics: LLMMetrics,
    ) -> None:
        """Called when a request goes through (called by the retrying LLM)."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_success() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_success() invoke `handler.on_success(metrics) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_success() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_success() {metrics=}")
        await asyncio.gather(*[
            handler.on_success(metrics) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_success() invoke `handler.on_success(metrics) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_success() end...")
        print()

    async def on_cache_hit(self, cache_key: str, name: str | None) -> None:
        """Called when there is a cache hit."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() invoke `handler.on_cache_hit(cache_key, name) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() {cache_key=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() {name=}")
        await asyncio.gather(*[
            handler.on_cache_hit(cache_key, name) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() invoke `handler.on_cache_hit(cache_key, name) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_cache_hit() end...")
        print()

    async def on_cache_miss(self, cache_key: str, name: str | None) -> None:
        """Called when there is a cache miss."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_cache_miss() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_cache_miss() invoke `handler.on_cache_miss(cache_key, name) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_cache_miss() {self._handlers=}")
        await asyncio.gather(*[
            handler.on_cache_miss(cache_key, name) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_cache_miss() invoke `handler.on_cache_miss(cache_key, name) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_cache_miss() end...")
        print()

    async def on_try(self, attempt_number: int) -> None:
        """Called every time a new try to call the LLM happens."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_try() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_try() invoke `handler.on_try(attempt_number) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_try() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_try() {attempt_number=}")
        await asyncio.gather(*[
            handler.on_try(attempt_number) for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_try() invoke `handler.on_try(attempt_number) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_try() end...")
        print()

    async def on_retryable_error(
            self, error: BaseException, attempt_number: int
    ) -> None:
        """Called when retryable errors happen."""
        print()
        print("fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() start...")
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() invoke `handler.on_retryable_error(error, attempt_number) for handler in self._handlers` start...")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() {self._handlers=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() {error=}")
        print(f"fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() {attempt_number=}")
        await asyncio.gather(*[
            handler.on_retryable_error(error, attempt_number)
            for handler in self._handlers
        ])
        print(
            f"fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() invoke `handler.on_retryable_error(error, attempt_number) for handler in self._handlers` end...")
        print("fnllm/events/composite.py LLMCompositeEvents.on_retryable_error() end...")
        print()
