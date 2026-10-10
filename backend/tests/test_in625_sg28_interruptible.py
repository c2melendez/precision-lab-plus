"""SG28: CI-only bounded subprocess termination proof, not production API."""
import time

import pytest

from app.services.interruptible import ComputationCancelled, ComputationTimedOut, run_bounded


def _add(a: int, b: int) -> int:
    return a + b


def _bounded_wait() -> None:
    time.sleep(2)


def test_isolated_computation_returns_result() -> None:
    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5


def test_timeout_terminates_isolated_process_and_recovers() -> None:
    started = time.monotonic()
    with pytest.raises(ComputationTimedOut):
        run_bounded(_bounded_wait, timeout_seconds=0.2)
    assert time.monotonic() - started < 3
    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5


def test_invalid_timeout_rejected() -> None:
    with pytest.raises(ValueError):
        run_bounded(_add, 2, 3, timeout_seconds=0)


def _real_sympy_evaluation() -> str:
    """Run actual SymPy in an isolated child, not a fabricated arithmetic stub."""
    import sympy
    x = sympy.Symbol("x")
    return str(sympy.diff(x**3 + 2*x, x))


def test_real_sympy_operation_executes_in_isolated_process() -> None:
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"


def test_real_sympy_operation_recovers_after_killed_process() -> None:
    with pytest.raises(ComputationTimedOut):
        run_bounded(_bounded_wait, timeout_seconds=0.2)
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"


def _sympy_after_gate(ready, release) -> str:
    """Perform genuine SymPy work only after parent confirms child is running."""
    ready.set()
    if not release.wait(timeout=3):
        raise RuntimeError("Test gate was never opened")
    return _real_sympy_evaluation()


def test_running_sympy_worker_is_terminated_before_evaluation_and_recovers() -> None:
    """Terminate a live child with a gated SymPy operation, not only a sleep stub."""
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    ready = ctx.Event()
    release = ctx.Event()
    # The process is already alive and blocked at a documented deterministic
    # gate. A short timeout must terminate it without starting SymPy compute.
    with pytest.raises(ComputationTimedOut):
        run_bounded(_sympy_after_gate, ready, release, timeout_seconds=1.0)
    assert ready.is_set(), "The isolated SymPy child never reached its active gate"
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"


def _sympy_mid_computation(ready) -> None:
    """Enter a genuine, bounded-repeat SymPy differentiation loop."""
    import sympy

    x = sympy.Symbol("x")
    expr = x**3 + 2*x
    ready.set()
    while True:
        # Actual SymPy computation, not a sleep or synchronization wait.
        expr = sympy.diff(expr, x) + x**3
        if expr == 0:
            expr = x**3


def test_terminate_during_real_sympy_computation_and_recover() -> None:
    """A live SymPy loop is stopped at its wall-clock limit, then recovers."""
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    ready = ctx.Event()
    with pytest.raises(ComputationTimedOut):
        run_bounded(_sympy_mid_computation, ready, timeout_seconds=1.0)
    assert ready.is_set(), "SymPy computation never reached its active loop"
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"


def test_explicit_cancellation_of_active_sympy_child_and_recovery() -> None:
    """Caller-triggered cancellation (not just timeout) kills active SymPy work."""
    import multiprocessing as mp
    import threading

    ready = mp.get_context("spawn").Event()
    cancelled = threading.Event()

    def cancel_after_worker_started() -> None:
        if ready.wait(timeout=3):
            cancelled.set()

    watcher = threading.Thread(target=cancel_after_worker_started, daemon=True)
    watcher.start()
    try:
        with pytest.raises(ComputationCancelled):
            run_bounded(
                _sympy_mid_computation, ready, timeout_seconds=5,
                cancel_event=cancelled,
            )
        assert ready.is_set()
    finally:
        cancelled.set()
        watcher.join(timeout=1)
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"


def _repeated_real_sympy_work() -> str:
    """Exercise actual SymPy repeatedly; the parent must stop this worker."""
    import sympy

    x = sympy.Symbol("x")
    deadline = time.monotonic() + 4.0
    while time.monotonic() < deadline:
        expr = (x + 1) ** 12
        _ = sympy.diff(expr, x)
    return "unexpected-completion-before-timeout"


def test_running_sympy_process_is_terminated_then_recovers() -> None:
    """Timeout kills a child running SymPy work; a fresh process still works."""
    started = time.monotonic()
    with pytest.raises(ComputationTimedOut):
        run_bounded(_repeated_real_sympy_work, timeout_seconds=1.5)
    assert time.monotonic() - started < 4.0
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"



def _raise_structured_worker_error() -> None:
    raise ValueError("isolated sentinel")


def test_isolated_child_failure_retains_structured_error_and_recovers() -> None:
    """Typed failures must cross the subprocess boundary without poisoning later jobs."""
    from app.services.interruptible import ComputationFailed

    with pytest.raises(ComputationFailed) as captured:
        run_bounded(_raise_structured_worker_error, timeout_seconds=5)
    assert captured.value.error_type == "ValueError"
    assert "isolated sentinel" in str(captured.value)
    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5



