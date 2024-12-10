# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI specific types."""

from .aliases import (
    OCIGenAIChatCompletionAssistantMessageParam,
    OCIGenAIChatCompletionFunctionMessageParam,
    OCIGenAIChatCompletionMessageModel,
    OCIGenAIChatCompletionMessageParam,
    OCIGenAIChatCompletionMessageToolCallModel,
    OCIGenAIChatCompletionMessageToolCallParam,
    OCIGenAIChatCompletionModel,
    OCIGenAIChatCompletionStreamOptionsParam,
    OCIGenAIChatCompletionSystemMessageParam,
    OCIGenAIChatCompletionToolChoiceOptionParam,
    OCIGenAIChatCompletionToolMessageParam,
    OCIGenAIChatCompletionToolParam,
    OCIGenAIChatCompletionUserMessageParam,
    OCIGenAIChatModel,
    OCIGenAIChoiceModel,
    OCIGenAICompletionUsageModel,
    OCIGenAICreateEmbeddingResponseModel,
    OCIGenAIEmbeddingModel,
    OCIGenAIEmbeddingUsageModel,
    OCIGenAIFunctionCallCreateParam,
    OCIGenAIFunctionCallModel,
    OCIGenAIFunctionCallParam,
    OCIGenAIFunctionCreateParam,
    OCIGenAIFunctionDefinitionParam,
    OCIGenAIFunctionModel,
    OCIGenAIFunctionParam,
    OCIGenAIResponseFormatCreateParam,
)
from .chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatMessageInput,
    OCIGenAIChatOutput,
    OCIGenAIStreamingChatOutput,
)
from .chat.parameters import OCIGenAIChatParameters
from .client import (
    OCIGenAIChatLLM,
    OCIGenAIClient,
    OCIGenAIEmbeddingsLLM,
    OCIGenAITextChatLLM,
)
from .embeddings.io import OCIGenAIEmbeddingsInput, OCIGenAIEmbeddingsOutput
from .embeddings.parameters import OCIGenAIEmbeddingsParameters

__all__ = [
    "OCIGenAIChatCompletionAssistantMessageParam",
    "OCIGenAIChatCompletionFunctionMessageParam",
    "OCIGenAIChatCompletionInput",
    "OCIGenAIChatCompletionMessageModel",
    "OCIGenAIChatCompletionMessageParam",
    "OCIGenAIChatCompletionMessageToolCallModel",
    "OCIGenAIChatCompletionMessageToolCallParam",
    "OCIGenAIChatCompletionModel",
    "OCIGenAIChatCompletionStreamOptionsParam",
    "OCIGenAIChatCompletionSystemMessageParam",
    "OCIGenAIChatCompletionToolChoiceOptionParam",
    "OCIGenAIChatCompletionToolMessageParam",
    "OCIGenAIChatCompletionToolParam",
    "OCIGenAIChatCompletionUserMessageParam",
    "OCIGenAIChatHistoryEntry",
    "OCIGenAIChatLLM",
    "OCIGenAIChatMessageInput",
    "OCIGenAIChatModel",
    "OCIGenAIChatOutput",
    "OCIGenAIChatParameters",
    "OCIGenAIChoiceModel",
    "OCIGenAIClient",
    "OCIGenAICompletionUsageModel",
    "OCIGenAICreateEmbeddingResponseModel",
    "OCIGenAIEmbeddingModel",
    "OCIGenAIEmbeddingUsageModel",
    "OCIGenAIEmbeddingsInput",
    "OCIGenAIEmbeddingsLLM",
    "OCIGenAIEmbeddingsOutput",
    "OCIGenAIEmbeddingsParameters",
    "OCIGenAIFunctionCallCreateParam",
    "OCIGenAIFunctionCallModel",
    "OCIGenAIFunctionCallParam",
    "OCIGenAIFunctionCreateParam",
    "OCIGenAIFunctionDefinitionParam",
    "OCIGenAIFunctionModel",
    "OCIGenAIFunctionParam",
    "OCIGenAIResponseFormatCreateParam",
    "OCIGenAIStreamingChatOutput",
    "OCIGenAITextChatLLM",
]
