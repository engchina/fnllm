# Copyright (c) 2024 Microsoft Corporation.

"""The chat-based LLM implementation."""
import asyncio
import json
import re
from collections.abc import AsyncIterator
from typing import TypeAlias, Callable

import oci
from openai import AsyncStream
from openai.types.chat import ChatCompletionChunk
from typing_extensions import Unpack

from fnllm.base.base import BaseLLM
from fnllm.events.base import LLMEvents
from fnllm.oci_genai.llm.utils import build_chat_messages
from fnllm.oci_genai.types.chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIStreamingChatOutput, )
from fnllm.oci_genai.types.chat.parameters import OCIGenAIChatParameters
from fnllm.oci_genai.types.client import OCIGenAIClient
from fnllm.services.rate_limiter import RateLimiter
from fnllm.services.retryer import Retryer
from fnllm.services.variable_injector import VariableInjector
from fnllm.types import LLMUsageMetrics
from fnllm.types.generics import TJsonModel
from fnllm.types.io import LLMInput

ChunkStream: TypeAlias = AsyncStream[ChatCompletionChunk]


class OCIGenAIStreamingChatLLMImpl(
    BaseLLM[
        OCIGenAIChatCompletionInput,
        OCIGenAIStreamingChatOutput,
        OCIGenAIChatHistoryEntry,
        OCIGenAIChatParameters,
    ]
):
    """A chat-based LLM."""

    def __init__(
            self,
            client: OCIGenAIClient,
            *,
            variable_injector: VariableInjector | None = None,
            rate_limiter: RateLimiter[
                              OCIGenAIChatCompletionInput,
                              OCIGenAIStreamingChatOutput,
                              OCIGenAIChatHistoryEntry,
                              OCIGenAIChatParameters,
                          ]
                          | None = None,
            retryer: Retryer[
                         OCIGenAIChatCompletionInput,
                         OCIGenAIStreamingChatOutput,
                         OCIGenAIChatHistoryEntry,
                         OCIGenAIChatParameters,
                     ]
                     | None = None,
            emit_usage: bool = False,
            model_parameters: OCIGenAIChatParameters | None = None,
            events: LLMEvents | None = None,
    ):
        """Create a new OCIGenAIChatLLM."""
        super().__init__(
            events=events,
            variable_injector=variable_injector,
            rate_limiter=rate_limiter,
            retryer=retryer,
        )
        self._client = client
        self._emit_usage = emit_usage
        # print(f"{model_parameters=}")
        self._global_model_parameters = model_parameters or {}
        # print(f"{self._global_model_parameters=}")

    def child(self, name: str) -> "OCIGenAIStreamingChatLLMImpl":
        """Create a child LLM."""
        return self

    def _build_completion_parameters(
            self, local_parameters: OCIGenAIChatParameters | None
    ) -> OCIGenAIChatParameters:
        params: OCIGenAIChatParameters = {
            **self._global_model_parameters,
            **(local_parameters or {}),
        }

        return params

    async def _execute_llm(
            self,
            prompt: OCIGenAIChatCompletionInput,
            **kwargs: Unpack[
                LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]
            ],
    ) -> OCIGenAIStreamingChatOutput:
        print("chat_streaming.py _execute_llm() start...")
        # print(f"{kwargs=}")
        history = kwargs.get("history", [])
        local_model_parameters = kwargs.get("model_parameters")
        messages, prompt_message = build_chat_messages(prompt, history)
        completion_parameters = self._build_completion_parameters(
            local_model_parameters
        )

        completion_kwargs = {**completion_parameters, "stream": True}
        if self._emit_usage:
            completion_kwargs["stream_options"] = {"include_usage": True}

        chat_detail = oci.generative_ai_inference.models.ChatDetails()

        chat_request = oci.generative_ai_inference.models.CohereChatRequest()
        # chat_request.preamble_override = f"{system_prompt}"
        # print(f"{prompt=}")
        # print(f"{prompt_message=}")
        chat_request.message = prompt
        chat_request.max_tokens = completion_parameters.pop("max_tokens", 4000)
        chat_request.temperature = completion_parameters.pop("temperature", 0.0)
        chat_request.frequency_penalty = completion_parameters.pop("frequency_penalty", 0.0)
        chat_request.top_p = completion_parameters.pop("top_p", 0.75)
        chat_request.top_k = completion_parameters.pop("top_k", 0)
        chat_request.is_stream = True
        chat_request.is_echo = True
        # chat_request.is_raw_prompting = True

        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=completion_parameters.pop("model_id"))
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = completion_parameters.pop("compartment_id")

        chat_response = self._client.chat(chat_detail)
        iterator = StreamingChatIterator(chunks=chat_response.data, events=chat_response.data.events())
        result = OCIGenAIStreamingChatOutput(
            raw_input=prompt,
            content=iterator.iterator,
            close=iterator.close,
        )

        def handle_usage(usage: LLMUsageMetrics) -> None:
            result.usage = usage

        iterator.on_usage(handle_usage)

        return result


class StreamingChatIterator:
    """A streaming llm response iterator."""

    def __init__(
            self,
            chunks: ChunkStream,
            events: LLMEvents,
    ):
        """Create a new Response."""
        self._chunks = chunks
        self._events = events
        self._iterator = self.__stream__()

    def on_usage(self, cb: Callable[[LLMUsageMetrics], None]) -> None:
        """Handle usage events."""
        self._on_usage = cb

    async def __stream__(self) -> AsyncIterator[str | None]:
        """Read chunks from the stream."""
        print("chat_streaming.py StreamingChatIterator.__stream__() start...")

        # usage = LLMUsageMetrics()
        async def async_wrapper(sync_generator):
            for item in sync_generator:
                await asyncio.sleep(0)  # 确保异步行为
                yield item

        usage = LLMUsageMetrics()
        try:
            if not self._chunks or not self._chunks.events():
                print("No events in the stream.")
                return

            async for event in async_wrapper(self._chunks.events()):
                # Note: this is only emitted _just_ prior to the stream completing.
                delta = json.loads(event.data)
                # print(f"{delta=}")
                if 'finishReason' in delta.keys():
                    complete_text = delta['text']
                    prompt = delta['prompt']
                    pattern = r"<\|START_OF_TURN_TOKEN\|><\|USER_TOKEN\|>(.*?)<\|END_OF_TURN_TOKEN\|>"
                    match = re.search(pattern, prompt)
                    if match:
                        prompt = match.group(1)  # 提取括号中的内容
                    else:
                        print("No match found.")

                    usage = LLMUsageMetrics(
                        input_tokens=len(prompt),
                        output_tokens=len(complete_text),
                    )

                    self._on_usage(usage)
                    break
                if 'text' in delta:
                    yield delta['text']

        except BaseException as e:
            # print(f"{e=}")
            raise e

    @property
    def iterator(self) -> AsyncIterator[str | None]:
        """Return the content."""
        print("chat_streaming.py StreamingChatIterator.iterator() start...")
        return self._iterator

    async def close(self) -> None:
        """Close the stream."""
        print("chat_streaming.py StreamingChatIterator.close() start...")
        await self._chunks.close()
