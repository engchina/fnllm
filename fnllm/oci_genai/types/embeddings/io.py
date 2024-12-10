# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI embeddings input/output types."""

from typing import TypeAlias

from fnllm.oci_genai.types.aliases import OCIGenAIEmbeddingModel
from fnllm.oci_genai.types.chat.io import OCIGenAIEmbeddingsMessage
from fnllm.types.generalized import EmbeddingsLLMInput, EmbeddingsLLMOutput
from fnllm.types.metrics import LLMUsageMetrics

OCIGenAIEmbeddingsInput: TypeAlias = EmbeddingsLLMInput
"""Main input type for OCIGenAI embeddings."""


class OCIGenAIEmbeddingsOutput(EmbeddingsLLMOutput):
    """OCIGenAI embeddings completion output."""

    raw_input: OCIGenAIEmbeddingsInput | None
    """Raw input that resulted in this output."""

    raw_output: OCIGenAIEmbeddingsMessage | list[OCIGenAIEmbeddingModel]
    """Raw embeddings output from OCIGenAI."""

    usage: LLMUsageMetrics | None
    """Usage statistics for the embeddings request."""
