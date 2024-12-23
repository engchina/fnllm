# Copyright (c) 2024 Microsoft Corporation.

"""Composite limiter module."""

from collections.abc import Sequence

from .base import Limiter, Manifest


class CompositeLimiter(Limiter):
    """A composite limiter that combines multiple limiters."""

    def __init__(self, limiters: Sequence[Limiter]):
        """A composite limiter that combines multiple limiters."""
        print()
        print("fnllm/limiting/composite.py CompositeLimiter.__init__() start...")
        self._limiters = limiters
        self._acquire_order = limiters
        self._release_order = limiters[::-1]
        print("fnllm/limiting/composite.py CompositeLimiter.__init__() end...")
        print()

    async def acquire(self, manifest: Manifest) -> None:
        """Acquire the specified amount of tokens from all limiters."""
        # this needs to be sequential, the order of the limiters must be respected
        # to avoid deadlocks
        print()
        print("fnllm/limiting/composite.py CompositeLimiter.acquire() start...")
        print(f"fnllm/limiting/composite.py CompositeLimiter.acquire() {manifest=}")
        for limiter in self._acquire_order:
            print(f"fnllm/limiting/composite.py CompositeLimiter.acquire() {limiter=}")
            print(f"fnllm/limiting/composite.py CompositeLimiter.acquire() invoke {limiter} acquire() start...")
            await limiter.acquire(manifest)
            print(f"fnllm/limiting/composite.py CompositeLimiter.acquire() invoke {limiter} acquire() end...")

        print("fnllm/limiting/composite.py CompositeLimiter.acquire() end...")
        print()

    async def release(self, manifest: Manifest) -> None:
        """Release all tokens from all limiters."""
        # release in the opposite order we acquired
        # the last limiter acquired should be the first one released
        print()
        print("fnllm/limiting/composite.py CompositeLimiter.release() start...")
        for limiter in self._release_order:
            print(f"fnllm/limiting/composite.py CompositeLimiter.release() {limiter=}")
            print(f"fnllm/limiting/composite.py CompositeLimiter.release() invoke {limiter} release() start...")
            await limiter.release(manifest)
            print(f"fnllm/limiting/composite.py CompositeLimiter.release() invoke {limiter} release() end...")

        print("fnllm/limiting/composite.py CompositeLimiter.release() end...")
        print()
