# Copyright (c) 2024 Microsoft Corporation.

"""TPM RPM limiter module."""

from __future__ import annotations

from aiolimiter import AsyncLimiter

from fnllm.limiting.base import Limiter, Manifest


class TPMLimiter(Limiter):
    """TPM limiter class definition."""

    def __init__(self, limiter: AsyncLimiter):
        """Create a new RpmLimiter."""
        print("fnllm/limiting/tpm.py TPMLimiter.__init__() start...")
        self._limiter = limiter
        print("fnllm/limiting/tpm.py TPMLimiter.__init__() end...")
        print()

    async def acquire(self, manifest: Manifest) -> None:
        """Acquire limiter permission."""
        print()
        print("fnllm/limiting/tpm.py TPMLimiter.acquire() start...")
        total_tokens = manifest.request_tokens + manifest.post_request_tokens
        print(f"fnllm/limiting/tpm.py TPMLimiter.acquire() {total_tokens=}")

        if total_tokens > 0:
            print(f"fnllm/limiting/tpm.py TPMLimiter.acquire() {total_tokens > 0=}")
            print(f"fnllm/limiting/tpm.py TPMLimiter.acquire() invoke self._limiter.acquire({total_tokens=}) start...")
            await self._limiter.acquire(total_tokens)
            print(f"fnllm/limiting/tpm.py TPMLimiter.acquire() invoke self._limiter.acquire({total_tokens=}) end...")
        print("fnllm/limiting/tpm.py TPMLimiter.acquire() end...")
        print()

    async def release(self, manifest: Manifest) -> None:
        """Do nothing."""
        print()
        print("fnllm/limiting/tpm.py TPMLimiter.release() start...")
        print("fnllm/limiting/tpm.py TPMLimiter.release() Do nothing....")
        print("fnllm/limiting/tpm.py TPMLimiter.release() end...")
        print()

    @classmethod
    def from_tpm(cls, tokens_per_minute: int) -> TPMLimiter:
        """Create a new RpmLimiter."""
        print()
        print("fnllm/limiting/tpm.py TPMLimiter.from_tpm() start...")
        print(f"fnllm/limiting/tpm.py TPMLimiter.from_tpm() return cls(AsyncLimiter({tokens_per_minute=}))...")
        return cls(AsyncLimiter(tokens_per_minute))
