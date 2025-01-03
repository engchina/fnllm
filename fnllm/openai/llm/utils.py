# Copyright (c) 2024 Microsoft Corporation.

"""OpenAI parsing utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fnllm.openai.types.aliases import (
    OpenAIChatCompletionAssistantMessageParam,
    OpenAIChatCompletionMessageModel,
    OpenAIChatCompletionMessageToolCallModel,
    OpenAIChatCompletionMessageToolCallParam,
    OpenAIChatCompletionToolParam,
    OpenAIChatCompletionUserMessageParam,
    OpenAIFunctionCallModel,
    OpenAIFunctionCallParam,
    OpenAIFunctionDefinitionParam,
    OpenAIFunctionModel,
    OpenAIFunctionParam,
)
from fnllm.openai.types.chat.io import OpenAIChatCompletionInput, OpenAIChatHistoryEntry

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from fnllm.tools.base import LLMTool


def function_call_to_param(
        func: OpenAIFunctionCallModel | None,
) -> OpenAIFunctionCallParam | None:
    """Parses FunctionCall base model to the equivalent typed dict."""
    print("function_call_to_param() start...")
    print(f"{func=}")
    if not func:
        return None

    return OpenAIFunctionCallParam(
        arguments=func.arguments,
        name=func.name,
    )


def function_to_param(func: OpenAIFunctionModel) -> OpenAIFunctionParam:
    """Parses Function base model to the equivalent typed dict."""
    return OpenAIFunctionParam(arguments=func.arguments, name=func.name)


def tool_calls_to_params(
        tools: list[OpenAIChatCompletionMessageToolCallModel] | None,
) -> Sequence[OpenAIChatCompletionMessageToolCallParam] | None:
    """Parses a list of ChatCompletionMessageToolCall base model to the equivalent typed dict."""
    if not tools:
        return None

    return [
        OpenAIChatCompletionMessageToolCallParam(
            id=tool.id, function=function_to_param(tool.function), type=tool.type
        )
        for tool in tools
    ]


def llm_tool_to_param(tool: type[LLMTool]) -> OpenAIFunctionDefinitionParam:
    """Parses a class that implements LLMTool to the equivalent typed dict."""
    return OpenAIFunctionDefinitionParam(
        name=tool.get_name(),
        description=tool.get_description(),
        parameters=tool.get_parameters_schema(),
    )


def llm_tools_to_param(
        tools: Sequence[type[LLMTool]],
) -> Iterable[OpenAIChatCompletionToolParam]:
    """Parses a list of classes that implements LLMTool to the equivalent typed dicts."""
    print()
    print("fnllm/openai/llm/utils.py llm_tools_to_param() start...")
    print("fnllm/openai/llm/utils.py llm_tools_to_param() return OpenAIChatCompletionToolParam()...")
    print()
    return [
        OpenAIChatCompletionToolParam(
            function=llm_tool_to_param(tool),
            type="function",
        )
        for tool in tools
    ]


def chat_completion_message_to_param(
        message: OpenAIChatCompletionMessageModel,
) -> OpenAIChatCompletionAssistantMessageParam:
    """Parses ChatCompletionMessage base model to the equivalent typed dict."""
    print("fnllm/openai/llm/utils.py chat_completion_message_to_param() start...")
    print(f"{message=}")
    param = OpenAIChatCompletionAssistantMessageParam(
        role=message.role, content=message.content
    )

    function_call = function_call_to_param(message.function_call)

    if function_call:
        param["function_call"] = function_call

    tool_calls = tool_calls_to_params(message.tool_calls)

    if tool_calls:
        param["tool_calls"] = tool_calls

    return param


def build_chat_messages(
        prompt: OpenAIChatCompletionInput,
        history: Sequence[OpenAIChatHistoryEntry],
) -> tuple[list[OpenAIChatHistoryEntry], OpenAIChatHistoryEntry]:
    """Builds a chat history list from the prompt and existing history, along with the prompt message."""
    print()
    print("fnllm/openai/llm/utils.py build_chat_messages() start...")
    if isinstance(prompt, str):
        prompt = OpenAIChatCompletionUserMessageParam(
            content=prompt,
            role="user",
        )
    messages = [*history]
    if prompt is not None:
        messages.append(prompt)

    print("fnllm/openai/llm/utils.py build_chat_messages() return messages, cast(OpenAIChatHistoryEntry, prompt)...")
    print()
    return messages, cast(OpenAIChatHistoryEntry, prompt)
