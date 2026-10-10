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


def test_starlette_request_receives_asgi_disconnect_and_recovers() -> None:
    """Exercise a real Starlette Request with an ASGI http.disconnect message.

    This is an in-process ASGI transport test, NOT an external network socket.
    """
    from starlette.requests import Request

    async def scenario():
        messages: asyncio.Queue[dict] = asyncio.Queue()
        scope = {"type": "http", "method": "POST", "path": "/sg28-isolated",
                 "headers": [], "query_string": b""}

        async def receive():
            try:
                return messages.get_nowait()
            except asyncio.QueueEmpty:
                return {"type": "http.request", "body": b"", "more_body": False}

        request = Request(scope, receive=receive)
        pending = asyncio.create_task(run_for_request(request, _long_job, timeout_seconds=4))
        await asyncio.sleep(0.3)
        await messages.put({"type": "http.disconnect"})
        with pytest.raises(ComputationCancelled, match="disconnected"):
            await asyncio.wait_for(pending, timeout=3)
        recovered = Request(scope, receive=receive)
        return await run_for_request(recovered, _add, 2, 3, timeout_seconds=4)

    assert asyncio.run(scenario()) == 5
