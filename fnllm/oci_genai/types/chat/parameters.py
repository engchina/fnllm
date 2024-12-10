# Copyright (c) 2024 Microsoft Corporation.

"""OCIGenAI chat parameters types."""

from typing_extensions import NotRequired, TypedDict


#
# Note: streaming options have been removed from this class to avoid downstream tying issues.
# OCIGenAI streaming should be handled with a StreamingLLM, not additional client-side parameters.
#
class OCIGenAIChatParameters(TypedDict):
    """OCIGenAI allowed chat parameters."""
    compartment_id: NotRequired[str | None]

    model_id: NotRequired[str | None]

    max_tokens: NotRequired[int | None]

    temperature: NotRequired[float | None]

    frequency_penalty: NotRequired[float | None]

    top_p: NotRequired[float | None]

    top_k: NotRequired[float | None]

    is_echo: NotRequired[bool | None]

    is_raw_prompting: NotRequired[bool | None]
