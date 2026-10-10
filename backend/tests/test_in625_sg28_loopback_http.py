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
