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
    assert captured.value.error_type == exception_name



def _evaluate_contract_roundtrip(expression: str):
    """Exercise the actual response model inside the isolated process."""
    from app.schemas.responses import MathResponse, OperationType, ResultType
    result = _evaluate_actual_service(expression)
    return MathResponse(
        success=True,
        operation=OperationType.EVALUATE,
        request_id="sg28-contract-probe",
        result_type=ResultType.SCALAR,
        input_text=expression,
        result_text=str(result.expr),
        result_approx=result.approx_value,
        has_detailed_steps=False,
        duration_ms=0.0,
    )


def test_isolated_math_response_contract_survives_process_boundary() -> None:
    """A real MathResponse must retain its public types after subprocess return."""
    from app.schemas.responses import MathResponse, OperationType, ResultType

    async def scenario():
        return await run_for_request(
            FakeRequest(), _evaluate_contract_roundtrip,
            "2+3", timeout_seconds=6,
        )

    result = asyncio.run(scenario())
    assert isinstance(result, MathResponse)
    assert result.success is True
    assert result.operation == OperationType.EVALUATE
    assert result.result_type == ResultType.SCALAR
    assert result.result_approx == pytest.approx(5.0)
    assert result.has_detailed_steps is False
    assert result.model_dump(mode="json")["request_id"] == "sg28-contract-probe"



def _error_contract_roundtrip():
    """Build the canonical error schema in a child (not the public router)."""
    from app.schemas.responses import ErrorCode, MathResponse, OperationType
    return MathResponse(
        success=False,
        operation=OperationType.EVALUATE,
        request_id="sg28-error-probe",
        has_detailed_steps=False,
        error_code=ErrorCode.PARSE_ERROR,
        error_message="Invalid mathematical expression",
        duration_ms=0.0,
    )


def test_isolated_math_response_error_contract_survives_process_boundary() -> None:
    """A typed error response must survive transport without becoming success."""
    from app.schemas.responses import ErrorCode, MathResponse, OperationType

    async def scenario():
        return await run_for_request(
            FakeRequest(), _error_contract_roundtrip, timeout_seconds=6,
        )

    result = asyncio.run(scenario())
    assert isinstance(result, MathResponse)
    assert result.success is False
    assert result.operation == OperationType.EVALUATE
    assert result.error_code == ErrorCode.PARSE_ERROR
    assert result.error_message == "Invalid mathematical expression"
    assert result.result_type is None
    assert result.has_detailed_steps is False
    assert result.model_dump(mode="json")["error_code"] == "PARSE_ERROR"


@pytest.mark.parametrize(
    ("expression", "error_type", "expected_code"),
    [
        ("1/0", "DomainErrorResult", "DOMAIN_ERROR"),
        ("x+(", "ParseSecurityError", "PARSE_ERROR"),
    ],
)
def test_isolated_real_evaluate_error_maps_to_public_error_code(
    expression: str, error_type: str, expected_code: str,
) -> None:
    """Check typed child failures map to the existing public error enum."""
    from app.services.interruptible import ComputationFailed
    from app.schemas.responses import ErrorCode

    async def scenario():
        return await run_for_request(
            FakeRequest(), _evaluate_actual_service,
            expression, "rad", timeout_seconds=6,
        )

    with pytest.raises(ComputationFailed) as captured:
        asyncio.run(scenario())
    assert captured.value.error_type == error_type

    typed_mapping = {
        "DomainErrorResult": ErrorCode.DOMAIN_ERROR,
        "ParseSecurityError": ErrorCode.PARSE_ERROR,
    }
    assert typed_mapping[captured.value.error_type].value == expected_code



