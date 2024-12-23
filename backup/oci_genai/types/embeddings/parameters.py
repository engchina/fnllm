# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI embeddings parameters types."""

from typing_extensions import NotRequired, TypedDict


class OCIGenAIEmbeddingsParameters(TypedDict):
    """OCIGenAI allowed embeddings parameters."""

    model_id: NotRequired[str]

    compartment_id: NotRequired[str]
