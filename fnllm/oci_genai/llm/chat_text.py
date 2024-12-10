# Copyright (c) 2024 Microsoft Corporation.

"""The chat-based LLM implementation."""
import asyncio
from typing import Any, cast

import oci
from oci.generative_ai_inference.models import ChatDetails
from typing_extensions import Unpack

from fnllm import LLMEvents
from fnllm.base.base import BaseLLM
from fnllm.oci_genai.llm.services.history_extractor import OCIGenAIHistoryExtractor
from fnllm.oci_genai.llm.services.usage_extractor import OCIGenAIUsageExtractor
from fnllm.oci_genai.llm.utils import build_chat_messages
from fnllm.oci_genai.types import OCIGenAIChatCompletionModel
from fnllm.oci_genai.types.chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatOutput, )
from fnllm.oci_genai.types.chat.parameters import OCIGenAIChatParameters
from fnllm.oci_genai.types.client import OCIGenAIClient
from fnllm.services.cache_interactor import CacheInteractor
from fnllm.services.json import JsonHandler
from fnllm.services.rate_limiter import RateLimiter
from fnllm.services.retryer import Retryer
from fnllm.services.variable_injector import VariableInjector
from fnllm.types.generics import TJsonModel
from fnllm.types.io import LLMInput
from fnllm.types.metrics import LLMUsageMetrics


class OCIGenAITextChatLLMImpl(
    BaseLLM[
        OCIGenAIChatCompletionInput,
        OCIGenAIChatOutput,
        OCIGenAIChatHistoryEntry,
        OCIGenAIChatParameters,
    ]
):
    """A chat-based LLM."""

    def __init__(
            self,
            client: OCIGenAIClient,
            cache: CacheInteractor,
            *,
            usage_extractor: OCIGenAIUsageExtractor[OCIGenAIChatOutput] | None = None,
            history_extractor: OCIGenAIHistoryExtractor | None = None,
            variable_injector: VariableInjector | None = None,
            rate_limiter: RateLimiter[
                              OCIGenAIChatCompletionInput,
                              OCIGenAIChatOutput,
                              OCIGenAIChatHistoryEntry,
                              OCIGenAIChatParameters,
                          ]
                          | None = None,
            retryer: Retryer[
                         OCIGenAIChatCompletionInput,
                         OCIGenAIChatOutput,
                         OCIGenAIChatHistoryEntry,
                         OCIGenAIChatParameters,
                     ]
                     | None = None,
            model_parameters: OCIGenAIChatParameters | None = None,
            events: LLMEvents | None = None,
            json_handler: JsonHandler[OCIGenAIChatOutput, OCIGenAIChatHistoryEntry]
                          | None = None,
    ):
        """Create a new OCIGenAIChatLLM."""
        super().__init__(
            events=events,
            usage_extractor=usage_extractor,
            history_extractor=history_extractor,
            variable_injector=variable_injector,
            retryer=retryer,
            rate_limiter=rate_limiter,
            json_handler=json_handler,
        )
        # print(f"{model_parameters=}")
        self._client = client
        self._global_model_parameters = model_parameters or {}
        self._cache = cache

    def child(self, name: str) -> Any:
        """Create a child LLM."""
        return OCIGenAITextChatLLMImpl(
            self._client,
            self._cache.child(name),
            events=self.events,
            usage_extractor=cast(
                OCIGenAIUsageExtractor[OCIGenAIChatOutput], self._usage_extractor
            ),
            history_extractor=cast(OCIGenAIHistoryExtractor, self._history_extractor),
            variable_injector=self._variable_injector,
            rate_limiter=self._rate_limiter,
            retryer=self._retryer,
            model_parameters=self._global_model_parameters,
            json_handler=self._json_handler,
        )

    def _build_completion_parameters(
            self, local_parameters: OCIGenAIChatParameters | None
    ) -> OCIGenAIChatParameters:
        params: OCIGenAIChatParameters = {
            **self._global_model_parameters,
            **(local_parameters or {}),
        }

        return params

    async def _call_completion_or_cache(
            self,
            name: str | None,
            *,
            messages: list[OCIGenAIChatHistoryEntry],
            chat_detail: ChatDetails,
            parameters: OCIGenAIChatParameters,
            bypass_cache: bool,
    ) -> OCIGenAIChatCompletionModel:
        # TODO: check if we need to remove max_tokens and n from the keys
        return await self._cache.get_or_insert(
            lambda: asyncio.to_thread(self._client.chat, chat_detail),
            prefix=f"chat_{name}" if name else "chat",
            key_data={"messages": messages, "parameters": parameters},
            name=name,
            json_model=OCIGenAIChatCompletionModel,
            bypass_cache=bypass_cache,
        )

    async def _execute_llm(
            self,
            prompt: OCIGenAIChatCompletionInput,
            **kwargs: Unpack[
                LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]
            ],
    ) -> OCIGenAIChatOutput:
        print("_execute_llm() start...")
        name = kwargs.get("name")
        history = kwargs.get("history", [])
        bypass_cache = kwargs.get("bypass_cache", False)
        local_model_parameters = kwargs.get("model_parameters")
        messages, prompt_message = build_chat_messages(prompt, history)
        completion_parameters = self._build_completion_parameters(
            local_model_parameters
        )
        # print(f"{chat_parameters=}")

        chat_detail = oci.generative_ai_inference.models.ChatDetails()

        chat_request = oci.generative_ai_inference.models.CohereChatRequest()
        # chat_request.preamble_override = f"{system_prompt}"
        chat_request.message = prompt
        chat_request.max_tokens = completion_parameters.pop("max_tokens", 4000)
        chat_request.temperature = completion_parameters.pop("temperature", 0.0)
        chat_request.frequency_penalty = completion_parameters.pop("frequency_penalty", 0.0)
        chat_request.top_p = completion_parameters.pop("top_p", 0.75)
        chat_request.top_k = completion_parameters.pop("top_k", 0)
        chat_request.is_echo = True

        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=completion_parameters.get("model_id"))
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = completion_parameters.get("compartment_id")

        # If there's a history, we need to add it to the chat request
        if history:
            chat_request.conversation = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]

        chat_response = self._client.chat(chat_detail)

        completion = await self._call_completion_or_cache(
            name,
            messages=messages,
            chat_detail=chat_detail,
            parameters=completion_parameters,
            bypass_cache=bypass_cache,
        )

        response = completion.data.chat_response

        # print(f"{response=}")
        return OCIGenAIChatOutput(
            raw_input=prompt,
            # raw_output=OCIGenAIChatCompletionMessage(chat_response=chat_response.data.chat_response),
            raw_output=response.text,
            content=response.text,
            usage=LLMUsageMetrics(
                input_tokens=len(prompt),
                output_tokens=len(response.text),
            )
        )
