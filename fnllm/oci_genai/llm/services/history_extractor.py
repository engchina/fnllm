# Copyright (c) 2024 Microsoft Corporation.

"""LLM history tracking module for OCIGenAI."""

from collections.abc import Sequence

from fnllm.oci_genai.llm.utils import chat_completion_message_to_param
from fnllm.oci_genai.types import OCIGenAIChatCompletionAssistantMessageParam
from fnllm.oci_genai.types.chat.io import OCIGenAIChatHistoryEntry, OCIGenAIChatOutput
from fnllm.services.history_extractor import HistoryExtractor


class OCIGenAIHistoryExtractor(
    HistoryExtractor[OCIGenAIChatOutput, OCIGenAIChatHistoryEntry]
):
    """An OCIGenAI history-tracking LLM."""

    def extract_history(
            self,
            history: Sequence[OCIGenAIChatHistoryEntry] | None,
            output: OCIGenAIChatOutput,
    ) -> list[OCIGenAIChatHistoryEntry]:
        """Call the LLM."""
        print("history_extractor.py OCIGenAIHistoryExtractor.extract_history() start...")
        # print(f"{output=}")
        result = [*history] if history else []
        # print(f"{result=}")

        if output.raw_input is not None:
            param = OCIGenAIChatCompletionAssistantMessageParam(
                # role=message.role, content=message.content
                role="USER", content=output.raw_input
            )
            result.append(param)

        result.append(chat_completion_message_to_param(output))

        return result
