# Copyright (c) 2024 Microsoft Corporation.

"""Rate limiting LLM implementation for OpenAI."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final, Generic

from openai import APIConnectionError, InternalServerError, RateLimitError

from fnllm.openai.llm.utils import llm_tools_to_param
from fnllm.services.rate_limiter import RateLimiter
from fnllm.types.generics import (
    THistoryEntry,
    TInput,
    TJsonModel,
    TModelParameters,
    TOutput,
)

if TYPE_CHECKING:
    from tiktoken import Encoding

    from fnllm.events.base import LLMEvents
    from fnllm.limiting import Limiter
    from fnllm.types.io import LLMInput

OPENAI_RETRYABLE_ERRORS: Final[list[type[Exception]]] = [
    RateLimitError,
    APIConnectionError,
    InternalServerError,
]


class OpenAIRateLimiter(
    RateLimiter[TInput, TOutput, THistoryEntry, TModelParameters],
    Generic[TInput, TOutput, THistoryEntry, TModelParameters],
):
    """A base class to rate limit the LLM."""

    def __init__(
            self,
            limiter: Limiter,
            encoder: Encoding,
            *,
            events: LLMEvents | None = None,
    ):
        """Create a new BaseRateLimitLLM."""
        print()
        print("fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter.__init__() start...")
        print(
            "fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter.__init__() invoke super().__init__() start...")
        super().__init__(
            limiter,
            events=events,
        )
        print("fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter.__init__() invoke super().__init__() end...")

        self._encoding = encoder
        print("fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter.__init__() end...")
        print()

    def _estimate_request_tokens(
            self,
            prompt: TInput,
            kwargs: LLMInput[TJsonModel, THistoryEntry, TModelParameters],
    ) -> int:
        print("fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() start...")
        print(f"fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() {prompt=}")
        print(f"fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() {kwargs=}")
        history = kwargs.get("history", [])

        print(
            f"fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() invoke llm_tools_to_param() start...")
        tools = llm_tools_to_param(kwargs.get("tools", []))
        print(
            f"fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() invoke llm_tools_to_param() end...")

        print(f"fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() {tools=}")
        tokens_usage = sum(
            len(self._encoding.encode(json.dumps(entry)))
            for entry in (*history, *tools, prompt)
        )
        print(
            f"fnllm/openai/llm/services/rate_limiter.py OpenAIRateLimiter._estimate_request_tokens() return {tokens_usage=}")
        return tokens_usage
