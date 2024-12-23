# Copyright (c) 2024 Microsoft Corporation.

"""Base LLM module."""

from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic

from typing_extensions import Unpack

from fnllm.events.base import LLMEvents
from fnllm.types.generics import (
    THistoryEntry,
    TInput,
    TJsonModel,
    TModelParameters,
    TOutput,
)
from fnllm.types.io import LLMInput, LLMOutput
from fnllm.types.metrics import LLMUsageMetrics
from fnllm.types.protocol import LLM

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fnllm.caching.base import Cache
    from fnllm.services.decorator import LLMDecorator
    from fnllm.services.history_extractor import HistoryExtractor
    from fnllm.services.json import JsonHandler
    from fnllm.services.rate_limiter import RateLimiter
    from fnllm.services.retryer import Retryer
    from fnllm.services.usage_extractor import UsageExtractor
    from fnllm.services.variable_injector import VariableInjector


class BaseLLM(
    ABC,
    LLM[TInput, TOutput, THistoryEntry, TModelParameters],
    Generic[TInput, TOutput, THistoryEntry, TModelParameters],
):
    """Base LLM interface definition."""

    def __init__(
            self,
            *,
            events: LLMEvents | None = None,
            cache: Cache | None = None,
            usage_extractor: UsageExtractor[TOutput] | None = None,
            history_extractor: HistoryExtractor[TOutput, THistoryEntry] | None = None,
            variable_injector: VariableInjector | None = None,
            rate_limiter: RateLimiter[TInput, TOutput, THistoryEntry, TModelParameters]
                          | None = None,
            retryer: Retryer[TInput, TOutput, THistoryEntry, TModelParameters]
                     | None = None,
            json_handler: JsonHandler[TOutput, THistoryEntry] | None = None,
    ) -> None:
        """Base constructor for the BaseLLM."""
        print("fnllm/base/base.py BaseLLM.__init__() start...")
        self._events = events or LLMEvents()
        self._cache = cache
        self._usage_extractor = usage_extractor
        self._history_extractor = history_extractor
        self._variable_injector = variable_injector
        self._rate_limiter = rate_limiter
        self._retryer = retryer
        self._json_handler = json_handler

        decorated = self._decorator_target
        print(f"fnllm/base/base.py BaseLLM.__init__() {decorated=}")
        print(f"fnllm/base/base.py BaseLLM.__init__() {self.decorators=}")
        print(f"fnllm/base/base.py BaseLLM.__init__() run `for decorator in self.decorators` start...")
        for decorator in self.decorators:
            print(f"fnllm/base/base.py BaseLLM.__init__() invoke decorator.decorate({decorator=}) start")
            decorated = decorator.decorate(decorated)
            print(f"fnllm/base/base.py BaseLLM.__init__() {decorated=}")
            print(f"fnllm/base/base.py BaseLLM.__init__() invoke decorator.decorate({decorator=}) end")
        print(f"fnllm/base/base.py BaseLLM.__init__() run `for decorator in self.decorators` end...")
        self._decorated_target = decorated
        print(f"fnllm/base/base.py BaseLLM.__init__() {self._decorated_target=}")
        print("fnllm/base/base.py BaseLLM.__init__() end...")

    def child(
            self, name: str
    ) -> BaseLLM[TInput, TOutput, THistoryEntry, TModelParameters]:
        """Create a child LLM."""
        print("fnllm/base/base.py BaseLLM.child() start...")
        if self._cache is None:
            return self
        return self.__class__(
            events=self._events,
            cache=self._cache.child(name),
            usage_extractor=self._usage_extractor,
            history_extractor=self._history_extractor,
            variable_injector=self._variable_injector,
            rate_limiter=self._rate_limiter,
            retryer=self._retryer,
            json_handler=self._json_handler,
        )

    @property
    def events(self) -> LLMEvents:
        """Registered LLM events handler."""
        print("fnllm/base/base.py BaseLLM.events() start...")
        return self._events

    @property
    def decorators(self) -> list[LLMDecorator[TOutput, THistoryEntry]]:
        """Get the list of LLM decorators."""
        print()
        print("fnllm/base/base.py BaseLLM.decorators() start...")
        decorators: list[LLMDecorator] = []
        if self._json_handler and self._json_handler.requester:
            decorators.append(self._json_handler.requester)
        if self._rate_limiter:
            decorators.append(self._rate_limiter)
        if self._retryer:
            decorators.append(self._retryer)
        if self._json_handler and self._json_handler.receiver:
            decorators.append(self._json_handler.receiver)
        print(f"fnllm/base/base.py BaseLLM.decorators() return {decorators=}")
        print()

        return decorators

    async def __call__(
            self,
            prompt: TInput,
            **kwargs: Unpack[LLMInput[TJsonModel, THistoryEntry, TModelParameters]],
    ) -> LLMOutput[TOutput, TJsonModel, THistoryEntry]:
        """Invoke the LLM."""
        print()
        print("fnllm/base/base.py BaseLLM.__call__() start...")
        print(f"fnllm/base/base.py BaseLLM.__call__() {prompt=}")
        print(f"fnllm/base/base.py BaseLLM.__call__() {kwargs=}")
        try:
            print(f"fnllm/base/base.py BaseLLM.__call__() return self._invoke(prompt, **kwargs)")
            return await self._invoke(prompt, **kwargs)
        except BaseException as e:
            stack_trace = traceback.format_exc()
            if self._events:
                await self._events.on_error(
                    e, stack_trace, {"prompt": prompt, "kwargs": kwargs}
                )
            raise

    async def _invoke(
            self,
            prompt: TInput,
            **kwargs: Unpack[LLMInput[TJsonModel, THistoryEntry, TModelParameters]],
    ) -> LLMOutput[TOutput, TJsonModel, THistoryEntry]:
        """Run the LLM invocation, returning an LLMOutput."""
        print("fnllm/base/base.py BaseLLM._invoke() start...")
        print(f"fnllm/base/base.py BaseLLM._invoke() {prompt=}")
        print(f"fnllm/base/base.py BaseLLM._invoke() {kwargs=}")
        print(f"fnllm/base/base.py BaseLLM._invoke() invoke self._rewrite_input(prompt, kwargs) start...")
        prompt, kwargs = self._rewrite_input(prompt, kwargs)
        print(f"fnllm/base/base.py BaseLLM._invoke() {prompt=}")
        print(f"fnllm/base/base.py BaseLLM._invoke() {kwargs=}")
        print(f"fnllm/base/base.py BaseLLM._invoke() {self._decorated_target=}")
        print("fnllm/base/base.py BaseLLM._invoke() return self._decorated_target(prompt, **kwargs)...")
        return await self._decorated_target(prompt, **kwargs)

    def _rewrite_input(
            self,
            prompt: TInput,
            kwargs: LLMInput[TJsonModel, THistoryEntry, TModelParameters],
    ) -> tuple[TInput, LLMInput[TJsonModel, THistoryEntry, TModelParameters]]:
        """Rewrite the input prompt and arguments.."""
        print("fnllm/base/base.py BaseLLM._rewrite_input() start...")
        print(f"fnllm/base/base.py BaseLLM._rewrite_input() {prompt=}")
        print(f"fnllm/base/base.py BaseLLM._rewrite_input() {kwargs=}")
        print(f"fnllm/base/base.py BaseLLM._rewrite_input() {self._variable_injector=}")
        if self._variable_injector:
            prompt = self._variable_injector.inject_variables(
                prompt, kwargs.get("variables")
            )
        print(f"fnllm/base/base.py BaseLLM._rewrite_input() return {prompt=}, {kwargs=}...")
        return prompt, kwargs

    async def _decorator_target(
            self,
            prompt: TInput,
            **kwargs: Unpack[LLMInput[TJsonModel, THistoryEntry, TModelParameters]],
    ) -> LLMOutput[TOutput, TJsonModel, THistoryEntry]:
        """Target for the decorator chain.

        Leave signature alone as prompt, **kwargs.
        """
        print("fnllm/base/base.py BaseLLM._decorator_target() start...")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() {prompt=}")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() {kwargs=}")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() {self._events=}")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._events.on_execute_llm() start...")
        await self._events.on_execute_llm()
        print(f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._events.on_execute_llm() end...")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._execute_llm(prompt, **kwargs) start...")
        output = await self._execute_llm(prompt, **kwargs)
        print(f"fnllm/base/base.py BaseLLM._decorator_target() {output=}")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._execute_llm(prompt, **kwargs) end...")
        result: LLMOutput[TOutput, TJsonModel, THistoryEntry] = LLMOutput(output=output)
        print(f"fnllm/base/base.py BaseLLM._decorator_target() {result=}")

        print(f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._inject_usage(result) start...")
        await self._inject_usage(result)
        print(f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._inject_usage(result) end...")

        print(
            f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._inject_history(result, kwargs.get('history')) start...")
        self._inject_history(result, kwargs.get("history"))
        print(
            f"fnllm/base/base.py BaseLLM._decorator_target() invoke self._inject_history(result, kwargs.get('history')) end...")
        print(f"fnllm/base/base.py BaseLLM._decorator_target() return {result=}...")

        return result

    async def _inject_usage(
            self, result: LLMOutput[TOutput, TJsonModel, THistoryEntry]
    ):
        print("fnllm/base/base.py BaseLLM._inject_usage() start...")
        print(f"fnllm/base/base.py BaseLLM._inject_usage() {result=}")
        usage = LLMUsageMetrics()
        print(f"fnllm/base/base.py BaseLLM._inject_usage() {self._usage_extractor=}")
        if self._usage_extractor:
            usage = self._usage_extractor.extract_usage(result.output)
            await self._events.on_usage(usage)
        result.metrics.usage = usage
        print("fnllm/base/base.py BaseLLM._inject_usage() end...")

    def _inject_history(
            self,
            result: LLMOutput[TOutput, TJsonModel, THistoryEntry],
            history: Sequence[THistoryEntry] | None,
    ) -> None:
        print("fnllm/base/base.py BaseLLM._inject_history() start...")
        if self._history_extractor:
            result.history = self._history_extractor.extract_history(
                history, result.output
            )
        print("fnllm/base/base.py BaseLLM._inject_history() end...")

    @abstractmethod
    async def _execute_llm(
            self,
            prompt: TInput,
            **kwargs: Unpack[LLMInput[TJsonModel, THistoryEntry, TModelParameters]],
    ) -> TOutput:
        ...
