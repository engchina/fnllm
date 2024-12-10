# Copyright (c) 2024 Microsoft Corporation.

"""Tool handling error definitions."""

from pydantic import ValidationError

# from fnllm.oci_genai.types import (
#     OCIGenAIChatCompletionMessageModel,
#     OCIGenAIChatCompletionMessageToolCallModel,
# )
from fnllm.openai.types.aliases import (
    OpenAIChatCompletionMessageModel,
    OpenAIChatCompletionMessageToolCallModel,
)
from .base import LLMTool


class OpenAIToolInvalidArgumentsError(RuntimeError):
    """Raise when a tool is called with invalid arguments."""

    def __init__(
            self,
            raw_output: OpenAIChatCompletionMessageModel,
            *,
            tool_call: OpenAIChatCompletionMessageToolCallModel,
            expected_tool: type[LLMTool],
            validation_error: ValidationError,
    ) -> None:
        """Init method definition."""
        self.raw_output = raw_output
        self.tool_call = tool_call
        self.expected_tool = expected_tool
        self.validation_error = validation_error

        super().__init__(
            f"JSON response for tool arguments does not match the expected schema, error={validation_error}."
        )


class OpenAIToolNotFoundError(RuntimeError):
    """LLM tried to call a tool that was not found."""

    def __init__(
            self,
            raw_output: OpenAIChatCompletionMessageModel,
            *,
            tool_call: OpenAIChatCompletionMessageToolCallModel,
    ) -> None:
        """Init method definition."""
        self.raw_output = raw_output
        self.tool_call = tool_call

        super().__init__(
            f"Requested tool '{tool_call.function.name}' by the LLM does not exist"
        )

# class OCIGenAIToolInvalidArgumentsError(RuntimeError):
#     """Raise when a tool is called with invalid arguments."""
#
#     def __init__(
#             self,
#             raw_output: OCIGenAIChatCompletionMessageModel,
#             *,
#             tool_call: OCIGenAIChatCompletionMessageToolCallModel,
#             expected_tool: type[LLMTool],
#             validation_error: ValidationError,
#     ) -> None:
#         """Init method definition."""
#         self.raw_output = raw_output
#         self.tool_call = tool_call
#         self.expected_tool = expected_tool
#         self.validation_error = validation_error
#
#         super().__init__(
#             f"JSON response for tool arguments does not match the expected schema, error={validation_error}."
#         )
#
#
# class OCIGenAIToolNotFoundError(RuntimeError):
#     """LLM tried to call a tool that was not found."""
#
#     def __init__(
#             self,
#             raw_output: OCIGenAIChatCompletionMessageModel,
#             *,
#             tool_call: OCIGenAIChatCompletionMessageToolCallModel,
#     ) -> None:
#         """Init method definition."""
#         self.raw_output = raw_output
#         self.tool_call = tool_call
#
#         super().__init__(
#             f"Requested tool '{tool_call.function.name}' by the LLM does not exist"
#         )
