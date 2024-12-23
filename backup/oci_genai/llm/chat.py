# Copyright (c) 2024 Microsoft Corporation.
"""OCIGenAI Chat LLM."""

from typing import Any, Literal, overload

from typing_extensions import Unpack

from fnllm.oci_genai.types.chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatOutput,
    OCIGenAIStreamingChatOutput,
)
from fnllm.oci_genai.types.chat.parameters import OCIGenAIChatParameters
from fnllm.oci_genai.types.client import (
    OCIGenAIChatLLM,
    OCIGenAIStreamingChatLLM,
    OCIGenAITextChatLLM,
)
from fnllm.types.generics import TJsonModel
from fnllm.types.io import LLMInput, LLMOutput


class OCIGenAIChatLLMImpl(OCIGenAIChatLLM):
    """The OCIGenAIChatLLM Facade."""

    def __init__(
            self,
            *,
            text_chat_llm: OCIGenAITextChatLLM,
            streaming_chat_llm: OCIGenAIStreamingChatLLM,
    ):
        """Create a new OCIGenAI Chat Facade."""
        self._text_chat_llm = text_chat_llm
        self._streaming_chat_llm = streaming_chat_llm

    def child(self, name: str) -> "OCIGenAIChatLLMImpl":
        """Create a child LLM (with child cache)."""
        return OCIGenAIChatLLMImpl(
            text_chat_llm=self._text_chat_llm.child(name),
            streaming_chat_llm=self._streaming_chat_llm.child(name),
        )

    @overload
    async def __call__(
            self,
            prompt: OCIGenAIChatCompletionInput,
            *,
            stream: Literal[True],
            **kwargs: Unpack[
                LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]
            ],
    ) -> LLMOutput[OCIGenAIStreamingChatOutput, TJsonModel, OCIGenAIChatHistoryEntry]: ...

    @overload
    async def __call__(
            self,
            prompt: OCIGenAIChatCompletionInput,
            *,
            stream: Literal[False] | None = None,
            **kwargs: Unpack[
                LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]
            ],
    ) -> LLMOutput[OCIGenAIChatOutput, TJsonModel, OCIGenAIChatHistoryEntry]: ...

    async def __call__(
            self,
            prompt: OCIGenAIChatCompletionInput,
            *,
            stream: bool | None = None,
            **kwargs: Unpack[
                LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]
            ],
    ) -> LLMOutput[
        Any | OCIGenAIStreamingChatOutput | OCIGenAIChatOutput,
        TJsonModel,
        OCIGenAIChatHistoryEntry,
    ]:
        """Invoke the streaming chat output."""
        if stream:
            return await self._streaming_chat_llm(prompt, **kwargs)

        return await self._text_chat_llm(prompt, **kwargs)
