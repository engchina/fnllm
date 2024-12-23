# Copyright (c) 2024 Microsoft Corporation.

"""Rate limiting LLM implementation for OpenAI."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Final, Generic

from openai import APIConnectionError, InternalServerError, RateLimitError

from fnllm.services.retryer import Retryer
from fnllm.types.generics import THistoryEntry, TInput, TModelParameters, TOutput

if TYPE_CHECKING:
    from fnllm.events.base import LLMEvents

OPENAI_RETRYABLE_ERRORS: Final[list[type[Exception]]] = [
    RateLimitError,
    APIConnectionError,
    InternalServerError,
]


class OpenAIRetryer(
    Retryer[TInput, TOutput, THistoryEntry, TModelParameters],
    Generic[TInput, TOutput, THistoryEntry, TModelParameters],
):
    """A base class to rate limit the LLM."""

    def __init__(
            self,
            *,
            tag: str = "OpenAIRetryingLLM",
            max_retries: int = 10,
            max_retry_wait: float = 10,
            sleep_on_rate_limit_recommendation: bool = False,
            events: LLMEvents | None = None,
    ):
        """Create a new BaseRateLimitLLM."""
        print()
        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer.__init__() start...")
        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer.__init__() invoke super().__init__() start...")
        super().__init__(
            retryable_errors=OPENAI_RETRYABLE_ERRORS,
            tag=tag,
            max_retries=max_retries,
            max_retry_wait=max_retry_wait,
            events=events,
        )
        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer.__init__() invoke super().__init__() end...")

        self._sleep_on_rate_limit_recommendation = sleep_on_rate_limit_recommendation
        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer.__init__() end...")
        print()

    async def _on_retryable_error(self, error: BaseException) -> None:
        print()
        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer._on_retryable_error() start...")
        print(
            f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._on_retryable_error() invoke self._extract_sleep_recommendation({error=}) start...")
        sleep_recommendation = self._extract_sleep_recommendation(error)
        print(
            f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._on_retryable_error() invoke self._extract_sleep_recommendation({error=}) end...")
        if sleep_recommendation > 0:
            print(
                f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._on_retryable_error() invoke asyncio.sleep({sleep_recommendation=}) end...")
            await asyncio.sleep(sleep_recommendation)
            print(
                f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._on_retryable_error() invoke asyncio.sleep({sleep_recommendation=}) end...")

        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer._on_retryable_error() end...")

    def _extract_sleep_recommendation(self, error: BaseException) -> float:
        """Extract the sleep time value from a RateLimitError. This is usually only available in Azure."""
        print("fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() start...")
        please_retry_after_msg: Final = "Rate limit is exceeded. Try again in "

        print(f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() {error=}")
        print(
            f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() {self._sleep_on_rate_limit_recommendation=}")
        if not self._sleep_on_rate_limit_recommendation:
            print(f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() return 0...")
            return 0

        error_str = str(error)

        if (
                not isinstance(error, RateLimitError)
                or please_retry_after_msg not in error_str
        ):
            print(f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() return 0...")
            return 0

        # could be second or seconds
        print(
            f"fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() {please_retry_after_msg=}")
        print(
            "fnllm/openai/llm/services/retryer.py OpenAIRetryer._extract_sleep_recommendation() return int(error_str.split(please_retry_after_msg)[1].split(' second')[0])...")
        return int(error_str.split(please_retry_after_msg)[1].split(" second")[0])