@pytest.mark.parametrize(
    ("payload", "expected_success", "expected_error"),
    [
        ({"expression": "2+3"}, True, None),
        ({"expression": "sin(30)", "angle_unit": "deg"}, True, None),
        ({"expression": "x+("}, False, "PARSE_ERROR"),
        ({"expression": "1/0"}, False, "DOMAIN_ERROR"),
    ],
)
def test_opt_in_public_evaluate_http_contract(
    monkeypatch, payload: dict, expected_success: bool, expected_error: str | None,
) -> None:
    """Hit the actual FastAPI route with and without process isolation."""
    from fastapi.testclient import TestClient
    from app.main import app

    results = []
    for enabled in ("0", "1"):
        monkeypatch.setenv("SG28_EVALUATE_ISOLATION", enabled)
        with TestClient(app) as client:
            response = client.post("/api/v1/evaluate", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is expected_success
        assert body["operation"] == "evaluate"
        assert body["error_code"] == expected_error
        assert body["has_detailed_steps"] is False
        assert body["request_id"]
        results.append(body)

    for key in ("success", "operation", "error_code", "result_text", "result_latex"):
        assert results[0][key] == results[1][key]



def test_isolation_capacity_rejects_second_request_and_recovers(monkeypatch) -> None:
    """Admission returns immediately when busy and frees slot after cancellation."""
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))

    async def scenario():
        first = FakeRequest()
        task = asyncio.create_task(
            bridge.run_for_request(first, _long_job, timeout_seconds=4)
        )
        await asyncio.sleep(0.3)
        assert not task.done(), "First worker exited before capacity test"
        with pytest.raises(bridge.IsolationCapacityExceeded):
            await bridge.run_for_request(FakeRequest(), _add, 2, 3, timeout_seconds=4)
        first.disconnected = True
        with pytest.raises(ComputationCancelled):
            await task
        return await bridge.run_for_request(FakeRequest(), _add, 2, 3, timeout_seconds=4)

    assert asyncio.run(scenario()) == 5



def test_repeated_cancel_cycles_release_admission_and_recover() -> None:
    """SG28-E2E-07 backend: repeated real child cancellation must not leak slots.

    Each iteration disconnects a request during a bounded sleeping child,
    then runs an independent real spawned calculation. A leaked admission slot
    or unfinished coordinator causes a later iteration to fail.
    """
    async def scenario() -> None:
        for iteration in range(4):
            request = FakeRequest()
            pending = asyncio.create_task(
                run_for_request(request, _long_job, timeout_seconds=5)
            )
            try:
                await asyncio.sleep(0.2)
                request.disconnected = True
                with pytest.raises(ComputationCancelled, match="disconnected"):
                    await asyncio.wait_for(pending, timeout=4)
            finally:
                if not pending.done():
                    pending.cancel()
                    try:
                        await pending
                    except (ComputationCancelled, asyncio.CancelledError):
                        pass

            assert await run_for_request(
                FakeRequest(), _add, iteration, 10, timeout_seconds=5
            ) == iteration + 10

    asyncio.run(scenario())



def test_timeout_releases_single_slot_and_allows_recovery(monkeypatch) -> None:
    """SG28 resource gate: timeout must reap active work before releasing quota."""
    import threading
    import app.services.request_cancellation as bridge
    from app.services.interruptible import ComputationTimedOut

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))

    async def scenario() -> int:
        task = asyncio.create_task(
            bridge.run_for_request(FakeRequest(), _long_job, timeout_seconds=0.65)
        )
        await asyncio.sleep(0.15)
        assert not task.done(), "Timed worker completed before admission probe"
        with pytest.raises(bridge.IsolationCapacityExceeded):
            await bridge.run_for_request(FakeRequest(), _add, 2, 3, timeout_seconds=3)
        with pytest.raises(ComputationTimedOut):
            await asyncio.wait_for(task, timeout=4)
        return await bridge.run_for_request(
            FakeRequest(), _add, 4, 5, timeout_seconds=5
        )

    assert asyncio.run(scenario()) == 9



def _sg28_independent_admission_process(ready, release) -> None:
    """Probe the actual admission model from a separate Python process."""
    import threading
    import app.services.request_cancellation as bridge

    bridge._ADMISSION = threading.BoundedSemaphore(1)
    first = bridge._ADMISSION.acquire(blocking=False)
    second = bridge._ADMISSION.acquire(blocking=False)
    ready.put((first, second))
    release.wait(timeout=8)
    if first:
        bridge._ADMISSION.release()


