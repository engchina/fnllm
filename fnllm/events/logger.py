# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Class for LLM event logging."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fnllm.events.base import LLMEvents

if TYPE_CHECKING:
    from logging import Logger

    from fnllm.limiting.base import Manifest
    from fnllm.types.metrics import LLMMetrics, LLMUsageMetrics


class LLMEventsLogger(LLMEvents):
    """Implementation of the LLM events that just logs the events."""

    def __init__(self, logger: Logger) -> None:
        """Create a new LLMEventsLogger."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.__init__() start...")
        self._logger = logger
        print("fnllm/events/logger.py LLMEventsLogger.__init__() end...")
        print()

    async def on_error(
            self,
            error: BaseException | None,
            traceback: str | None = None,
            arguments: dict[str, Any] | None = None,
    ) -> None:
        """An unhandled error that happens during the LLM call (called by the LLM base)."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_error() start...")
        self._logger.error(
            "unexpected error occurred for arguments '%s':\n\n%s\n\n%s",
            arguments,
            error,
            traceback,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_error() end...")
        print()

    async def on_usage(self, usage: LLMUsageMetrics) -> None:
        """Called when there is any LLM usage."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_usage() start...")
        self._logger.info(
            "LLM usage with %d total tokens (input=%d, output=%d)",
            usage.total_tokens,
            usage.input_tokens,
            usage.output_tokens,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_usage() end...")
        print()

    async def on_limit_acquired(self, manifest: Manifest) -> None:
        """Called when limit is acquired for a request (does not include post limiting)."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_limit_acquired() start...")
        self._logger.info(
            "limit acquired for request, request_tokens=%d, post_request_tokens=%d",
            manifest.request_tokens,
            manifest.post_request_tokens,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_limit_acquired() end...")
        print()

    async def on_limit_released(self, manifest: Manifest) -> None:
        """Called when limit is released for a request (does not include post limiting)."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_limit_released() start...")
        self._logger.info(
            "limit released for request, request_tokens=%d, post_request_tokens=%d",
            manifest.request_tokens,
            manifest.post_request_tokens,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_limit_released() end...")
        print()

    async def on_post_limit(self, manifest: Manifest) -> None:
        """Called when post request limiting is triggered (called by the rate limiting LLM)."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_post_limit() start...")
        self._logger.info(
            "post request limiting triggered, acquired extra %d tokens",
            manifest.post_request_tokens,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_post_limit() end...")
        print()

    async def on_success(
            self,
            metrics: LLMMetrics,
    ) -> None:
        """Called when a request goes through (called by the retrying LLM)."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_success() start...")
        self._logger.info(
            "request succeed with %d retries in %.2fs and used %d tokens",
            metrics.retry.num_retries,
            metrics.retry.total_time,
            metrics.usage.total_tokens,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_success() end...")
        print()

    async def on_cache_hit(self, cache_key: str, name: str | None) -> None:
        """Called when there is a cache hit."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_cache_hit() start...")
        self._logger.info(
            "cache hit for key=%s and name=%s",
            cache_key,
            name,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_cache_hit() end...")
        print()

    async def on_cache_miss(self, cache_key: str, name: str | None) -> None:
        """Called when there is a cache miss."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_cache_miss() start...")
        self._logger.info(
            "cache miss for key=%s and name=%s",
            cache_key,
            name,
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_cache_miss() end...")
        print()

    async def on_try(self, attempt_number: int) -> None:
        """Called every time a new try to call the LLM happens."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_try() start...")
        self._logger.debug("calling llm, attempt #%d", attempt_number)
        print("fnllm/events/logger.py LLMEventsLogger.on_try() end...")
        print()

    async def on_retryable_error(
            self, error: BaseException, attempt_number: int
    ) -> None:
        """Called when retryable errors happen."""
        print()
        print("fnllm/events/logger.py LLMEventsLogger.on_retryable_error() start...")
        self._logger.warning(
            "retryable error happened on attempt #%d: %s", attempt_number, str(error)
        )
        print("fnllm/events/logger.py LLMEventsLogger.on_retryable_error() end...")
        print()
