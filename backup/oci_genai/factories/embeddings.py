# Copyright (c) 2024 Microsoft Corporation.

"""Factory functions for creating OCIGenAI LLMs."""

from fnllm.caching.base import Cache
from fnllm.events.base import LLMEvents
from fnllm.oci_genai.config import OCIGenAIConfig
from fnllm.oci_genai.llm.embeddings import OCIGenAIEmbeddingsLLMImpl
from fnllm.oci_genai.llm.services.usage_extractor import OCIGenAIUsageExtractor
from fnllm.oci_genai.types.client import OCIGenAIClient, OCIGenAIEmbeddingsLLM
from fnllm.services.cache_interactor import CacheInteractor
from fnllm.services.variable_injector import VariableInjector

from .client import create_oci_genai_client
from .utils import create_limiter, create_rate_limiter, create_retryer


def create_oci_genai_embeddings_llm(
        config: OCIGenAIConfig,
        *,
        client: OCIGenAIClient | None = None,
        cache: Cache | None = None,
        cache_interactor: CacheInteractor | None = None,
        events: LLMEvents | None = None,
) -> OCIGenAIEmbeddingsLLM:
    """Create an OCIGenAI embeddings LLM."""
    print("create_oci_genai_embeddings_llm() start...")
    # print(f"{config.chat_parameters=}")
    operation = "embedding"

    if client is None:
        client = create_oci_genai_client(config)

    limiter = create_limiter(config)
    return OCIGenAIEmbeddingsLLMImpl(
        client,
        model_parameters=config.chat_parameters,
        cache=cache_interactor or CacheInteractor(events, cache),
        events=events,
        usage_extractor=OCIGenAIUsageExtractor(),
        variable_injector=VariableInjector(),
        rate_limiter=create_rate_limiter(config=config, events=events, limiter=limiter),
        retryer=create_retryer(config=config, operation=operation, events=events),
    )
