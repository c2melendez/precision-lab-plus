"""SG28/H2: real loopback TCP disconnect observed by ASGI outer middleware.

Runs a disposable Uvicorn server inside CI. No production endpoint or isolation
feature flag is touched. This covers the transport signal, not fleet admission.
"""
import socket
import threading
import time

from app.services.disconnect_tracking import DisconnectTrackingMiddleware


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
