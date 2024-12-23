# Copyright (c) 2024 Microsoft Corporation.
"""OpenAI JSON Handler."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fnllm.config.json_strategy import JsonStrategy
from fnllm.openai.types.chat.io import (
    OpenAIChatCompletionInput,
    OpenAIChatHistoryEntry,
    OpenAIChatOutput,
)
from fnllm.openai.types.chat.parameters import OpenAIChatParameters
from fnllm.services.json import (
    JsonHandler,
    JsonMarshaler,
    JsonReceiver,
    JsonRequester,
    LooseModeJsonReceiver,
)

if TYPE_CHECKING:
    from fnllm.types.generics import TJsonModel
    from fnllm.types.io import LLMInput, LLMOutput


def create_json_handler(
        strategy: JsonStrategy,
        max_retries: int,
) -> JsonHandler[OpenAIChatOutput, OpenAIChatHistoryEntry]:
    """Create a JSON handler for OpenAI."""
    print()
    print("fnllm/openai/llm/services/json.py create_json_handler() start...")
    print(f"fnllm/openai/llm/services/json.py create_json_handler() {strategy=}")
    print(f"fnllm/openai/llm/services/json.py create_json_handler() {max_retries=}")
    marshaler = OpenAIJsonMarshaler()
    print(f"fnllm/openai/llm/services/json.py create_json_handler() {marshaler=}")

    match strategy:
        case JsonStrategy.LOOSE:
            print(
                "fnllm/openai/llm/services/json.py create_json_handler() return JsonHandler(None, LooseModeJsonReceiver(marshaler, max_retries))...")
            print()
            return JsonHandler(None, LooseModeJsonReceiver(marshaler, max_retries))
        case JsonStrategy.VALID:
            print(
                "fnllm/openai/llm/services/json.py create_json_handler() return JsonHandler(OpenAIJsonRequester(), JsonReceiver(marshaler, max_retries))...")
            print()
            return JsonHandler(
                OpenAIJsonRequester(), JsonReceiver(marshaler, max_retries)
            )
        case JsonStrategy.STRUCTURED:
            raise NotImplementedError


class OpenAIJsonMarshaler(JsonMarshaler[OpenAIChatOutput, OpenAIChatHistoryEntry]):
    """An OpenAI JSON marshaler."""

    def inject_json_string(
            self,
            json_string: str | None,
            output: LLMOutput[OpenAIChatOutput, TJsonModel, OpenAIChatHistoryEntry],
    ) -> LLMOutput[OpenAIChatOutput, TJsonModel, OpenAIChatHistoryEntry]:
        """Inject the JSON string into the output."""
        print()
        print("fnllm/openai/llm/services/json.py inject_json_string() start...")
        output.output.content = json_string
        print(f"fnllm/openai/llm/services/json.py inject_json_string() return {output=}...")
        print()

        return output

    def extract_json_string(
            self, output: LLMOutput[OpenAIChatOutput, TJsonModel, OpenAIChatHistoryEntry]
    ) -> str | None:
        """Extract the JSON string from the output."""
        print()
        print("fnllm/openai/llm/services/json.py extract_json_string() start...")
        print(f"fnllm/openai/llm/services/json.py extract_json_string() return {output.output.content=}...")
        print()

        return output.output.content


class OpenAIJsonRequester(
    JsonRequester[
        OpenAIChatCompletionInput,
        OpenAIChatOutput,
        OpenAIChatHistoryEntry,
        OpenAIChatParameters,
    ]
):
    """An OpenAI JSON requester."""

    def rewrite_args(
            self,
            prompt: OpenAIChatCompletionInput,
            kwargs: LLMInput[TJsonModel, OpenAIChatHistoryEntry, OpenAIChatParameters],
    ) -> tuple[
        OpenAIChatCompletionInput,
        LLMInput[TJsonModel, OpenAIChatHistoryEntry, OpenAIChatParameters],
    ]:
        """Rewrite the input prompt and arguments.."""
        print()
        print("fnllm/openai/llm/services/json.py OpenAIJsonRequester.rewrite_args() start...")
        kwargs["model_parameters"] = self._enable_oai_json_mode(
            kwargs.get("model_parameters", {})
        )
        print(f"fnllm/openai/llm/services/json.py OpenAIJsonRequester.rewrite_args() return {prompt=}, {kwargs=}...")
        print()

        return prompt, kwargs

    def _enable_oai_json_mode(
            self, parameters: OpenAIChatParameters
    ) -> OpenAIChatParameters:
        print("fnllm/openai/llm/services/json.py OpenAIJsonRequester._enable_oai_json_mode() start...")
        result: OpenAIChatParameters = parameters.copy()
        result["response_format"] = {"type": "json_object"}
        print("fnllm/openai/llm/services/json.py OpenAIJsonRequester._enable_oai_json_mode() return {result=}...")

        return result