def test_admission_quota_is_per_process_not_a_cluster_wide_limit() -> None:
    """H2 topology gap: two workers with K=1 each admit two concurrent slots.

    This regression deliberately documents a production rollout blocker; it
    must NOT be misreported as evidence of global cross-replica admission.
    """
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    ready = ctx.Queue()
    release = ctx.Event()
    workers = [
        ctx.Process(target=_sg28_independent_admission_process, args=(ready, release))
        for _ in range(2)
    ]
    try:
        for worker in workers:
            worker.start()
        observed = [ready.get(timeout=6) for _ in workers]
        assert observed == [(True, False), (True, False)]
        # Aggregate capacity is 2 although each process has a limit of 1.
        assert sum(admitted for admitted, _ in observed) == 2
    finally:
        release.set()
        for worker in workers:
            worker.join(timeout=4)
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=2)
            if worker.pid is not None:
                worker.close()
        ready.close()



def test_distributed_slot_budget_can_be_partitioned_per_replica() -> None:
    """Document a safe allocation strategy without claiming global admission.

    An operator can partition a desired fleet budget into fixed per-replica
    quotas only when replica/worker count is known and bounded. Dynamic
    autoscaling invalidates that assumption until a shared coordinator exists.
    """
    for total, replicas, expected in (
        (1, 1, [1]),
        (2, 2, [1, 1]),
        (5, 2, [3, 2]),
        (7, 3, [3, 2, 2]),
    ):
        allocated = [total // replicas + (i < total % replicas) for i in range(replicas)]
        assert allocated == expected
        assert sum(allocated) == total
        assert max(allocated) - min(allocated) <= 1


def test_static_partition_rejects_more_workers_than_global_budget() -> None:
    """A semaphore minimum of one per worker cannot represent global K < R."""
    from app.services import request_cancellation as bridge

    global_budget, worker_count = 2, 3
    assert worker_count > global_budget
    assert bridge._MAX_ISOLATED_REQUESTS >= 1
    assert worker_count * 1 > global_budget


def test_two_stage_request_admission_is_phase_scoped_not_end_to_end(monkeypatch) -> None:
    """Deterministic local gate: evaluation and presentation compete for one slot.

    This proves admission/recovery per phase, NOT a reservation across the
    complete HTTP request or an admission limit shared by other processes.
    No real worker, production endpoint, or external load is involved.
    """
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    entered_evaluation = threading.Event()
    release_evaluation = threading.Event()
    entered_presentation = threading.Event()
    release_presentation = threading.Event()

    def bounded_probe(operation, *args, timeout_seconds, cancel_event):
        if operation == "evaluation":
            entered_evaluation.set()
            assert release_evaluation.wait(timeout=3)
        elif operation == "presentation":
            entered_presentation.set()
            assert release_presentation.wait(timeout=3)
        return operation

    monkeypatch.setattr(bridge, "run_bounded", bounded_probe)

    async def scenario() -> tuple[str, str]:
        evaluation = asyncio.create_task(
            bridge.run_for_request(FakeRequest(), "evaluation")
        )
        presentation = None
        try:
            assert await asyncio.to_thread(entered_evaluation.wait, 2)
            with pytest.raises(bridge.IsolationCapacityExceeded):
                await bridge.run_for_request(FakeRequest(), "presentation")
            release_evaluation.set()
            assert await asyncio.wait_for(evaluation, 3) == "evaluation"

            # The same logical HTTP request could still require presentation,
            # yet its first-phase slot is already available to other requests.
            presentation = asyncio.create_task(
                bridge.run_for_request(FakeRequest(), "presentation")
            )
            assert await asyncio.to_thread(entered_presentation.wait, 2)
            with pytest.raises(bridge.IsolationCapacityExceeded):
                await bridge.run_for_request(FakeRequest(), "evaluation")
            release_presentation.set()
            return "evaluation", await asyncio.wait_for(presentation, 3)
        finally:
            release_evaluation.set()
            release_presentation.set()
            for task in (evaluation, presentation):
                if task is not None and not task.done():
                    await asyncio.wait_for(task, 3)

    assert asyncio.run(scenario()) == ("evaluation", "presentation")
    # Both stages finished: no admission leak remains.
    assert asyncio.run(bridge.run_for_request(FakeRequest(), "recovery")) == "recovery"


def test_cancelled_handler_retains_slot_until_coordinator_thread_finishes(monkeypatch) -> None:
    """A cancelled handler cannot admit replacement work before cleanup ends.

    Deterministic, single-process contract: this simulates a coordinator thread
    stalled during its final cleanup. It makes no claims about cluster quotas,
    live network disconnects, or process termination in a deployed server.
    """
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    entered = threading.Event()
    release = threading.Event()
    finished = threading.Event()
    calls = []

    def controlled_worker(operation, *args, timeout_seconds, cancel_event):
        calls.append(operation)
        if operation == "occupied":
            entered.set()
            try:
                assert release.wait(timeout=5), "cleanup release signal missing"
            finally:
                finished.set()
        return operation

    monkeypatch.setattr(bridge, "run_bounded", controlled_worker)

    async def scenario():
        occupied = asyncio.create_task(
            bridge.run_for_request(FakeRequest(), "occupied")
        )
        try:
            assert await asyncio.to_thread(entered.wait, 2)
            occupied.cancel()
            # The handler intentionally waits for coordinator cleanup before
            # acknowledging cancellation. Assert saturation while it waits;
            # awaiting the handler first would deadlock this test.
            await asyncio.sleep(0)
            assert not occupied.done(), "handler returned before coordinator cleanup"
            assert not finished.is_set(), "worker ended before saturation check"
            with pytest.raises(bridge.IsolationCapacityExceeded):
                await bridge.run_for_request(FakeRequest(), "must-not-run")
            assert "must-not-run" not in calls

            release.set()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(occupied, 3)
            assert await asyncio.to_thread(finished.wait, 2)
            for _ in range(100):
                try:
                    return await bridge.run_for_request(FakeRequest(), "recovered")
                except bridge.IsolationCapacityExceeded:
                    await asyncio.sleep(0.01)
            pytest.fail("admission slot not returned after worker cleanup")
        finally:
            release.set()

    assert asyncio.run(scenario()) == "recovered"
    assert calls == ["occupied", "recovered"]


def test_interleaving_request_can_take_slot_between_evaluation_and_presentation(monkeypatch) -> None:
    """Demonstrate phase-scoped admission gap without claiming an end-to-end lease.

    After evaluation releases local K=1, another request can acquire the only
    slot and block presentation. All work is mocked and bounded; this proves
    the known design limitation rather than implementing distributed quotas.
    """
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    interloper_entered = threading.Event()
    interloper_release = threading.Event()

    def controlled(operation, *args, timeout_seconds, cancel_event):
        if operation == "other-request":
            interloper_entered.set()
            assert interloper_release.wait(timeout=3)
        return operation

    monkeypatch.setattr(bridge, "run_bounded", controlled)

    async def scenario():
        # Logical request A completes its evaluation phase and releases K=1.
        assert await bridge.run_for_request(FakeRequest(), "evaluation-A") == "evaluation-A"
        # Request B starts before A can acquire capacity for presentation.
        other = asyncio.create_task(
            bridge.run_for_request(FakeRequest(), "other-request")
        )
        try:
            assert await asyncio.to_thread(interloper_entered.wait, 2)
            with pytest.raises(bridge.IsolationCapacityExceeded):
                await bridge.run_for_request(FakeRequest(), "presentation-A")
            interloper_release.set()
            assert await asyncio.wait_for(other, 3) == "other-request"
        finally:
            interloper_release.set()
            if not other.done():
                await asyncio.wait_for(other, 3)
        # After B finishes, A may retry presentation, but no reservation exists.
        assert await bridge.run_for_request(FakeRequest(), "presentation-A") == "presentation-A"

    asyncio.run(scenario())


def test_request_scoped_admission_lease_blocks_interleaving_and_releases(monkeypatch) -> None:
    """Executable target contract: one local K=1 lease spans both phases.

    This probe deliberately owns the BoundedSemaphore in the test. It is a
    proposed admission lifetime, NOT a claim the current router implements it.
    The released-between-phases regression above documents the current gap.
    """
    import threading
    import app.services.request_cancellation as bridge

    quota = threading.BoundedSemaphore(1)
    monkeypatch.setattr(bridge, "_ADMISSION", quota)
    assert quota.acquire(blocking=False)
    try:
        # Request A holds capacity through both logical phases.
        assert not quota.acquire(blocking=False), "request B interleaved at evaluate boundary"
        evaluation = "evaluation-A"
        assert evaluation == "evaluation-A"
        assert not quota.acquire(blocking=False), "request B interleaved before presentation"
        presentation = "presentation-A"
        assert presentation == "presentation-A"
        assert not quota.acquire(blocking=False), "request B interleaved before lease exit"
    finally:
        quota.release()
    assert quota.acquire(blocking=False), "request B cannot recover after lease exit"
    quota.release()


def test_real_local_request_admission_lease_holds_slot_across_phases(monkeypatch) -> None:
    """Exercise real opt-in lease ownership, not the public router."""
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    with bridge.request_admission_lease():
        assert not bridge._ADMISSION.acquire(blocking=False)
        # A logical request owns one slot through evaluation and presentation.
        for phase in ("evaluation", "presentation"):
            assert phase in ("evaluation", "presentation")
            with pytest.raises(bridge.IsolationCapacityExceeded):
                with bridge.request_admission_lease():
                    pytest.fail("a competing request entered during " + phase)
        assert not bridge._ADMISSION.acquire(blocking=False)
    with bridge.request_admission_lease():
        assert not bridge._ADMISSION.acquire(blocking=False)


def test_real_local_request_admission_lease_recovers_on_exception(monkeypatch) -> None:
    """Exception paths release the local slot, including capacity failures."""
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    with pytest.raises(RuntimeError, match="synthetic failure"):
        with bridge.request_admission_lease():
            raise RuntimeError("synthetic failure")
    with bridge.request_admission_lease():
        assert not bridge._ADMISSION.acquire(blocking=False)


def test_reserved_bridge_two_phases_preserve_single_local_lease(monkeypatch) -> None:
    """The real bridge does not reacquire or release a caller-owned lease."""
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))

    async def scenario() -> None:
        with bridge.request_admission_lease():
            for phase in ("evaluation", "presentation"):
                assert await bridge.run_for_request(
                    FakeRequest(), _add, 2, 3,
                    timeout_seconds=5, admission_reserved=True,
                ) == 5
                with pytest.raises(bridge.IsolationCapacityExceeded):
                    with bridge.request_admission_lease():
                        pytest.fail("reserved slot became available in " + phase)
        assert await bridge.run_for_request(
            FakeRequest(), _add, 4, 5, timeout_seconds=5,
        ) == 9

    asyncio.run(scenario())