def _report_pid_then_compute_forever(pid_value, ready) -> None:
    """Expose the real child PID before starting an active SymPy workload."""
    import os
    import sympy

    pid_value.value = os.getpid()
    ready.set()
    x = sympy.Symbol("x")
    expr = x**3 + 2*x
    while True:
        expr = sympy.diff(expr, x) + x**3


@pytest.mark.skipif(__import__("os").name != "posix", reason="POSIX child PID liveness check")
@pytest.mark.parametrize("stop_mode", ["timeout", "cancel"])
def test_isolated_worker_pid_is_gone_after_interruption(stop_mode: str) -> None:
    """Prove that the actual child PID is gone, not merely that an error returned."""
    import multiprocessing as mp
    import os
    import threading

    ctx = mp.get_context("spawn")
    pid = ctx.Value("i", 0)
    ready = ctx.Event()
    stop = threading.Event()
    observed_alive = []

    def request_cancel_only_after_child_is_alive() -> None:
        if ready.wait(timeout=3):
            try:
                os.kill(pid.value, 0)
                observed_alive.append(True)
            except ProcessLookupError:
                observed_alive.append(False)
            stop.set()

    watcher = None
    if stop_mode == "cancel":
        watcher = threading.Thread(
            target=request_cancel_only_after_child_is_alive, daemon=True
        )
        watcher.start()
    try:
        expected = ComputationCancelled if stop_mode == "cancel" else ComputationTimedOut
        with pytest.raises(expected):
            run_bounded(
                _report_pid_then_compute_forever, pid, ready,
                timeout_seconds=4 if stop_mode == "cancel" else 1.5,
                cancel_event=stop if stop_mode == "cancel" else None,
            )
        assert ready.is_set(), "Child process never reported being active"
        assert pid.value > 0, "Missing observed child PID"
        if stop_mode == "cancel":
            assert observed_alive == [True], "Worker not alive before cancel signal"
        with pytest.raises(ProcessLookupError):
            os.kill(pid.value, 0)
    finally:
        stop.set()
        if watcher is not None:
            watcher.join(timeout=2)

    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5



def _sg28_read_cpu_budget() -> tuple[int, int]:
    import resource
    return resource.getrlimit(resource.RLIMIT_CPU)


@pytest.mark.skipif(__import__("os").name != "posix", reason="POSIX CPU limit only")
def test_opt_in_child_cpu_budget_applies_only_to_spawned_worker(monkeypatch) -> None:
    """SG28: optional CPU ceiling is installed in child, not the API process."""
    import resource
    parent_before = resource.getrlimit(resource.RLIMIT_CPU)
    monkeypatch.setenv("SG28_ISOLATED_CPU_SECONDS", "2")
    assert run_bounded(_sg28_read_cpu_budget, timeout_seconds=5) == (2, 3)
    assert resource.getrlimit(resource.RLIMIT_CPU) == parent_before
    monkeypatch.delenv("SG28_ISOLATED_CPU_SECONDS")
    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5


def _sg28_cpu_bound_loop() -> None:
    """Bounded by RLIMIT_CPU in POSIX spawned child only."""
    value = 0
    while True:
        value = (value + 1) % 1_000_003


@pytest.mark.skipif(__import__("os").name != "posix", reason="POSIX CPU limit only")
def test_cpu_budget_exhaustion_reaps_child_and_recovers(monkeypatch) -> None:
    """SG28: CPU-exhausted child exits before wall timeout; subsequent math works."""
    import time
    from app.services.interruptible import ComputationTimedOut

    monkeypatch.setenv("SG28_ISOLATED_CPU_SECONDS", "1")
    start = time.monotonic()
    with pytest.raises(ComputationTimedOut, match="CPU budget exceeded"):
        run_bounded(_sg28_cpu_bound_loop, timeout_seconds=6)
    assert time.monotonic() - start < 5.5, "CPU ceiling did not end child in time"
    monkeypatch.delenv("SG28_ISOLATED_CPU_SECONDS")
    assert run_bounded(_add, 4, 5, timeout_seconds=5) == 9



def _sg28_read_memory_budget() -> tuple[int, int]:
    import resource
    return resource.getrlimit(resource.RLIMIT_AS)


@pytest.mark.skipif(__import__("os").name != "posix", reason="POSIX virtual memory budget only")
def test_optional_child_memory_budget_is_isolated_and_recovers(monkeypatch) -> None:
    """Check opt-in child RLIMIT_AS without constraining FastAPI parent."""
    import resource
    before = resource.getrlimit(resource.RLIMIT_AS)
    monkeypatch.setenv("SG28_ISOLATED_MEMORY_MB", "1024")
    limit = 1024 * 1024 * 1024
    assert run_bounded(_sg28_read_memory_budget, timeout_seconds=5) == (limit, limit)
    assert resource.getrlimit(resource.RLIMIT_AS) == before
    monkeypatch.delenv("SG28_ISOLATED_MEMORY_MB")
    assert run_bounded(_add, 4, 5, timeout_seconds=5) == 9
