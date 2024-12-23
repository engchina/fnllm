# Copyright (c) 2024 Microsoft Corporation.
"""OCIGenAI JSON Handler."""

from fnllm.config.json_strategy import JsonStrategy
from fnllm.oci_genai.types.chat.io import (
    OCIGenAIChatCompletionInput,
    OCIGenAIChatHistoryEntry,
    OCIGenAIChatOutput,
)
from fnllm.oci_genai.types.chat.parameters import OCIGenAIChatParameters
from fnllm.services.json import (
    JsonHandler,
    JsonMarshaler,
    JsonReceiver,
    JsonRequester,
    LooseModeJsonReceiver,
)
from fnllm.types.generics import TJsonModel
from fnllm.types.io import LLMInput, LLMOutput


def create_json_handler(
        strategy: JsonStrategy,
        max_retries: int,
) -> JsonHandler[OCIGenAIChatOutput, OCIGenAIChatHistoryEntry]:
    """Create a JSON handler for OCIGenAI."""
    marshaler = OCIGenAIJsonMarshaler()
    match strategy:
        case JsonStrategy.LOOSE:
            return JsonHandler(None, LooseModeJsonReceiver(marshaler, max_retries))
        case JsonStrategy.VALID:
            return JsonHandler(
                OCIGenAIJsonRequester(), JsonReceiver(marshaler, max_retries)
            )
        case JsonStrategy.STRUCTURED:
            raise NotImplementedError


class OCIGenAIJsonMarshaler(JsonMarshaler[OCIGenAIChatOutput, OCIGenAIChatHistoryEntry]):
    """An OCIGenAI JSON marshaler."""

    def inject_json_string(
            self,
            json_string: str | None,
            output: LLMOutput[OCIGenAIChatOutput, TJsonModel, OCIGenAIChatHistoryEntry],
    ) -> LLMOutput[OCIGenAIChatOutput, TJsonModel, OCIGenAIChatHistoryEntry]:
        """Inject the JSON string into the output."""
        output.output.content = json_string
        return output

    def extract_json_string(
            self, output: LLMOutput[OCIGenAIChatOutput, TJsonModel, OCIGenAIChatHistoryEntry]
    ) -> str | None:
        """Extract the JSON string from the output."""
        return output.output.content


class OCIGenAIJsonRequester(
    JsonRequester[
        OCIGenAIChatCompletionInput,
        OCIGenAIChatOutput,
        OCIGenAIChatHistoryEntry,
        OCIGenAIChatParameters,
    ]
):
    """An OCIGenAI JSON requester."""

    def rewrite_args(
            self,
            prompt: OCIGenAIChatCompletionInput,
            kwargs: LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters],
    ) -> tuple[
        OCIGenAIChatCompletionInput,
        LLMInput[TJsonModel, OCIGenAIChatHistoryEntry, OCIGenAIChatParameters],
    ]:
        """Rewrite the input prompt and arguments.."""
        kwargs["model_parameters"] = self._enable_oai_json_mode(
            kwargs.get("model_parameters", {})
        )
        return prompt, kwargs

    def _enable_oai_json_mode(
            self, parameters: OCIGenAIChatParameters
    ) -> OCIGenAIChatParameters:
        result: OCIGenAIChatParameters = parameters.copy()
        result["response_format"] = {"type": "json_object"}
        return result
