# Copyright (c) 2024 Microsoft Corporation.


"""OCIGenAI Configuration class definition."""

from typing import Annotated

from pydantic import Field

from fnllm.config import Config
from fnllm.oci_genai.types import OCIGenAIChatParameters


class CommonOCIGenAIConfig(Config, frozen=True, extra="allow", protected_namespaces=()):
    """Common configuration parameters between Azure OCIGenAI and Public OCIGenAI."""

    timeout: float | None = Field(default=None, description="The request timeout.")

    encoding: str = Field(default="cl100k_base", description="The encoding model.")

    track_stream_usage: bool = Field(
        default=False, description="Whether to emit stream usage."
    )

    chat_parameters: OCIGenAIChatParameters = Field(
        default_factory=dict,
        description="Global chat parameters to be used across calls.",
    )

    sleep_on_rate_limit_recommendation: bool = Field(
        default=False,
        description="Whether to sleep on rate limit recommendation.",
    )


class PublicOCIGenAIConfig(
    CommonOCIGenAIConfig, frozen=True, extra="allow", protected_namespaces=()
):
    """Public OCIGenAI configuration definition."""

    endpoint: str | None = Field(default=None, description="The OCI GenAI API endpoint.")

    config_profile: str | None = Field(default="DEFAULT", description="The OCI GenAI API profile.")


OCIGenAIConfig = Annotated[
    PublicOCIGenAIConfig, Field(discriminator="azure")
]
"""OCIGenAI configuration definition."""
