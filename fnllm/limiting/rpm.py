# Copyright (c) 2024 Microsoft Corporation.

"""TPM RPM limiter module."""
from datetime import datetime

from aiolimiter import AsyncLimiter

from fnllm.limiting.base import Limiter, Manifest


class RPMLimiter(Limiter):
    """RPM limiter class definition."""

    def __init__(self, limiter: AsyncLimiter):
        """Create a new RPMLimiter."""
        print("fnllm/limiting/rpm.py RPMLimiter.__init__() start...")
        self._limiter = limiter
        print("fnllm/limiting/rpm.py RPMLimiter.__init__() end...")
        print()

    async def acquire(self, manifest: Manifest) -> None:
        """Acquire a new request."""
        print()
        print("fnllm/limiting/rpm.py RPMLimiter.acquire() start...")
        print(f"fnllm/limiting/rpm.py RPMLimiter.acquire() {self._limiter=}")
        print(f"fnllm/limiting/rpm.py RPMLimiter.acquire() {manifest=}")
        print(f"fnllm/limiting/rpm.py RPMLimiter.acquire() {manifest.request_tokens > 0=}")
        # print(f"fnllm/limiting/rpm.py RPMLimiter.acquire() {self._limiter.has_capacity()=}")

        if manifest.request_tokens > 0:
            start_time = datetime.now()
            print(
                f"fnllm/limiting/rpm.py RPMLimiter.acquire() at {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} start...")

            await self._limiter.acquire()
            end_time = datetime.now()
            print(
                f"fnllm/limiting/rpm.py RPMLimiter.acquire() at {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} end...")

            elapsed_time = (end_time - start_time).total_seconds()
            print(
                f"fnllm/limiting/rpm.py RPMLimiter.acquire() executed at {elapsed_time:>5.3f} seconds")

        # await self._limiter.acquire()
        print("fnllm/limiting/rpm.py RPMLimiter.acquire() end...")
        print()

    async def release(self, manifest: Manifest) -> None:
        """Do nothing."""
        print()
        print("fnllm/limiting/rpm.py RPMLimiter.release() start...")
        print("fnllm/limiting/rpm.py RPMLimiter.release() Do nothing.")
        print("fnllm/limiting/rpm.py RPMLimiter.release() end...")
        print()

    @classmethod
    def from_rpm(
            cls, requests_per_minute: int, burst_mode: bool = True
    ) -> "RPMLimiter":
        """Create a new RPMLimiter."""
        print()
        print("fnllm/limiting/rpm.py RPMLimiter.from_rpm() start...")
        print(f"fnllm/limiting/rpm.py RPMLimiter.from_rpm() {requests_per_minute=}")
        print(f"fnllm/limiting/rpm.py RPMLimiter.from_rpm() {burst_mode=}")
        if burst_mode:
            print(
                f"fnllm/limiting/rpm.py RPMLimiter.from_rpm() return cls(AsyncLimiter({requests_per_minute}, time_period=60)...")
            return cls(AsyncLimiter(requests_per_minute, time_period=60))

        print(
            f"fnllm/limiting/rpm.py RPMLimiter.from_rpm() return cls(AsyncLimiter(1, time_period=60 / {requests_per_minute})...")
        return cls(AsyncLimiter(1, time_period=60 / requests_per_minute))
