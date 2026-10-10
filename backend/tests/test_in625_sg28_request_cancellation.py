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


def _active_sympy_calculation(ready) -> None:
    """Keep a spawned child busy doing real algebra until interrupted."""
    import sympy

    x = sympy.Symbol("x")
    expr = x**3 + 2*x
    ready.set()
    while True:
        expr = sympy.diff(expr, x) + x**3


def _sympy_after_cancellation() -> str:
    import sympy

    x = sympy.Symbol("x")
    return str(sympy.diff(x**3 + 2*x, x))


def test_asgi_disconnect_interrupts_active_sympy_and_recovers() -> None:
    """ASGI disconnect terminates an active SymPy child, not a sleeping stub."""
    import multiprocessing as mp
    from starlette.requests import Request

    async def scenario() -> str:
        ready = mp.get_context("spawn").Event()
        messages: asyncio.Queue[dict] = asyncio.Queue()
        scope = {
            "type": "http", "method": "POST", "path": "/sg28-isolated",
            "headers": [], "query_string": b"",
        }

        async def receive():
            try:
                return messages.get_nowait()
            except asyncio.QueueEmpty:
                return {"type": "http.request", "body": b"", "more_body": False}

        request = Request(scope, receive=receive)
        pending = asyncio.create_task(
            run_for_request(request, _active_sympy_calculation, ready, timeout_seconds=6)
        )
        try:
            assert await asyncio.to_thread(ready.wait, 3), "SymPy child did not start"
            await messages.put({"type": "http.disconnect"})
            with pytest.raises(ComputationCancelled, match="disconnected"):
                await asyncio.wait_for(pending, timeout=4)
        finally:
            if not pending.done():
                pending.cancel()
                try:
                    await pending
                except (ComputationCancelled, asyncio.CancelledError):
                    pass

        clean_request = Request(scope, receive=receive)
        return await run_for_request(
            clean_request, _sympy_after_cancellation, timeout_seconds=5
        )

    assert asyncio.run(scenario()) == "3*x**2 + 2"


def test_asgi_handler_task_cancellation_interrupts_child_and_recovers() -> None:
    """Cancelling an ASGI handler must clean up active math before recovery."""
    import multiprocessing as mp

    async def scenario() -> str:
        ready = mp.get_context("spawn").Event()
        request = FakeRequest()
        pending = asyncio.create_task(
            run_for_request(request, _active_sympy_calculation, ready, timeout_seconds=6)
        )
        try:
            assert await asyncio.to_thread(ready.wait, 3), "SymPy child did not start"
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(pending, timeout=4)
        finally:
            if not pending.done():
                pending.cancel()
                try:
                    await pending
                except asyncio.CancelledError:
                    pass
        return await run_for_request(
            FakeRequest(), _sympy_after_cancellation, timeout_seconds=5
        )

    assert asyncio.run(scenario()) == "3*x**2 + 2"




def _healthy_sympy_with_start_signal(ready, release) -> str:
    """Compute with SymPy, then remain active until independent cancel completes."""
    result = _sympy_after_cancellation()
    ready.set()
    if not release.wait(timeout=5):
        raise RuntimeError("Healthy worker release was not received")
    return result


def test_concurrent_request_disconnect_does_not_cancel_independent_request() -> None:
    """Cancel one active SymPy worker while a second completed math but is still running."""
    import multiprocessing as mp

    async def scenario() -> tuple[str, str]:
        ctx = mp.get_context("spawn")
        ready = ctx.Event()
        healthy_ready = ctx.Event()
        healthy_release = ctx.Event()
        disconnected = FakeRequest()
        healthy = FakeRequest()
        cancelled_task = asyncio.create_task(
            run_for_request(
                disconnected, _active_sympy_calculation, ready, timeout_seconds=8
            )
        )
        healthy_task = None
        try:
            assert await asyncio.to_thread(ready.wait, 4), "SymPy child did not start"
            healthy_task = asyncio.create_task(
                run_for_request(
                    healthy, _healthy_sympy_with_start_signal,
                    healthy_ready, healthy_release, timeout_seconds=8
                )
            )
            assert await asyncio.to_thread(healthy_ready.wait, 4), (
                "Independent SymPy child did not complete its calculation"
            )
            assert not healthy_task.done(), "Independent worker exited before cancellation"
            disconnected.disconnected = True
            with pytest.raises(ComputationCancelled, match="disconnected"):
                await asyncio.wait_for(cancelled_task, timeout=5)
            assert not healthy_task.done(), "Cancellation affected the independent worker"
            healthy_release.set()
            healthy_result = await asyncio.wait_for(healthy_task, timeout=5)
            return "cancelled", healthy_result
        finally:
            healthy_release.set()
            for pending in (cancelled_task, healthy_task):
                if pending is not None and not pending.done():
                    pending.cancel()
                    try:
                        await pending
                    except (asyncio.CancelledError, ComputationCancelled):
                        pass

    assert asyncio.run(scenario()) == ("cancelled", "3*x**2 + 2")


def _evaluate_actual_service(expression: str, angle_unit: str = "rad"):
    """Call the real evaluate service rather than a stand-in SymPy function."""
    from app.services.evaluate_service import evaluate
    return evaluate(expression, angle_unit)


@pytest.mark.parametrize(
    ("expression", "angle_unit", "expected"),
    [
        ("2+3", "rad", 5.0),
        ("sin(30)", "deg", 0.5),
        ("1/4", "rad", 0.25),
    ],
)
def test_isolated_real_evaluate_service_preserves_results(
    expression: str, angle_unit: str, expected: float,
) -> None:
    """Pre-integration gate: actual evaluate service remains usable in spawn."""
    async def scenario():
        return await run_for_request(
            FakeRequest(), _evaluate_actual_service,
            expression, angle_unit, timeout_seconds=6,
        )

    result = asyncio.run(scenario())
    assert result.is_numeric is True
    assert result.approx_value == pytest.approx(expected)
    assert result.input_expr is not None
    assert result.expr is not None


def test_isolated_real_evaluate_service_preserves_symbolic_result() -> None:
    """The spawn bridge must retain symbolic output, not force float conversion."""
    async def scenario():
        return await run_for_request(
            FakeRequest(), _evaluate_actual_service,
            "x+1", "rad", timeout_seconds=6,
        )

    result = asyncio.run(scenario())
    assert result.is_numeric is False
    assert result.approx_value is None
    assert str(result.expr) == "x + 1"
    assert str(result.input_expr) == "x + 1"


@pytest.mark.parametrize(
    ("expression", "exception_name"),
    [
        ("1/0", "DomainErrorResult"),
        ("x+(", "ParseSecurityError"),
    ],
)
def test_isolated_real_evaluate_service_rejects_invalid_input(
    expression: str, exception_name: str,
) -> None:
    """A child failure must not masquerade as a successful mathematical value."""
    from app.services.interruptible import ComputationFailed

    async def scenario():
        return await run_for_request(
            FakeRequest(), _evaluate_actual_service,
            expression, "rad", timeout_seconds=6,
        )

    with pytest.raises(ComputationFailed) as captured:
        asyncio.run(scenario())
    assert exception_name in str(captured.value)
