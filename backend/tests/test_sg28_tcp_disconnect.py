"""SG28/H2: real loopback TCP disconnect observed by ASGI outer middleware.

Runs a disposable Uvicorn server inside CI. No production endpoint or isolation
feature flag is touched. This covers the transport signal, not fleet admission.
"""
import socket
import threading
import time

from app.services.disconnect_tracking import DisconnectTrackingMiddleware


def _real_sympy_child(ready):
    import sympy
    x = sympy.Symbol('x')
    expression = x**3 + 2*x
    ready.set()
    while True:
        expression = sympy.diff(expression, x) + x**3



def test_real_tcp_disconnect_sets_outer_scope_event():
    import uvicorn

    disconnected = threading.Event()
    server_scope = {}

    async def endpoint(scope, receive, send):
        server_scope["scope"] = scope
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                assert scope["sg28_http_disconnected"].is_set()
                disconnected.set()
                return

    app = DisconnectTrackingMiddleware(endpoint)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(5)
    host, port = listener.getsockname()
    server = uvicorn.Server(
        uvicorn.Config(app, host=host, port=port, log_level="error", lifespan="off")
    )
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [listener]}, daemon=True
    )
    try:
        thread.start()
        deadline = time.monotonic() + 5
        while not server.started and time.monotonic() < deadline:
            assert thread.is_alive(), "Temporary HTTP server failed to start"
            time.sleep(0.02)
        assert server.started, "Temporary HTTP server startup timed out"
        with socket.create_connection((host, port), timeout=3) as client:
            client.sendall(
                b"POST /probe HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Length: 0\r\nConnection: close\r\n\r\n"
            )
        assert disconnected.wait(5), "ASGI did not observe closed TCP client"
        assert server_scope["scope"]["sg28_http_disconnected"].is_set()
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        listener.close()
        assert not thread.is_alive(), "Temporary HTTP server failed to stop"


def test_real_tcp_disconnect_keeps_local_k1_reserved_until_cleanup(monkeypatch):
    """Socket close cannot free local admission while coordinator is still active.

    Real network/ASGI signal; mock the isolated coordinator to control cleanup.
    Does not establish multi-replica admission or actual subprocess termination.
    """
    import asyncio
    from starlette.requests import Request
    import uvicorn
    import app.services.request_cancellation as bridge
    from app.services.interruptible import ComputationCancelled

    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    entered = threading.Event()
    cancel_seen = threading.Event()
    release = threading.Event()
    completed = threading.Event()
    outcomes = []

    def controlled(operation, *args, timeout_seconds, cancel_event):
        entered.set()
        assert cancel_event.wait(7), "Disconnect was never forwarded to coordinator"
        cancel_seen.set()
        assert release.wait(7), "Coordinator cleanup was not released"
        raise ComputationCancelled("coordinator cancelled")

    monkeypatch.setattr(bridge, "run_bounded", controlled)

    async def endpoint(scope, receive, send):
        request = Request(scope, receive=receive)
        try:
            with bridge.request_admission_lease():
                await bridge.run_for_request(
                    request, lambda: None, admission_reserved=True
                )
        except ComputationCancelled:
            outcomes.append("disconnected")
        finally:
            completed.set()

    app = DisconnectTrackingMiddleware(endpoint)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(5)
    host, port = listener.getsockname()
    server = uvicorn.Server(
        uvicorn.Config(app, host=host, port=port, log_level="error", lifespan="off")
    )
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [listener]}, daemon=True
    )
    try:
        thread.start()
        deadline = time.monotonic() + 5
        while not server.started and time.monotonic() < deadline:
            assert thread.is_alive(), "Temporary HTTP server did not start"
            time.sleep(0.02)
        assert server.started, "Temporary HTTP server startup timed out"

        with socket.create_connection((host, port), timeout=3) as client:
            client.sendall(
                b"POST /probe HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Length: 0\r\nConnection: close\r\n\r\n"
            )
            assert entered.wait(4), "Coordinator did not acquire the local slot"

        assert cancel_seen.wait(5), "TCP close did not trigger cancellation"
        assert not completed.is_set(), "Request completed before coordinator cleanup"
        try:
            with bridge.request_admission_lease():
                raise AssertionError("Competing request admitted before cleanup")
        except bridge.IsolationCapacityExceeded:
            pass
        release.set()
        assert completed.wait(5), "Request did not finish after coordinator cleanup"
        assert outcomes == ["disconnected"]
        with bridge.request_admission_lease():
            pass
    finally:
        release.set()
        server.should_exit = True
        thread.join(timeout=5)
        listener.close()
        assert not thread.is_alive(), "Temporary HTTP server did not stop"


def test_real_tcp_disconnect_cancels_actual_sympy_child_and_recovers(monkeypatch):
    """Observe real TCP disconnect and spawned SymPy evaluation under local K=1."""
    import asyncio
    import multiprocessing as mp
    from starlette.requests import Request
    import uvicorn
    import app.services.request_cancellation as bridge
    from app.services.interruptible import ComputationCancelled


    monkeypatch.setattr(bridge, "_ADMISSION", threading.BoundedSemaphore(1))
    ready = mp.get_context("spawn").Event()
    completed = threading.Event()
    cancelled = threading.Event()

    async def endpoint(scope, receive, send):
        try:
            with bridge.request_admission_lease():
                await bridge.run_for_request(
                    Request(scope, receive=receive),
                    _real_sympy_child, ready,
                    timeout_seconds=8, admission_reserved=True,
                )
        except ComputationCancelled:
            cancelled.set()
        finally:
            completed.set()

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(5)
    host, port = listener.getsockname()
    server = uvicorn.Server(uvicorn.Config(
        DisconnectTrackingMiddleware(endpoint),
        host=host, port=port, log_level="error", lifespan="off",
    ))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    try:
        thread.start()
        deadline = time.monotonic() + 6
        while not server.started and time.monotonic() < deadline:
            assert thread.is_alive()
            time.sleep(0.02)
        assert server.started
        with socket.create_connection((host, port), timeout=4) as client:
            client.sendall(
                b"POST /probe HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Length: 0\r\nConnection: close\r\n\r\n"
            )
            assert ready.wait(6), "SymPy child did not start"
            assert not completed.is_set()
            try:
                with bridge.request_admission_lease():
                    raise AssertionError("Concurrent admission while K=1 occupied")
            except bridge.IsolationCapacityExceeded:
                pass
        assert completed.wait(7), "Disconnect did not finish process cleanup"
        assert cancelled.is_set(), "Real TCP disconnect did not cancel spawned child"
        with bridge.request_admission_lease():
            assert bridge._ADMISSION.acquire(blocking=False) is False
    finally:
        server.should_exit = True
        thread.join(timeout=6)
        listener.close()
        assert not thread.is_alive()
