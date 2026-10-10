"""SG28 ASGI request-lifecycle bridge, tested without a public API route."""
import asyncio
import time

import pytest

from app.services.interruptible import ComputationCancelled
from app.services.request_cancellation import run_for_request


def _add(a: int, b: int) -> int:
    return a + b


def _long_job() -> None:
    time.sleep(2)


class FakeRequest:
    disconnected = False

    async def is_disconnected(self) -> bool:
        return self.disconnected


def test_request_bridge_returns_real_result() -> None:
    async def scenario():
        request = FakeRequest()
        return await run_for_request(request, _add, 2, 3, timeout_seconds=4)
    assert asyncio.run(scenario()) == 5


def test_request_disconnect_cancels_child_then_recovers() -> None:
    async def scenario():
        request = FakeRequest()
        task = asyncio.create_task(run_for_request(request, _long_job, timeout_seconds=4))
        await asyncio.sleep(0.25)
        request.disconnected = True
        with pytest.raises(ComputationCancelled, match="disconnected"):
            await task
        request.disconnected = False
        return await run_for_request(request, _add, 2, 3, timeout_seconds=4)
    assert asyncio.run(scenario()) == 5
