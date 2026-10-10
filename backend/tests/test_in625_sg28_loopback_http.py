"""SG28: real loopback TCP client disconnect, isolated test-only FastAPI app."""
import asyncio
import socket
import threading
import time

from fastapi import FastAPI, Request
import uvicorn

from app.services.interruptible import ComputationCancelled
from app.services.request_cancellation import run_for_request


def _bounded_work() -> str:
    time.sleep(2)
    return "done"


def _add(a: int, b: int) -> int:
    return a + b


def test_local_http_disconnect_cancels_worker_and_recovers() -> None:
    app = FastAPI()
    entered = threading.Event()
    cleaned = threading.Event()

    @app.get("/busy")
    async def busy(request: Request):
        entered.set()
        try:
            return {"value": await run_for_request(request, _bounded_work, timeout_seconds=4)}
        except ComputationCancelled:
            cleaned.set()
            return {"cancelled": True}

    @app.get("/recover")
    async def recover(request: Request):
        return {"value": await run_for_request(request, _add, 2, 3, timeout_seconds=4)}

    listen = socket.socket()
    listen.bind(("127.0.0.1", 0))
    listen.listen(16)
    port = listen.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", lifespan="off"))
    thread = threading.Thread(
        target=lambda: asyncio.run(server.serve(sockets=[listen])), daemon=True
    )
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.02)
        assert server.started, "Loopback ASGI server failed to start"
        with socket.create_connection(("127.0.0.1", port), timeout=2) as client:
            client.sendall(b"GET /busy HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            assert entered.wait(timeout=2), "Server did not receive busy request"
            # Closing the actual TCP socket emits ASGI http.disconnect.
            client.shutdown(socket.SHUT_RDWR)
        assert cleaned.wait(timeout=3), "Real HTTP disconnect did not cancel the worker"
        import httpx
        response = httpx.get(f"http://127.0.0.1:{port}/recover", timeout=6)
        assert response.status_code == 200
        assert response.json() == {"value": 5}
    finally:
        server.should_exit = True
        thread.join(timeout=4)
        listen.close()
        assert not thread.is_alive(), "Loopback server did not shut down"



def _slow_real_evaluate(expression, angle_unit, substitutions):
    """Picklable, deliberately slow real evaluate-service workload for TCP test."""
    from app.services import evaluate_service
    time.sleep(4)
    return evaluate_service.evaluate(expression, angle_unit, substitutions)


def test_public_evaluate_disconnect_cancels_isolated_worker_and_recovers(monkeypatch):
    """Exercise production FastAPI /evaluate over TCP with SG28 explicitly enabled."""
    import json
    import httpx
    from app.main import app
    from app.routers import evaluate as evaluate_router

    entered = threading.Event()
    cleaned = threading.Event()
    original_bridge = evaluate_router.run_for_request

    async def observed_bridge(request, operation, *args, **kwargs):
        entered.set()
        try:
            return await original_bridge(request, _slow_real_evaluate, *args, **kwargs)
        except Exception:
            cleaned.set()
            raise

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setattr(evaluate_router, "run_for_request", observed_bridge)

    listen = socket.socket()
    listen.bind(("127.0.0.1", 0))
    listen.listen(16)
    port = listen.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="error", lifespan="off"
    ))
    thread = threading.Thread(
        target=lambda: asyncio.run(server.serve(sockets=[listen])), daemon=True
    )
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.02)
        assert server.started
        body = json.dumps({"expression": "2+3"}).encode()
        header = (
            f"POST /api/v1/evaluate HTTP/1.1\r\nHost: localhost\r\n"
            f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        ).encode()
        with socket.create_connection(("127.0.0.1", port), timeout=2) as client:
            client.sendall(header + body)
            assert entered.wait(timeout=3), "Real evaluate route did not enter isolation"
            client.shutdown(socket.SHUT_RDWR)
        assert cleaned.wait(timeout=3), "Client disconnect did not interrupt public evaluate"

        # Restore the actual evaluate service for a fresh HTTP request.
        monkeypatch.setattr(evaluate_router, "run_for_request", original_bridge)
        response = httpx.post(
            f"http://127.0.0.1:{port}/api/v1/evaluate",
            json={"expression": "2+3"}, timeout=8,
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["result_approx"] == 5.0
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        listen.close()
        assert not thread.is_alive()



def test_public_evaluate_exhausted_capacity_returns_structured_503(monkeypatch):
    """Check the actual FastAPI route contract when admission is exhausted."""
    from fastapi.testclient import TestClient
    import app.services.request_cancellation as cancellation
    from app.main import app

    class NoCapacity:
        def acquire(self, blocking=False):
            return False

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setattr(cancellation, "_ADMISSION", NoCapacity())
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    assert body["operation"] == "evaluate"
    assert body["request_id"]
    assert body["error_code"] == "INTERNAL_ERROR"
    assert "Capacidad" in body["error_message"]



def test_public_evaluate_default_mode_does_not_use_isolation_capacity(monkeypatch):
    """The SG28 experimental quota must not affect the default API route."""
    from fastapi.testclient import TestClient
    import app.services.request_cancellation as cancellation
    from app.main import app

    class NoCapacity:
        def acquire(self, blocking=False):
            raise AssertionError("Default evaluate must not enter SG28 admission")

    monkeypatch.delenv("SG28_EVALUATE_ISOLATION", raising=False)
    monkeypatch.setattr(cancellation, "_ADMISSION", NoCapacity())
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["result_approx"] == 5.0



def test_public_evaluate_isolation_matches_default_mathresponse(monkeypatch):
    """SG28-E2E-06/09: compare real public MathResponse on both API paths.

    Compare stable public fields, not request IDs or wall-clock duration.
    This checks ordinary, symbolic and invalid input without mocking SymPy.
    """
    from fastapi.testclient import TestClient
    from app.main import app

    expressions = ("2+3", "x+x", "x+(")
    with TestClient(app) as client:
        for expression in expressions:
            responses = []
            for enabled in ("0", "1"):
                monkeypatch.setenv("SG28_EVALUATE_ISOLATION", enabled)
                response = client.post(
                    "/api/v1/evaluate", json={"expression": expression}
                )
                assert response.status_code == 200
                body = response.json()
                assert body["request_id"]
                assert body["operation"] == "evaluate"
                responses.append(body)

            original, isolated = responses
            for field in (
                "success", "operation", "result_type", "result_text",
                "result_latex", "result_approx", "error_code",
                "has_detailed_steps",
            ):
                assert isolated.get(field) == original.get(field), (
                    f"{expression!r}: public MathResponse field {field} differs: "
                    f"{original.get(field)!r} vs {isolated.get(field)!r}"
                )



def _sg28_public_cpu_spin(*_args) -> None:
    """Picklable CPU-intensive operation for actual /evaluate HTTP contract."""
    n = 0
    while True:
        n = (n + 1) % 1_000_003


def test_public_evaluate_cpu_exhaustion_returns_timeout_mathresponse(monkeypatch) -> None:
    """Real POSIX SIGXCPU must surface as public TIMEOUT, not HTTP 500."""
    import os
    import pytest
    from fastapi.testclient import TestClient
    from app.main import app
    from app.routers import evaluate as evaluate_router
    from app.services.request_cancellation import run_for_request

    if os.name != "posix":
        pytest.skip("POSIX RLIMIT_CPU only")

    async def cpu_bound_bridge(request, operation, *args, **kwargs):
        return await run_for_request(
            request, _sg28_public_cpu_spin, timeout_seconds=6,
        )

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setenv("SG28_ISOLATED_CPU_SECONDS", "1")
    monkeypatch.setattr(evaluate_router, "run_for_request", cpu_bound_bridge)
    with TestClient(app) as client:
        result = client.post("/api/v1/evaluate", json={"expression": "2+3"})
    assert result.status_code == 200
    body = result.json()
    assert body["success"] is False
    assert body["operation"] == "evaluate"
    assert body["error_code"] == "TIMEOUT"
    assert body["has_detailed_steps"] is False
    assert body["request_id"]


def _sg28_public_memory_allocation(*_args) -> None:
    """Use virtual address-space quota to fail allocation in isolated child."""
    unused = bytearray(2 * 1024 * 1024 * 1024)
    return len(unused)


def test_public_evaluate_memory_exhaustion_returns_complexity_mathresponse(monkeypatch) -> None:
    """Real child MemoryError must surface as a controlled public response."""
    import os
    import pytest
    from fastapi.testclient import TestClient
    from app.main import app
    from app.routers import evaluate as evaluate_router
    from app.services.request_cancellation import run_for_request

    if os.name != "posix":
        pytest.skip("POSIX virtual memory quota only")

    async def memory_bound_bridge(request, operation, *args, **kwargs):
        return await run_for_request(
            request, _sg28_public_memory_allocation, timeout_seconds=6,
        )

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setenv("SG28_ISOLATED_MEMORY_MB", "1024")
    monkeypatch.setattr(evaluate_router, "run_for_request", memory_bound_bridge)
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["operation"] == "evaluate"
    assert body["error_code"] == "COMPLEXITY_LIMIT"
    assert body["has_detailed_steps"] is False
    assert body["request_id"]
