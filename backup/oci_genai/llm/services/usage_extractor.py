# Copyright (c) 2024 Microsoft Corporation.

"""LLM metrics parsing module for OCIGenAI."""

from typing import Generic, TypeVar

from fnllm.oci_genai.types.chat.io import OCIGenAIChatOutput
from fnllm.oci_genai.types.embeddings.io import OCIGenAIEmbeddingsOutput
from fnllm.services.usage_extractor import UsageExtractor
from fnllm.types.metrics import LLMUsageMetrics

TOutputWithUsageMetrics = TypeVar(
    "TOutputWithUsageMetrics", OCIGenAIChatOutput, OCIGenAIEmbeddingsOutput
)
"""Represents the support output types for usage metrics parsing."""


class OCIGenAIUsageExtractor(
    UsageExtractor[TOutputWithUsageMetrics],
    Generic[TOutputWithUsageMetrics],
):
    """An OCIGenAI usage metrics parsing LLM."""

    def extract_usage(self, output: TOutputWithUsageMetrics) -> LLMUsageMetrics:
        """Extract the LLM Usage from an OCIGenAI response."""
        return output.usage or LLMUsageMetrics()
