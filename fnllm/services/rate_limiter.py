# Copyright (c) 2024 Microsoft Corporation.

"""Rate limiting LLM implementation."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import Unpack

from fnllm.events.base import LLMEvents
from fnllm.limiting import Limiter, Manifest
from fnllm.types.generics import TInput, TJsonModel, TModelParameters
from .decorator import LLMDecorator, THistoryEntry, TOutput

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fnllm.types.io import LLMInput, LLMOutput


class RateLimiter(
    LLMDecorator[TOutput, THistoryEntry],
    Generic[TInput, TOutput, THistoryEntry, TModelParameters],
):
    """A base class to rate limit the LLM."""

    def __init__(
            self,
            limiter: Limiter,
            *,
            events: LLMEvents | None = None,
    ):
        """Create a new BaseRateLimitLLM."""
        print()
        print("fnllm/services/rate_limiter.py RateLimiter.__init__() start...")
        self._limiter = limiter
        self._events = events or LLMEvents()
        print("fnllm/services/rate_limiter.py RateLimiter.__init__() end...")
        print()

    @abstractmethod
    def _estimate_request_tokens(
            self,
            prompt: TInput,
            kwargs: LLMInput[TJsonModel, THistoryEntry, TModelParameters],
    ) -> int:
        """Estimate how many tokens are on the request input."""

    async def _handle_post_request_limiting(
            self,
            result: LLMOutput[TOutput, TJsonModel, THistoryEntry],
    ) -> None:
        print("fnllm/services/rate_limiter.py RateLimiter._handle_post_request_limiting() start...")
        print(f"RateLimiter._handle_post_request_limiting() {result=}")
        diff = result.metrics.tokens_diff
        print(f"RateLimiter._handle_post_request_limiting() {diff=}")

        if diff > 0:
            manifest = Manifest(post_request_tokens=diff)
            # consume the token difference
            async with self._limiter.use(manifest):
                await self._events.on_post_limit(manifest)

    def decorate(
            self,
            delegate: Callable[
                ..., Awaitable[LLMOutput[TOutput, TJsonModel, THistoryEntry]]
            ],
    ) -> Callable[..., Awaitable[LLMOutput[TOutput, TJsonModel, THistoryEntry]]]:
        """Execute the LLM with the configured rate limits."""
        print("fnllm/services/rate_limiter.py RateLimiter.decorate() start...")

        async def invoke(prompt: TInput, **args: Unpack[LLMInput[Any, Any, Any]]):
            print("fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() start...")
            print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() {prompt=}")
            print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() {args=}")
            estimated_input_tokens = self._estimate_request_tokens(prompt, args)
            print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() {estimated_input_tokens=}")

            manifest = Manifest(request_tokens=estimated_input_tokens)
            print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() {manifest=}")
            try:
                print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() {self._limiter=}")
                print(
                    f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() run `async with self._limiter.use(manifest)` start...")
                async with self._limiter.use(manifest):
                    print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() {self._events=}")
                    print(
                        f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke self._events.on_limit_acquired() start...")
                    await self._events.on_limit_acquired(manifest)
                    print(
                        f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke self._events.on_limit_acquired() end...")
                    print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke delegate() start...")
                    result = await delegate(prompt, **args)
                    print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke delegate() end...")
                print(
                    f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() run `async with self._limiter.use(manifest)` end...")
            finally:
                print(
                    f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke self._events.on_limit_released() start...")
                await self._events.on_limit_released(manifest)
                print(
                    f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke self._events.on_limit_released() end...")

            result.metrics.estimated_input_tokens = estimated_input_tokens
            print(
                f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke self._handle_post_request_limiting() start...")
            await self._handle_post_request_limiting(result)
            print(
                f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() invoke self._handle_post_request_limiting() start...")

            print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() return {result=}...")
            return result

        print(f"fnllm/services/rate_limiter.py RateLimiter.decorate().invoke() return {invoke=}...")
        return invoke
