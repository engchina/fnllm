# Copyright (c) 2024 Microsoft Corporation.

"""Factory functions for creating OCIGenAI LLMs."""
from fnllm import Limiter
from fnllm.caching.base import Cache
from fnllm.events.base import LLMEvents
from fnllm.oci_genai.config import OCIGenAIConfig
from fnllm.oci_genai.llm.chat import OCIGenAIChatLLMImpl
from fnllm.oci_genai.llm.chat_streaming import OCIGenAIStreamingChatLLMImpl
from fnllm.oci_genai.llm.chat_text import OCIGenAITextChatLLMImpl
from fnllm.oci_genai.llm.features.tools_parsing import OCIGenAIParseToolsLLM
from fnllm.oci_genai.types.client import (
    OCIGenAIChatLLM,
    OCIGenAIClient,
    OCIGenAIStreamingChatLLM,
    OCIGenAITextChatLLM,
)
from fnllm.services.cache_interactor import CacheInteractor
from fnllm.services.variable_injector import VariableInjector
from .client import create_oci_genai_client
from .utils import create_limiter, create_rate_limiter, create_retryer
from ..llm.services.history_extractor import OCIGenAIHistoryExtractor
from ..llm.services.json import create_json_handler
from ..llm.services.usage_extractor import OCIGenAIUsageExtractor


def create_oci_genai_chat_llm(
        config: OCIGenAIConfig,
        *,
        client: OCIGenAIClient | None = None,
        cache: Cache | None = None,
        cache_interactor: CacheInteractor | None = None,
        events: LLMEvents | None = None,
) -> OCIGenAIChatLLM:
    """Create an OCIGenAI chat LLM."""
    print("create_oci_genai_chat_llm() start...")
    if client is None:
        client = create_oci_genai_client(config)

    # print(f"{config=}")
    limiter = create_limiter(config)

    text_chat_llm = _create_oci_genai_text_chat_llm(
        client=client,
        config=config,
        cache=cache,
        cache_interactor=cache_interactor,
        events=events,
        limiter=limiter,
    )
    streaming_chat_llm = _create_oci_genai_streaming_chat_llm(
        client=client,
        config=config,
        events=events,
        limiter=limiter,
    )
    return OCIGenAIChatLLMImpl(
        text_chat_llm=text_chat_llm,
        streaming_chat_llm=streaming_chat_llm,
    )


def _create_oci_genai_text_chat_llm(
        *,
        client: OCIGenAIClient,
        config: OCIGenAIConfig,
        limiter: Limiter,
        cache: Cache | None,
        cache_interactor: CacheInteractor | None,
        events: LLMEvents | None,
) -> OCIGenAITextChatLLM:
    print("_create_oci_genai_text_chat_llm() start...")
    operation = "chat"
    result = OCIGenAITextChatLLMImpl(
        client,
        model_parameters=config.chat_parameters,
        cache=cache_interactor or CacheInteractor(events, cache),
        events=events,
        json_handler=create_json_handler(config.json_strategy, config.max_json_retries),
        usage_extractor=OCIGenAIUsageExtractor(),
        history_extractor=OCIGenAIHistoryExtractor(),
        variable_injector=VariableInjector(),
        retryer=create_retryer(config=config, operation=operation, events=events),
        rate_limiter=create_rate_limiter(config=config, limiter=limiter, events=events),
    )

    return OCIGenAIParseToolsLLM(result)


def _create_oci_genai_streaming_chat_llm(
        *,
        client: OCIGenAIClient,
        config: OCIGenAIConfig,
        limiter: Limiter,
        events: LLMEvents | None,
) -> OCIGenAIStreamingChatLLM:
    """Create an OCIGenAI streaming chat LLM."""
    print("_create_oci_genai_streaming_chat_llm() start...")
    # print(f"{config.chat_parameters=}")
    return OCIGenAIStreamingChatLLMImpl(
        client,
        model_parameters=config.chat_parameters,
        events=events,
        emit_usage=config.track_stream_usage,
        variable_injector=VariableInjector(),
        rate_limiter=create_rate_limiter(limiter=limiter, config=config, events=events),
    )
