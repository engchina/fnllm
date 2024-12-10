# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI input/output types."""

from collections.abc import AsyncIterable, Awaitable, Callable
from typing import ClassVar, TypeAlias

from oci.generative_ai_inference.models import CohereChatResponse, EmbedTextResult
from pydantic import BaseModel, ConfigDict, Field

from fnllm.oci_genai.types.aliases import (
    OCIGenAIChatCompletionMessageParam,
)
from fnllm.types.generalized import ChatLLMOutput
from fnllm.types.metrics import LLMUsageMetrics

OCIGenAIChatMessageInput: TypeAlias = str | OCIGenAIChatCompletionMessageParam
"""OCIGenAI chat message input."""

OCIGenAIChatHistoryEntry: TypeAlias = OCIGenAIChatCompletionMessageParam
"""OCIGenAI chat history entry."""

OCIGenAIChatCompletionInput: TypeAlias = str | OCIGenAIChatMessageInput | None
"""Main input type for OCIGenAI completions."""


class OCIGenAIChatCompletionMessage(BaseModel):
    chat_response: CohereChatResponse

    class Config:
        arbitrary_types_allowed = True


class OCIGenAIChatOutput(ChatLLMOutput):
    """OCIGenAI chat completion output."""

    raw_input: OCIGenAIChatMessageInput | None
    """Raw input that resulted in this output."""

    raw_output: str | OCIGenAIChatCompletionMessage
    """Raw output message from OCIGenAI."""

    usage: LLMUsageMetrics | None
    """Usage statistics for the completion request."""


class OCIGenAIStreamingChatOutput(BaseModel, arbitrary_types_allowed=True):
    """Async iterable chat content."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    raw_input: OCIGenAIChatMessageInput | None = Field(
        default=None, description="Raw input that resulted in this output."
    )

    usage: LLMUsageMetrics | None = Field(
        default=None,
        description="Usage statistics for the completion request.\nThis will only be available after the stream is complete, if the LLM has been configured to emit usage.",
    )

    content: AsyncIterable[str | None] = Field(exclude=True)

    close: Callable[[], Awaitable[None]] = Field(
        description="Close the underlying iterator", exclude=True
    )


class OCIGenAIEmbeddingsMessage(BaseModel):
    embeddings_response: EmbedTextResult

    class Config:
        arbitrary_types_allowed = True
