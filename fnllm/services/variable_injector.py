# Copyright (c) 2024 Microsoft Corporation.

"""Generic LLM variables replacing module."""

from string import Template
from typing import TypeVar, cast

from fnllm.types import PromptVariables

TInput = TypeVar("TInput")


class VariableInjector:
    """An variables replacing LLM."""

    def inject_variables(
            self, prompt: TInput, variables: PromptVariables | None
    ) -> TInput:
        """Call the LLM."""
        print("fnllm/services/variable_injector.py VariableInjector.inject_variables() start...")
        print(f"fnllm/services/variable_injector.py {prompt=}")
        print(f"fnllm/services/variable_injector.py {variables=}")
        parsed_prompt = prompt

        if isinstance(parsed_prompt, str) and variables:
            parsed_prompt = Template(parsed_prompt).substitute(**variables)

        print("fnllm/services/variable_injector.py VariableInjector.inject_variables() return cast(TInput, parsed_prompt)...")
        return cast(TInput, parsed_prompt)
