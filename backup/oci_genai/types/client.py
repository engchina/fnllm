# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI client types."""

from typing import Literal, Protocol, TypeAlias, overload, runtime_checkable

from oci.generative_ai_inference import GenerativeAiInferenceClient
from typing_extensions import Unpack

from fnllm.oci_genai.types.chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatOutput,
    OCIGenAIStreamingChatOutput,
)
from fnllm.oci_genai.types.chat.parameters import OCIGenAIChatParameters
from fnllm.oci_genai.types.embeddings.io import (
    OCIGenAIEmbeddingsInput,
    OCIGenAIEmbeddingsOutput,
)
from fnllm.oci_genai.types.embeddings.parameters import OCIGenAIEmbeddingsParameters
from fnllm.types.generics import TJsonModel
from fnllm.types.io import LLMInput, LLMOutput
from fnllm.types.protocol import LLM

OCIGenAIClient = GenerativeAiInferenceClient
"""Allowed OCIGenAI client types."""

OCIGenAITextChatLLM: TypeAlias = LLM[
    OCIGenAIChatCompletionInput,
    OCIGenAIChatOutput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatParameters,
]
"""Alias for the fully typed OCIGenAIChatLLM instance."""

OCIGenAIStreamingChatLLM: TypeAlias = LLM[
    OCIGenAIChatCompletionInput,
    OCIGenAIStreamingChatOutput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatParameters,
]

OCIGenAIEmbeddingsLLM: TypeAlias = LLM[
    OCIGenAIEmbeddingsInput, OCIGenAIEmbeddingsOutput, None, OCIGenAIEmbeddingsParameters
]
"""Alias for the fully typed OCIGenAIEmbeddingsLLM instance."""


@runtime_checkable
class OCIGenAIChatLLM(Protocol):
    """Protocol for the OCIGenAI chat LLM."""

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

    def child(self, name: str) -> "OCIGenAIChatLLM":
        """Create a child LLM."""
        ...
