# Copyright (c) 2024 Microsoft Corporation.

"""Concurrency limiter module."""

from __future__ import annotations

from asyncio import Semaphore

from fnllm.limiting.base import Limiter, Manifest


class ConcurrencyLimiter(Limiter):
    """Concurrency limiter class definition."""

    def __init__(self, semaphore: Semaphore):
        """Create a new ConcurrencyLimiter."""
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.__init__() start...")
        self._semaphore = semaphore
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.__init__() end...")

    async def acquire(self, manifest: Manifest) -> None:
        """Acquire a concurrency slot."""
        print()
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.acquire() start...")
        if manifest.request_tokens > 0:
            await self._semaphore.acquire()
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.acquire() end...")
        print()

    async def release(self, manifest: Manifest) -> None:
        """Release the concurrency slot."""
        print()
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.release() start...")
        print(f"fnllm/limiting/concurrency.py ConcurrencyLimiter.release() {manifest.request_tokens > 0=}...")
        if manifest.request_tokens > 0:
            print(
                "fnllm/limiting/concurrency.py ConcurrencyLimiter.release() invoke self._semaphore.release() start...")
            self._semaphore.release()
            print("fnllm/limiting/concurrency.py ConcurrencyLimiter.release() invoke self._semaphore.release() end...")

        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.release() end...")
        print()

    @classmethod
    def from_max_concurrency(cls, max_concurrency: int) -> ConcurrencyLimiter:
        """Create a new ConcurrencyLimiter."""
        print()
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.from_max_concurrency() start...")
        print("fnllm/limiting/concurrency.py ConcurrencyLimiter.from_max_concurrency() return cls(Semaphore())...")
        print()

        return cls(Semaphore(max_concurrency))
