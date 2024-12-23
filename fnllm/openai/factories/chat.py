# Copyright (c) 2024 Microsoft Corporation.

"""Factory functions for creating OpenAI LLMs."""

from fnllm.caching.base import Cache
from fnllm.events.base import LLMEvents
from fnllm.limiting.base import Limiter
from fnllm.openai.config import OpenAIConfig
from fnllm.openai.llm.chat import OpenAIChatLLMImpl
from fnllm.openai.llm.chat_streaming import OpenAIStreamingChatLLMImpl
from fnllm.openai.llm.chat_text import OpenAITextChatLLMImpl
from fnllm.openai.llm.features.tools_parsing import OpenAIParseToolsLLM
from fnllm.openai.llm.services.history_extractor import OpenAIHistoryExtractor
from fnllm.openai.llm.services.json import create_json_handler
from fnllm.openai.llm.services.usage_extractor import OpenAIUsageExtractor
from fnllm.openai.types.client import (
    OpenAIChatLLM,
    OpenAIClient,
    OpenAIStreamingChatLLM,
    OpenAITextChatLLM,
)
from fnllm.services.cache_interactor import CacheInteractor
from fnllm.services.variable_injector import VariableInjector

from .client import create_openai_client
from .utils import create_limiter, create_rate_limiter, create_retryer


def create_openai_chat_llm(
        config: OpenAIConfig,
        *,
        client: OpenAIClient | None = None,
        cache: Cache | None = None,
        cache_interactor: CacheInteractor | None = None,
        events: LLMEvents | None = None,
) -> OpenAIChatLLM:
    """Create an OpenAI chat LLM."""
    print()
    print("fnllm/openai/factories/chat.py create_openai_chat_llm() start...")
    if client is None:
        print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke create_openai_client()start...")
        client = create_openai_client(config)
        print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke create_openai_client() end...")

    print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke create_limiter() start...")
    limiter = create_limiter(config)
    print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke create_limiter() end...")

    print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke _create_openai_text_chat_llm() start...")
    text_chat_llm = _create_openai_text_chat_llm(
        client=client,
        config=config,
        cache=cache,
        cache_interactor=cache_interactor,
        events=events,
        limiter=limiter,
    )
    print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke _create_openai_text_chat_llm() end...")

    print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke _create_openai_streaming_chat_llm() end...")
    streaming_chat_llm = _create_openai_streaming_chat_llm(
        client=client,
        config=config,
        events=events,
        limiter=limiter,
    )
    print("fnllm/openai/factories/chat.py create_openai_chat_llm() invoke _create_openai_streaming_chat_llm() end...")

    return OpenAIChatLLMImpl(
        text_chat_llm=text_chat_llm,
        streaming_chat_llm=streaming_chat_llm,
    )


def _create_openai_text_chat_llm(
        *,
        client: OpenAIClient,
        config: OpenAIConfig,
        limiter: Limiter,
        cache: Cache | None,
        cache_interactor: CacheInteractor | None,
        events: LLMEvents | None,
) -> OpenAITextChatLLM:
    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() start...")
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {config=}")
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {limiter=}")
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {cache=}")
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {cache_interactor=}")
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {events=}")
    operation = "chat"
    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke create_json_handler() start...")
    json_handler = create_json_handler(config.json_strategy, config.max_json_retries)
    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke create_json_handler() end...")

    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke create_retryer() start...")
    retryer = create_retryer(config=config, operation=operation, events=events)
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {retryer=}")
    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke create_retryer() end...")

    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke create_rate_limiter() start...")
    rate_limiter = create_rate_limiter(config=config, limiter=limiter, events=events)
    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() {rate_limiter=}")
    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke create_rate_limiter() end...")

    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke OpenAITextChatLLMImpl() start...")
    result = OpenAITextChatLLMImpl(
        client,
        model=config.model,
        model_parameters=config.chat_parameters,
        cache=cache_interactor or CacheInteractor(events, cache),
        events=events,
        json_handler=json_handler,
        usage_extractor=OpenAIUsageExtractor(),
        history_extractor=OpenAIHistoryExtractor(),
        variable_injector=VariableInjector(),
        retryer=retryer,
        rate_limiter=rate_limiter,
    )
    print("fnllm/openai/factories/chat.py _create_openai_text_chat_llm() invoke OpenAITextChatLLMImpl() end...")

    print(f"fnllm/openai/factories/chat.py _create_openai_text_chat_llm() return OpenAIParseToolsLLM({result=})...")
    return OpenAIParseToolsLLM(result)


def _create_openai_streaming_chat_llm(
        *,
        client: OpenAIClient,
        config: OpenAIConfig,
        limiter: Limiter,
        events: LLMEvents | None,
) -> OpenAIStreamingChatLLM:
    """Create an OpenAI streaming chat LLM."""
    print("fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() start...")
    print(f"fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() {config=}")
    print(f"fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() {limiter=}")
    print(f"fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() {events=}")

    print("fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() invoke create_rate_limiter() start...")
    rate_limiter = create_rate_limiter(limiter=limiter, config=config, events=events)
    print(f"fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() {rate_limiter=}")

    print(
        "fnllm/openai/factories/chat.py _create_openai_streaming_chat_llm() return OpenAIStreamingChatLLMImpl() start...")
    print()
    return OpenAIStreamingChatLLMImpl(
        client,
        model=config.model,
        model_parameters=config.chat_parameters,
        events=events,
        emit_usage=config.track_stream_usage,
        variable_injector=VariableInjector(),
        rate_limiter=rate_limiter,
    )
