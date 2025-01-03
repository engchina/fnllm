# Copyright (c) 2024 Microsoft Corporation.

"""Rate limiting LLM implementation for OCIGenAI."""

import json
from typing import Final, Generic

from openai import APIConnectionError, InternalServerError, RateLimitError
from tiktoken import Encoding

from fnllm.events.base import LLMEvents
from fnllm.limiting import Limiter
from fnllm.oci_genai.llm.utils import llm_tools_to_param
from fnllm.services.rate_limiter import RateLimiter
from fnllm.types.generics import (
    THistoryEntry,
    TInput,
    TJsonModel,
    TModelParameters,
    TOutput,
)
from fnllm.types.io import LLMInput

OPENAI_RETRYABLE_ERRORS: Final[list[type[Exception]]] = [
    RateLimitError,
    APIConnectionError,
    InternalServerError,
]


class OCIGenAIRateLimiter(
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
        print("fnllm/oci_genai/llm/services/rate_limiter.py __init__() start...")
        super().__init__(
            limiter,
            events=events,
        )
        self._encoding = encoder

    def _estimate_request_tokens(
            self,
            prompt: TInput,
            kwargs: LLMInput[TJsonModel, THistoryEntry, TModelParameters],
    ) -> int:
        print("fnllm/oci_genai/llm/services/rate_limiter.py _estimate_request_tokens() start...")
        history = kwargs.get("history", [])
        tools = llm_tools_to_param(kwargs.get("tools", []))

        return sum(
            len(self._encoding.encode(json.dumps(entry)))
            for entry in (*history, *tools, prompt)
        )
