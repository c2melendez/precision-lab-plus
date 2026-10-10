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
