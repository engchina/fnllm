# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI parsing utilities."""

from collections.abc import Iterable, Sequence
from typing import cast

from fnllm.oci_genai.types.aliases import (
    OCIGenAIChatCompletionAssistantMessageParam,
    OCIGenAIChatCompletionMessageModel,
    OCIGenAIChatCompletionMessageToolCallModel,
    OCIGenAIChatCompletionMessageToolCallParam,
    OCIGenAIChatCompletionToolParam,
    OCIGenAIChatCompletionUserMessageParam,
    OCIGenAIFunctionCallModel,
    OCIGenAIFunctionCallParam,
    OCIGenAIFunctionDefinitionParam,
    OCIGenAIFunctionModel,
    OCIGenAIFunctionParam,
)
from fnllm.oci_genai.types.chat.io import OCIGenAIChatCompletionInput, OCIGenAIChatHistoryEntry
from fnllm.tools.base import LLMTool


def function_call_to_param(
        func: OCIGenAIFunctionCallModel | None,
) -> OCIGenAIFunctionCallParam | None:
    """Parses FunctionCall base model to the equivalent typed dict."""
    if not func:
        return None

    return OCIGenAIFunctionCallParam(
        arguments=func.arguments,
        name=func.name,
    )


def function_to_param(func: OCIGenAIFunctionModel) -> OCIGenAIFunctionParam:
    """Parses Function base model to the equivalent typed dict."""
    return OCIGenAIFunctionParam(arguments=func.arguments, name=func.name)


def tool_calls_to_params(
        tools: list[OCIGenAIChatCompletionMessageToolCallModel] | None,
) -> Sequence[OCIGenAIChatCompletionMessageToolCallParam] | None:
    """Parses a list of ChatCompletionMessageToolCall base model to the equivalent typed dict."""
    if not tools:
        return None

    return [
        OCIGenAIChatCompletionMessageToolCallParam(
            id=tool.id, function=function_to_param(tool.function), type=tool.type
        )
        for tool in tools
    ]


def llm_tool_to_param(tool: type[LLMTool]) -> OCIGenAIFunctionDefinitionParam:
    """Parses a class that implements LLMTool to the equivalent typed dict."""
    return OCIGenAIFunctionDefinitionParam(
        name=tool.get_name(),
        description=tool.get_description(),
        parameters=tool.get_parameters_schema(),
    )


def llm_tools_to_param(
        tools: Sequence[type[LLMTool]],
) -> Iterable[OCIGenAIChatCompletionToolParam]:
    """Parses a list of classes that implements LLMTool to the equivalent typed dicts."""
    return [
        OCIGenAIChatCompletionToolParam(
            function=llm_tool_to_param(tool),
            type="function",
        )
        for tool in tools
    ]


def chat_completion_message_to_param(
        message: OCIGenAIChatCompletionMessageModel,
) -> OCIGenAIChatCompletionAssistantMessageParam:
    """Parses ChatCompletionMessage base model to the equivalent typed dict."""
    param = OCIGenAIChatCompletionAssistantMessageParam(
        # role=message.role, content=message.content
        role="assistant", content=message.content
    )

    # function_call = function_call_to_param(message.function_call)
    #
    # if function_call:
    #     param["function_call"] = function_call

    # print(f"{message=}")
    if 'tool_calls' in message:
        tool_calls = tool_calls_to_params(message.tool_calls)

        if tool_calls:
            param["tool_calls"] = tool_calls

    return param


def build_chat_messages(
        prompt: OCIGenAIChatCompletionInput,
        history: Sequence[OCIGenAIChatHistoryEntry],
) -> tuple[list[OCIGenAIChatHistoryEntry], OCIGenAIChatHistoryEntry]:
    """Builds a chat history list from the prompt and existing history, along with the prompt message."""
    if isinstance(prompt, str):
        prompt = OCIGenAIChatCompletionUserMessageParam(
            content=prompt,
            role="user",
        )
    messages = [*history]
    if prompt is not None:
        messages.append(prompt)
    return messages, cast(OCIGenAIChatHistoryEntry, prompt)
