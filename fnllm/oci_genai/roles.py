# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI specific roles."""

from collections.abc import Sequence
from string import Template
from typing import Any, Final

from fnllm.oci_genai.types.aliases import (
    OCIGenAIChatCompletionAssistantMessageParam,
    OCIGenAIChatCompletionFunctionMessageParam,
    OCIGenAIChatCompletionMessageToolCallParam,
    OCIGenAIChatCompletionSystemMessageParam,
    OCIGenAIChatCompletionToolMessageParam,
    OCIGenAIChatCompletionUserMessageParam,
    OCIGenAIFunctionCallParam,
)


class _OCIGenAIBaseRole:
    """OCIGenAI base class for roles."""

    role = "user"

    def _substitute_template(
            self, value: str | Template, variables: dict[str, Any] | None
    ) -> str:
        if isinstance(value, Template):
            return value.substitute(**(variables or {}))

        if variables:
            return Template(value).substitute(**variables)

        return value

    def __str__(self) -> str:
        """String representation of the role."""
        return self.role

    def __hash__(self) -> int:
        """Hash representation of the role."""
        return hash(self.role)


class _OCIGenAISystemRole(_OCIGenAIBaseRole):
    """OCIGenAI system role."""

    role: Final = "system"

    def message(
            self,
            content: str | Template,
            *,
            name: str | None = None,
            variables: dict[str, Any] | None = None,
    ) -> OCIGenAIChatCompletionSystemMessageParam:
        """Create a message for the given role."""
        msg = OCIGenAIChatCompletionSystemMessageParam(
            content=self._substitute_template(content, variables), role=self.role
        )

        if name is not None:
            msg["name"] = name

        return msg


class _OCIGenAIUserRole(_OCIGenAIBaseRole):
    """OCIGenAI user role."""

    role: Final = "user"

    def message(
            self,
            content: str | Template,
            *,
            name: str | None = None,
            variables: dict[str, Any] | None = None,
    ) -> OCIGenAIChatCompletionUserMessageParam:
        """Create a message for the given role."""
        msg = OCIGenAIChatCompletionUserMessageParam(
            content=self._substitute_template(content, variables), role=self.role
        )

        if name is not None:
            msg["name"] = name

        return msg


class _OCIGenAIAssistantRole(_OCIGenAIBaseRole):
    """OCIGenAI assistant role."""

    role: Final = "assistant"

    def message(
            self,
            content: str | Template | None = None,
            *,
            tool_calls: Sequence[OCIGenAIChatCompletionMessageToolCallParam] | None = None,
            function_call: OCIGenAIFunctionCallParam | None = None,
            name: str | None = None,
            variables: dict[str, Any] | None = None,
    ) -> OCIGenAIChatCompletionAssistantMessageParam:
        """Create a message for the given role."""
        msg = OCIGenAIChatCompletionAssistantMessageParam(
            content=self._substitute_template(content, variables)
            if content is not None
            else None,
            role=self.role,
        )

        if tool_calls is not None:
            msg["tool_calls"] = tool_calls

        if function_call is not None:
            msg["function_call"] = function_call

        if name is not None:
            msg["name"] = name

        return msg


class _OCIGenAIToolRole(_OCIGenAIBaseRole):
    """OCIGenAI tool role."""

    role: Final = "tool"

    def message(
            self,
            content: str | Template,
            tool_call_id: str,
            *,
            variables: dict[str, Any] | None = None,
    ) -> OCIGenAIChatCompletionToolMessageParam:
        """Create a message for the given role."""
        return OCIGenAIChatCompletionToolMessageParam(
            content=self._substitute_template(content, variables),
            tool_call_id=tool_call_id,
            role=self.role,
        )


class _OCIGenAIFunctionRole(_OCIGenAIBaseRole):
    """OCIGenAI function role."""

    role: Final = "function"

    def message(
            self,
            content: str | Template,
            name: str,
            *,
            variables: dict[str, Any] | None = None,
    ) -> OCIGenAIChatCompletionFunctionMessageParam:
        """Create a message for the given role."""
        return OCIGenAIChatCompletionFunctionMessageParam(
            content=self._substitute_template(content, variables),
            name=name,
            role=self.role,
        )


class OCIGenAIChatRole:
    """OCIGenAI chat roles."""

    System: Final = _OCIGenAISystemRole()

    User: Final = _OCIGenAIUserRole()

    Assistant: Final = _OCIGenAIAssistantRole()

    Tool: Final = _OCIGenAIToolRole()

    Function: Final = _OCIGenAIFunctionRole()