def test_reserved_bridge_exception_keeps_lease_until_caller_exits(monkeypatch) -> None:
    """Child failure never double-releases an outer admission lease."""
    import threading
    import app.services.request_cancellation as bridge
    from app.services.interruptible import ComputationFailed

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))

    async def scenario() -> None:
        with bridge.request_admission_lease():
            with pytest.raises(ComputationFailed):
                await bridge.run_for_request(
                    FakeRequest(), _evaluate_actual_service,
                    "x+(", "rad", timeout_seconds=5, admission_reserved=True,
                )
            with pytest.raises(bridge.IsolationCapacityExceeded):
                with bridge.request_admission_lease():
                    pytest.fail("released while outer lease is still active")
        assert await bridge.run_for_request(
            FakeRequest(), _add, 4, 5, timeout_seconds=5,
        ) == 9

    asyncio.run(scenario())


def test_reserved_bridge_cancellation_retains_lease_until_worker_cleanup(monkeypatch) -> None:
    """A reserved request must retain admission until cancelled work is reaped."""
    import threading
    import app.services.request_cancellation as bridge

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    entered = threading.Event()
    release = threading.Event()

    def controlled(operation, *args, timeout_seconds, cancel_event):
        entered.set()
        assert release.wait(timeout=5), "worker cleanup never released"
        return operation

    monkeypatch.setattr(bridge, "run_bounded", controlled)

    async def scenario():
        with bridge.request_admission_lease():
            pending = asyncio.create_task(
                bridge.run_for_request(
                    FakeRequest(), "occupied", admission_reserved=True,
                )
            )
            try:
                assert await asyncio.to_thread(entered.wait, 2)
                pending.cancel()
                await asyncio.sleep(0)
                assert not pending.done(), "handler exited before coordinator cleanup"
                with pytest.raises(bridge.IsolationCapacityExceeded):
                    with bridge.request_admission_lease():
                        pytest.fail("capacity leaked during cleanup")
                release.set()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(pending, 3)
            finally:
                release.set()
                if not pending.done():
                    try:
                        await asyncio.wait_for(pending, 3)
                    except asyncio.CancelledError:
                        pass
        with bridge.request_admission_lease():
            assert not bridge._ADMISSION.acquire(blocking=False)

    asyncio.run(scenario())


