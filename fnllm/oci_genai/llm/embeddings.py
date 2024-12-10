# Copyright (c) 2024 Microsoft Corporation.

"""The EmbeddingsLLM class."""
from typing import cast

import oci
from typing_extensions import Unpack

from fnllm import LLMEvents
from fnllm.base.base import BaseLLM
from fnllm.oci_genai.llm.services.usage_extractor import OCIGenAIUsageExtractor
from fnllm.oci_genai.types.chat.io import OCIGenAIEmbeddingsMessage
from fnllm.oci_genai.types.client import OCIGenAIClient
from fnllm.oci_genai.types.embeddings.io import (
    OCIGenAIEmbeddingsInput,
    OCIGenAIEmbeddingsOutput,
)
from fnllm.oci_genai.types.embeddings.parameters import OCIGenAIEmbeddingsParameters
from fnllm.services.cache_interactor import CacheInteractor
from fnllm.services.rate_limiter import RateLimiter
from fnllm.services.retryer import Retryer
from fnllm.services.variable_injector import VariableInjector
from fnllm.types.io import LLMInput
from fnllm.types.metrics import LLMUsageMetrics


class OCIGenAIEmbeddingsLLMImpl(
    BaseLLM[
        OCIGenAIEmbeddingsInput, OCIGenAIEmbeddingsOutput, None, OCIGenAIEmbeddingsParameters
    ],
):
    """A text-embedding generator LLM."""

    def __init__(
            self,
            client: OCIGenAIClient,
            cache: CacheInteractor,
            *,
            usage_extractor: OCIGenAIUsageExtractor[OCIGenAIEmbeddingsOutput] | None = None,
            variable_injector: VariableInjector | None = None,
            rate_limiter: RateLimiter[
                              OCIGenAIEmbeddingsInput,
                              OCIGenAIEmbeddingsOutput,
                              None,
                              OCIGenAIEmbeddingsParameters,
                          ]
                          | None = None,
            retryer: Retryer[
                         OCIGenAIEmbeddingsInput,
                         OCIGenAIEmbeddingsOutput,
                         None,
                         OCIGenAIEmbeddingsParameters,
                     ]
                     | None = None,
            model_parameters: OCIGenAIEmbeddingsParameters,
            events: LLMEvents | None = None,
    ):
        super().__init__(
            events=events,
            usage_extractor=usage_extractor,
            variable_injector=variable_injector,
            rate_limiter=rate_limiter,
            retryer=retryer,
        )
        self._client = client
        self._model_id = model_parameters["model_id"]
        self._cache = cache
        self._compartment_id = model_parameters["compartment_id"]
        self._global_model_parameters = model_parameters or {}

    def child(self, name: str) -> "OCIGenAIEmbeddingsLLMImpl":
        """Create a child LLM."""
        return OCIGenAIEmbeddingsLLMImpl(
            self._client,
            self._cache.child(name),
            usage_extractor=cast(
                OCIGenAIUsageExtractor[OCIGenAIEmbeddingsOutput], self._usage_extractor
            ),
            variable_injector=self._variable_injector,
            rate_limiter=self._rate_limiter,
            retryer=self._retryer,
            model_parameters=self._global_model_parameters,
            events=self._events,
        )

    def _build_embeddings_parameters(
            self, local_parameters: OCIGenAIEmbeddingsParameters | None
    ) -> OCIGenAIEmbeddingsParameters:
        params: OCIGenAIEmbeddingsParameters = {
            **self._global_model_parameters,
            **(local_parameters or {}),
        }

        return params

    async def _execute_llm(
            self, prompt: OCIGenAIEmbeddingsInput, **kwargs: Unpack[LLMInput]
    ) -> OCIGenAIEmbeddingsOutput:
        name = kwargs.get("name")
        local_model_parameters = kwargs.get("model_parameters")
        bypass_cache = kwargs.get("bypass_cache", False)

        embeddings_parameters = self._build_embeddings_parameters(local_model_parameters)

        embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
        embed_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=embeddings_parameters["model_id"])
        embed_text_detail.inputs = prompt
        embed_text_detail.truncate = "NONE"
        embed_text_detail.compartment_id = embeddings_parameters["compartment_id"]
        embed_text_response = self._client.embed_text(embed_text_detail)
        # embed_texts = [embedding for embedding in embed_text_response.data.embeddings]

        return OCIGenAIEmbeddingsOutput(
            raw_input=prompt,
            raw_output=OCIGenAIEmbeddingsMessage(embeddings_response=embed_text_response.data),
            embeddings=[embedding for embedding in embed_text_response.data.embeddings],
            usage=LLMUsageMetrics(
                input_tokens=len(prompt),
                output_tokens=len(embed_text_response.data.embeddings),
            )
        )
