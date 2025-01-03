# Copyright (c) 2024 Microsoft Corporation.

"""Rate limiting LLM implementation."""

from __future__ import annotations

import asyncio
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from typing_extensions import Unpack

from fnllm.events.base import LLMEvents
from fnllm.services.errors import RetriesExhaustedError
from fnllm.types.generics import (
    THistoryEntry,
    TInput,
    TJsonModel,
    TModelParameters,
    TOutput,
)
from fnllm.types.metrics import LLMRetryMetrics
from .decorator import LLMDecorator

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from fnllm.types.io import LLMInput, LLMOutput


class Retryer(
    LLMDecorator[TOutput, THistoryEntry],
    Generic[TInput, TOutput, THistoryEntry, TModelParameters],
):
    """A base class to add retries to an llm."""

    def __init__(
            self,
            *,
            retryable_errors: Sequence[type[Exception]],
            tag: str = "RetryingLLM",
            max_retries: int = 10,
            max_retry_wait: float = 10,
            events: LLMEvents | None = None,
    ):
        """Create a new RetryingLLM."""
        print()
        print("fnllm/services/retryer.py Retryer.__init__() start...")
        self._retryable_errors = retryable_errors
        self._tag = tag
        self._max_retries = max_retries
        self._max_retry_wait = max_retry_wait
        self._events = events or LLMEvents()
        print("fnllm/services/retryer.py Retryer.__init__() end...")
        print()

    @abstractmethod
    async def _on_retryable_error(self, error: BaseException) -> None:
        """Called as soon as retryable error happen."""

    def decorate(
            self,
            delegate: Callable[
                ..., Awaitable[LLMOutput[TOutput, TJsonModel, THistoryEntry]]
            ],
    ) -> Callable[..., Awaitable[LLMOutput[TOutput, TJsonModel, THistoryEntry]]]:
        """Execute the LLM with the configured rate limits."""

        async def invoke(prompt: TInput, **kwargs: Unpack[LLMInput[Any, Any, Any]]):
            print()
            print("fnllm/services/retryer.py Retryer.decorate().invoke() start...")
            name = kwargs.get("name", self._tag)
            attempt_number = 0
            call_times: list[float] = []

            async def attempt() -> LLMOutput[TOutput, TJsonModel, THistoryEntry]:
                print("fnllm/services/retryer.py Retryer.decorate().invoke().attempt() start...")
                nonlocal call_times
                call_start = asyncio.get_event_loop().time()

                try:
                    print(
                        "fnllm/services/retryer.py Retryer.decorate().invoke().attempt() invoke self._events.on_try() start...")
                    await self._events.on_try(attempt_number)
                    print("fnllm/services/retryer.py Retryer.decorate().invoke().attempt() return delegate()...")
                    print()
                    return await delegate(prompt, **kwargs)
                except BaseException as error:
                    if isinstance(error, tuple(self._retryable_errors)):
                        await self._events.on_retryable_error(error, attempt_number)
                        await self._on_retryable_error(error)
                    raise
                finally:
                    call_end = asyncio.get_event_loop().time()
                    call_times.append(call_end - call_start)

            async def execute_with_retry() -> LLMOutput[
                TOutput, TJsonModel, THistoryEntry
            ]:
                print("fnllm/services/retryer.py Retryer.decorate().invoke().execute_with_retry() start...")
                nonlocal attempt_number
                try:
                    print(
                        "fnllm/services/retryer.py Retryer.decorate().invoke().execute_with_retry() return attempt()...")
                    print()

                    async for a in AsyncRetrying(
                            stop=stop_after_attempt(self._max_retries),
                            wait=wait_exponential_jitter(max=self._max_retry_wait),
                            reraise=True,
                            retry=retry_if_exception_type(tuple(self._retryable_errors)),
                    ):
                        with a:
                            attempt_number += 1
                            return await attempt()
                except BaseException as error:
                    if not isinstance(error, tuple(self._retryable_errors)):
                        raise

                raise RetriesExhaustedError(name, self._max_retries)

            start = asyncio.get_event_loop().time()
            print("fnllm/services/retryer.py Retryer.decorate().invoke() invoke execute_with_retry() start...")
            result = await execute_with_retry()
            print("fnllm/services/retryer.py Retryer.decorate().invoke() invoke execute_with_retry() end...")
            end = asyncio.get_event_loop().time()

            print("fnllm/services/retryer.py Retryer.decorate().invoke() invoke LLMRetryMetrics() start...")
            result.metrics.retry = LLMRetryMetrics(
                num_retries=attempt_number - 1,
                total_time=end - start,
                call_times=call_times,
            )
            print(f"fnllm/services/retryer.py Retryer.decorate().invoke() {result.metrics.retry=}")
            print(f"fnllm/services/retryer.py Retryer.decorate().invoke() invoke LLMRetryMetrics() end...")

            print(f"fnllm/services/retryer.py Retryer.decorate().invoke() invoke self._events.on_success() start...")
            await self._events.on_success(result.metrics)
            print(f"fnllm/services/retryer.py Retryer.decorate().invoke() invoke self._events.on_success() end...")

            print(f"fnllm/services/retryer.py Retryer.decorate().invoke() {result=}...")
            print("fnllm/services/retryer.py Retryer.decorate().invoke() return result...")
            return result

        print(f"fnllm/services/retryer.py Retryer.decorate().invoke() {invoke=}...")
        print("fnllm/services/retryer.py Retryer.decorate().invoke() return invoke...")
        return invoke