def test_opt_in_http_evaluate_holds_one_lease_across_both_worker_phases(monkeypatch) -> None:
    """Real route and two child phases share one local K=1 capacity lease."""
    import threading
    from fastapi.testclient import TestClient
    from app.main import app
    import app.services.request_cancellation as bridge
    import app.routers.evaluate as router_module

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    observed = []
    original = router_module.run_for_request

    async def traced(request, operation, *args, **kwargs):
        assert kwargs.get("admission_reserved") is True
        assert not bridge._ADMISSION.acquire(blocking=False)
        observed.append(getattr(operation, "__name__", str(operation)))
        return await original(request, operation, *args, **kwargs)

    monkeypatch.setattr(router_module, "run_for_request", traced)
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(observed) == 2
    with bridge.request_admission_lease():
        assert not bridge._ADMISSION.acquire(blocking=False)


def test_opt_in_http_evaluate_returns_503_when_local_lease_is_exhausted(monkeypatch) -> None:
    """Public HTTP admission must fail closed without starting calculation."""
    import threading
    from fastapi.testclient import TestClient
    from app.main import app
    import app.services.request_cancellation as bridge
    import app.routers.evaluate as router_module

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    calls = []

    async def forbidden_worker(*args, **kwargs):
        calls.append(True)
        pytest.fail("isolated worker started without admission")

    monkeypatch.setattr(router_module, "run_for_request", forbidden_worker)
    with bridge.request_admission_lease():
        with TestClient(app) as client:
            response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert response.status_code == 503
        body = response.json()
        assert body["success"] is False
        assert body["operation"] == "evaluate"
        assert body["error_code"] == "INTERNAL_ERROR"
        assert body["request_id"]
        assert not calls

    # Exhaustion must not permanently consume the slot.
    with bridge.request_admission_lease():
        assert not bridge._ADMISSION.acquire(blocking=False)


def test_opt_in_http_evaluate_recovers_after_capacity_503(monkeypatch) -> None:
    """Actual HTTP route rejects saturation, then processes math after release."""
    import threading
    from fastapi.testclient import TestClient
    from app.main import app
    import app.services.request_cancellation as bridge

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    with TestClient(app) as client:
        with bridge.request_admission_lease():
            denied = client.post("/api/v1/evaluate", json={"expression": "2+3"})
            assert denied.status_code == 503
            assert denied.json()["success"] is False
        recovered = client.post("/api/v1/evaluate", json={"expression": "4+5"})
    assert recovered.status_code == 200
    assert recovered.json()["success"] is True
    assert recovered.json()["result_approx"] == pytest.approx(9.0)
