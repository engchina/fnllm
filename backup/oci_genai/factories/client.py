# Copyright (c) 2024 Microsoft Corporation.

"""Create OCIGenAI client instance."""

from typing import cast

import oci
from oci.retry import NoneRetryStrategy

from fnllm.oci_genai.config import OCIGenAIConfig, PublicOCIGenAIConfig
from fnllm.oci_genai.types.client import OCIGenAIClient


def create_oci_genai_client(config: OCIGenAIConfig) -> OCIGenAIClient:
    """Create a new OCIGenAI client instance."""
    print("create_oci_genai_client() start...")

    config = cast(PublicOCIGenAIConfig, config)
    # print(f"{config=}")

    oci_config = oci.config.from_file('~/.oci/config', config.config_profile or "DEFAULT")

    client = oci.generative_ai_inference.GenerativeAiInferenceClient(
        config=oci_config,
        service_endpoint=config.endpoint,
        retry_strategy=NoneRetryStrategy(),
        timeout=(30, 240)
    )

    return client
