# Copyright (c) 2024 Microsoft Corporation.

"""Helper functions for creating OpenAI LLMs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import tiktoken

from fnllm.limiting.composite import CompositeLimiter
from fnllm.limiting.concurrency import ConcurrencyLimiter
from fnllm.limiting.rpm import RPMLimiter
from fnllm.limiting.tpm import TPMLimiter
from fnllm.openai.llm.services.rate_limiter import OpenAIRateLimiter
from fnllm.openai.llm.services.retryer import OpenAIRetryer

if TYPE_CHECKING:
    from fnllm.events.base import LLMEvents
    from fnllm.limiting.base import Limiter
    from fnllm.openai.config import OpenAIConfig
    from fnllm.services.rate_limiter import RateLimiter
    from fnllm.services.retryer import Retryer


def _get_encoding(encoding_name: str) -> tiktoken.Encoding:
    print()
    print("fnllm/openai/factories/utils.py _get_encoding() start...")
    print(f"fnllm/openai/factories/utils.py _get_encoding() return tiktoken.get_encoding({encoding_name=})...")
    print()
    return tiktoken.get_encoding(encoding_name)


def create_limiter(config: OpenAIConfig) -> Limiter:
    """Create an LLM limiter based on the incoming configuration."""
    print()
    print("fnllm/openai/factories/utils.py create_limiter() start...")
    limiters = []

    if config.max_concurrency:
        limiters.append(ConcurrencyLimiter.from_max_concurrency(config.max_concurrency))

    if config.requests_per_minute:
        limiters.append(
            RPMLimiter.from_rpm(
                config.requests_per_minute, burst_mode=config.requests_burst_mode
            )
        )

    if config.tokens_per_minute:
        limiters.append(TPMLimiter.from_tpm(config.tokens_per_minute))
    print(f"fnllm/openai/factories/utils.py create_limiter() {limiters=}")
    print(f"fnllm/openai/factories/utils.py create_limiter() return CompositeLimiter({limiters=})...")

    return CompositeLimiter(limiters)


def create_rate_limiter(
        *,
        limiter: Limiter,
        config: OpenAIConfig,
        events: LLMEvents | None,
) -> RateLimiter[Any, Any, Any, Any]:
    """Wraps the LLM to be rate limited."""
    print()
    print("fnllm/openai/factories/utils.py create_rate_limiter() start...")
    print(f"fnllm/openai/factories/utils.py create_rate_limiter() {limiter=}")
    print(f"fnllm/openai/factories/utils.py create_rate_limiter() {config=}")
    print(f"fnllm/openai/factories/utils.py create_rate_limiter() {events=}")
    print(f"fnllm/openai/factories/utils.py create_rate_limiter() invoke _get_encoding() start...")
    encoder = _get_encoding(config.encoding)
    print(f"fnllm/openai/factories/utils.py create_rate_limiter() invoke _get_encoding() end...")

    print(f"fnllm/openai/factories/utils.py create_rate_limiter() invoke OpenAIRateLimiter() start...")
    openai_rate_limiter = OpenAIRateLimiter(
        encoder=encoder,
        limiter=limiter,
        events=events,
    )
    print(f"fnllm/openai/factories/utils.py create_rate_limiter() invoke OpenAIRateLimiter() end...")

    print(f"fnllm/openai/factories/utils.py create_rate_limiter() return {openai_rate_limiter=}...")
    print()

    return openai_rate_limiter


def create_retryer(
        *,
        config: OpenAIConfig,
        operation: str,
        events: LLMEvents | None,
) -> Retryer[Any, Any, Any, Any]:
    """Wraps the LLM with retry logic."""
    print()
    print("fnllm/openai/factories/utils.py create_retryer() start...")
    print(f"fnllm/openai/factories/utils.py create_retryer() {config=}")
    print(f"fnllm/openai/factories/utils.py create_retryer() {operation=}")
    print(f"fnllm/openai/factories/utils.py create_retryer() {events=}")

    print(f"fnllm/openai/factories/utils.py create_retryer() invoke OpenAIRetryer() start...")
    openai_retryer = OpenAIRetryer(
        tag=operation,
        max_retries=config.max_retries,
        max_retry_wait=config.max_retry_wait,
        sleep_on_rate_limit_recommendation=config.sleep_on_rate_limit_recommendation,
        events=events,
    )
    print(f"fnllm/openai/factories/utils.py create_retryer() invoke OpenAIRetryer() end...")

    print(f"fnllm/openai/factories/utils.py create_retryer() return {openai_retryer=}...")
    print()
    return openai_retryer
