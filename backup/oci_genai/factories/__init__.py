# Copyright (c) 2024 Microsoft Corporation.

"""Methods to create OCIGenAI instances."""

from .chat import create_oci_genai_chat_llm
from .client import create_oci_genai_client
from .embeddings import create_oci_genai_embeddings_llm

__all__ = [
    "create_oci_genai_chat_llm",
    "create_oci_genai_client",
    "create_oci_genai_embeddings_llm",
]
