"""SG28: observe ASGI http.disconnect regardless of intermediate middleware consumers.

The event lives in the shared ASGI scope so a downstream request cancellation
bridge can see disconnects even if BaseHTTPMiddleware reads the message first.
No background reader is started and body-stream ownership is unchanged.
"""
from __future__ import annotations

import asyncio


class DisconnectTrackingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        event = asyncio.Event()
        scope["sg28_http_disconnected"] = event

        async def tracked_receive():
            message = await receive()
            if message["type"] == "http.disconnect":
                event.set()
            return message

        await self.app(scope, tracked_receive, send)
