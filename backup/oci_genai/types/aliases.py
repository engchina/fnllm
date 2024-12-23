# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI aliases types."""

from collections.abc import Sequence
from typing import Literal, TypeAlias

from openai.types.chat import (
    ChatCompletion as ChatCompletionModel,
)
from openai.types.chat.chat_completion import Choice as ChoiceModel
from openai.types.chat.chat_completion_assistant_message_param import (
    FunctionCall as FunctionCallParam,
)
from openai.types.chat.chat_completion_function_message_param import (
    ChatCompletionFunctionMessageParam,
)
from openai.types.chat.chat_completion_message import FunctionCall as FunctionCallModel, ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall as ChatCompletionMessageToolCallModel,
)
from openai.types.chat.chat_completion_message_tool_call import (
    Function as FunctionModel,
)
from openai.types.chat.chat_completion_message_tool_call_param import (
    ChatCompletionMessageToolCallParam,
)
from openai.types.chat.chat_completion_message_tool_call_param import (
    Function as FunctionParam,
)
from openai.types.chat.chat_completion_stream_options_param import (
    ChatCompletionStreamOptionsParam,
)
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.chat_completion_tool_message_param import (
    ChatCompletionToolMessageParam,
)
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import (
    Function as FunctionCreateParam,
)
from openai.types.chat.completion_create_params import (
    FunctionCall as FunctionCallCreateParam,
)
from openai.types.chat.completion_create_params import (
    ResponseFormat as ResponseFormatCreateParam,
)
from openai.types.chat_model import ChatModel
from openai.types.completion_usage import CompletionUsage as CompletionUsageModel
from openai.types.create_embedding_response import (
    CreateEmbeddingResponse as CreateEmbeddingResponseModel,
)
from openai.types.create_embedding_response import Usage as EmbeddingUsageModel
from openai.types.embedding import Embedding as EmbeddingModel
from openai.types.shared_params.function_definition import (
    FunctionDefinition as FunctionDefinitionParam,
)
from typing_extensions import Required, TypedDict

OCIGenAIChatModel: TypeAlias = ChatModel
"""Alias for the ChatModel (available model types)."""

OCIGenAICompletionUsageModel: TypeAlias = CompletionUsageModel
"""Alias for the CompletionUsage (base model)."""

OCIGenAIChatCompletionStreamOptionsParam: TypeAlias = ChatCompletionStreamOptionsParam
"""Alias for the ChatCompletionStreamOptionsParam (param)."""

OCIGenAIChatCompletionModel: TypeAlias = ChatCompletionModel
"""Alias for the ChatCompletion (base model)."""

OCIGenAIChatCompletionMessageModel: TypeAlias = ChatCompletionMessage
"""Alias for the ChatCompletionMessage (base model)."""

OCIGenAIChoiceModel: TypeAlias = ChoiceModel
"""Alias for the Choice (base model)."""

OCIGenAIFunctionModel: TypeAlias = FunctionModel
"""Alias for the Function (base model)."""

OCIGenAIFunctionParam: TypeAlias = FunctionParam
"""Alias for the Function (param)."""

OCIGenAIFunctionCreateParam: TypeAlias = FunctionCreateParam
"""Alias for the Function (create param)."""

OCIGenAIFunctionCallModel: TypeAlias = FunctionCallModel
"""Alias for the FunctionCall (base model)."""

OCIGenAIFunctionCallParam: TypeAlias = FunctionCallParam
"""Alias for the FunctionCall (param)."""

OCIGenAIFunctionCallCreateParam: TypeAlias = FunctionCallCreateParam
"""Alias for the FunctionCall (create param)."""

OCIGenAIFunctionDefinitionParam: TypeAlias = FunctionDefinitionParam
"""Alias for the FunctionDefinition (param)."""

OCIGenAIResponseFormatCreateParam: TypeAlias = ResponseFormatCreateParam
"""Alias for the ResponseFormatCreateParam (create param)."""

OCIGenAIChatCompletionMessageToolCallModel: TypeAlias = ChatCompletionMessageToolCallModel
"""Alias for the ChatCompletionMessageToolCall (base model)."""

OCIGenAIChatCompletionToolParam: TypeAlias = ChatCompletionToolParam
"""Alias for the ChatCompletionToolParam (param)."""

OCIGenAIChatCompletionMessageToolCallParam: TypeAlias = ChatCompletionMessageToolCallParam
"""Alias for the ChatCompletionMessageToolCallParam (param)."""

OCIGenAIChatCompletionToolChoiceOptionParam: TypeAlias = (
    ChatCompletionToolChoiceOptionParam
)
"""Alias for the ChatCompletionToolChoiceOptionParam (param)."""


# NOTE:
# This is done to avoid using an Iterator for the `tool_calls`,
# which when combined with pydantic will result in a generator that
# can only be iterated once
class _ChatCompletionAssistantMessageParam(TypedDict, total=False):
    """Shadow ChatCompletionAssistantMessageParam from OCIGenAI."""

    role: Required[Literal["assistant"]]
    """The role of the messages author, in this case `assistant`."""

    content: str | None
    """The contents of the assistant message.

    Required unless `tool_calls` or `function_call` is specified.
    """

    function_call: OCIGenAIFunctionCallParam | None
    """Deprecated and replaced by `tool_calls`.

    The name and arguments of a function that should be called, as generated by the
    model.
    """

    name: str
    """An optional name for the participant.

    Provides the model information to differentiate between participants of the same
    role.
    """

    tool_calls: Sequence[OCIGenAIChatCompletionMessageToolCallParam]
    """The tool calls generated by the model, such as function calls."""


OCIGenAIChatCompletionSystemMessageParam: TypeAlias = ChatCompletionSystemMessageParam
"""Alias for the ChatCompletionSystemMessageParam (param)."""

OCIGenAIChatCompletionUserMessageParam: TypeAlias = ChatCompletionUserMessageParam
"""Alias for the ChatCompletionUserMessageParam (param)."""

OCIGenAIChatCompletionAssistantMessageParam: TypeAlias = (
    _ChatCompletionAssistantMessageParam
)
"""Alias for the ChatCompletionAssistantMessageParam (param)."""

OCIGenAIChatCompletionToolMessageParam: TypeAlias = ChatCompletionToolMessageParam
"""Alias for the ChatCompletionToolMessageParam (param)."""

OCIGenAIChatCompletionFunctionMessageParam: TypeAlias = ChatCompletionFunctionMessageParam
"""Alias for the ChatCompletionFunctionMessageParam (param)."""

OCIGenAIChatCompletionMessageParam: TypeAlias = (
        OCIGenAIChatCompletionSystemMessageParam
        | OCIGenAIChatCompletionUserMessageParam
        | OCIGenAIChatCompletionAssistantMessageParam
        | OCIGenAIChatCompletionToolMessageParam
        | OCIGenAIChatCompletionFunctionMessageParam
)
"""OCIGenAI possible chat completion message types (param)."""

OCIGenAICreateEmbeddingResponseModel: TypeAlias = CreateEmbeddingResponseModel
"""Alias for the CreateEmbeddingResponse (base model)."""

OCIGenAIEmbeddingModel: TypeAlias = EmbeddingModel
"""Alias for the Embedding (base model)."""

OCIGenAIEmbeddingUsageModel: TypeAlias = EmbeddingUsageModel
"""Alias for the EmbeddingUsage (base model)."""
