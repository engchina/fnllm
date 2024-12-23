# Copyright (c) 2024 Microsoft Corporation.

"""LLM tools parsing module for OCIGenAI."""

from collections.abc import Sequence

import pydantic
from typing_extensions import Unpack

from fnllm.oci_genai.llm.utils import llm_tools_to_param
from fnllm.oci_genai.types.aliases import (
    OCIGenAIChatCompletionMessageModel,
    OCIGenAIChatCompletionMessageToolCallModel,
)
from fnllm.oci_genai.types.chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatOutput,
)
from fnllm.oci_genai.types.chat.parameters import OCIGenAIChatParameters
from fnllm.tools import LLMTool
# from fnllm.tools.errors import OCIGenAIToolNotFoundError, OCIGenAIToolInvalidArgumentsError
from fnllm.types.generics import TJsonModel
from fnllm.types.io import LLMInput, LLMOutput
from fnllm.types.protocol import LLM


class OCIGenAIParseToolsLLM(
    LLM[
        OCIGenAIChatCompletionInput,
        OCIGenAIChatOutput,
        OCIGenAIChatHistoryEntry,
        OCIGenAIChatParameters,
    ],
):
    """An OCIGenAI tools parsing LLM."""

    def __init__(
            self,
            delegate: LLM[
                OCIGenAIChatCompletionInput,
                OCIGenAIChatOutput,
                OCIGenAIChatHistoryEntry,
                OCIGenAIChatParameters,
            ],
    ):
        """Create a new OCIGenAIParseToolsLLM."""
        self._delegate = delegate

    def child(self, name: str) -> "OCIGenAIParseToolsLLM":
        """Create a child LLM (with child cache)."""
        return OCIGenAIParseToolsLLM(self._delegate.child(name))

    def _add_tools_to_parameters(
            self,
            parameters: LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters],
            tools: Sequence[type[LLMTool]],
    ) -> LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]:
        new_parameters = parameters.copy()

        new_parameters["model_parameters"] = new_parameters.get("model_parameters", {})
        new_parameters["model_parameters"]["tools"] = llm_tools_to_param(tools)

        return new_parameters

    def _parse_arguments(
            self,
            tool_call: OCIGenAIChatCompletionMessageToolCallModel,
            *,
            json_model: type[LLMTool],
            raw_output: OCIGenAIChatCompletionMessageModel,
    ) -> LLMTool:
        try:
            return json_model.model_validate_json(tool_call.function.arguments)
        except pydantic.ValidationError as err:
            # TODO: Add a better error message
            # raise OCIGenAIToolInvalidArgumentsError(
            #     raw_output,
            #     tool_call=tool_call,
            #     expected_tool=json_model,
            #     validation_error=err,
            # ) from err
            raise err

    def _parse_tool_calls(
            self,
            raw_output: OCIGenAIChatCompletionMessageModel,
            *,
            tools: Sequence[type[LLMTool]],
    ) -> list[LLMTool]:
        result = []
        tool_calls = raw_output.tool_calls or []

        for call in tool_calls:
            tool = LLMTool.find_tool(tools, call.function.name)

            if not tool:
                # TODO: Add a better error message
                # raise OCIGenAIToolNotFoundError(raw_output, tool_call=call)
                raise raw_output

            parsed_json = self._parse_arguments(
                call, json_model=tool, raw_output=raw_output
            )

            parsed_json.__raw_arguments_json__ = call.function.arguments
            parsed_json.call_id = call.id

            result.append(parsed_json)

        return result

    async def __call__(
            self,
            prompt: OCIGenAIChatCompletionInput,
            **kwargs: Unpack[
                LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters]
            ],
    ) -> LLMOutput[OCIGenAIChatOutput, TJsonModel, OCIGenAIChatHistoryEntry]:
        """Call the LLM."""
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
