# Copyright (c) 2024 Microsoft Corporation.

"""LLM tools parsing module for OpenAI."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic
from typing_extensions import Unpack

from fnllm.openai.llm.utils import llm_tools_to_param
from fnllm.openai.types.chat.io import (
    OpenAIChatCompletionInput,
    OpenAIChatHistoryEntry,
    OpenAIChatOutput,
)
from fnllm.openai.types.chat.parameters import OpenAIChatParameters
from fnllm.tools import LLMTool
from fnllm.tools.errors import ToolInvalidArgumentsError
from fnllm.types.protocol import LLM

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fnllm.openai.types.aliases import (
        OpenAIChatCompletionMessageModel,
        OpenAIChatCompletionMessageToolCallModel,
    )
    from fnllm.types.generics import TJsonModel
    from fnllm.types.io import LLMInput, LLMOutput


class OpenAIParseToolsLLM(
    LLM[
        OpenAIChatCompletionInput,
        OpenAIChatOutput,
        OpenAIChatHistoryEntry,
        OpenAIChatParameters,
    ],
):
    """An OpenAI tools parsing LLM."""

    def __init__(
            self,
            delegate: LLM[
                OpenAIChatCompletionInput,
                OpenAIChatOutput,
                OpenAIChatHistoryEntry,
                OpenAIChatParameters,
            ],
    ):
        """Create a new OpenAIParseToolsLLM."""
        print()
        print("fnllm/openai/llm/features/tools_parsing.py OpenAIParseToolsLLM.__init__() start...")
        self._delegate = delegate
        print("fnllm/openai/llm/features/tools_parsing.py OpenAIParseToolsLLM.__init__() end...")
        print()

    def child(self, name: str) -> "OpenAIParseToolsLLM":
        """Create a child LLM (with child cache)."""
        return OpenAIParseToolsLLM(self._delegate.child(name))

    def _add_tools_to_parameters(
            self,
            parameters: LLMInput[TJsonModel, OpenAIChatHistoryEntry, OpenAIChatParameters],
            tools: Sequence[type[LLMTool]],
    ) -> LLMInput[TJsonModel, OpenAIChatHistoryEntry, OpenAIChatParameters]:
        print("tools_parsing.py _add_tools_to_parameters() start...")
        new_parameters = parameters.copy()

        new_parameters["model_parameters"] = new_parameters.get("model_parameters", {})
        new_parameters["model_parameters"]["tools"] = llm_tools_to_param(tools)

        return new_parameters

    def _parse_arguments(
            self,
            tool_call: OpenAIChatCompletionMessageToolCallModel,
            *,
            json_model: type[LLMTool],
            raw_output: OpenAIChatCompletionMessageModel,
    ) -> LLMTool:
        print("fnllm/openai/llm/features/tools_parsing.py _parse_arguments.__init__() start...")
        try:
            print("fnllm/openai/llm/features/tools_parsing.py _parse_arguments.__init__() end...")
            print(
                "fnllm/openai/llm/features/tools_parsing.py _parse_arguments.__init__() return json_model.model_validate_json()...")
            return json_model.model_validate_json(tool_call.function.arguments)
        except pydantic.ValidationError as err:
            raise ToolInvalidArgumentsError(
                raw_output,
                tool_call=tool_call,
                expected_tool=json_model,
                validation_error=err,
            ) from err

    def _parse_tool_calls(
            self,
            raw_output: OpenAIChatCompletionMessageModel,
            *,
            tools: Sequence[type[LLMTool]],
    ) -> list[LLMTool]:
        print("tools_parsing.py _parse_tool_calls() start...")
        result = []
        tool_calls = raw_output.tool_calls or []

        for call in tool_calls:
            tool = LLMTool.find_tool(tools, call.function.name)

            if not tool:
                raise OpenAIToolNotFoundError(raw_output, tool_call=call)

            parsed_json = self._parse_arguments(
                call, json_model=tool, raw_output=raw_output
            )

            parsed_json.__raw_arguments_json__ = call.function.arguments
            parsed_json.call_id = call.id

            result.append(parsed_json)

        return result

    async def __call__(
            self,
            prompt: OpenAIChatCompletionInput,
            **kwargs: Unpack[
                LLMInput[TJsonModel, OpenAIChatHistoryEntry, OpenAIChatParameters]
            ],
    ) -> LLMOutput[OpenAIChatOutput, TJsonModel, OpenAIChatHistoryEntry]:
        """Call the LLM."""
        print("tools_parsing.py __call__() start...")
        tools = kwargs.get("tools", [])

        if not tools:
            return await self._delegate(prompt, **kwargs)

        completion_parameters = self._add_tools_to_parameters(kwargs, tools)

        result = await self._delegate(prompt, **completion_parameters)

        result.tool_calls = self._parse_tool_calls(
            result.output.raw_output,
            tools=tools,
        )

        return result
