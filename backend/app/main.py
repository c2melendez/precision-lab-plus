"""
Punto de entrada de la aplicación FastAPI (spec, sección 9):

- Middleware de request_id/start_time ANTES de cualquier validación.
- CORS desde CORS_ORIGINS (env), nunca "*" con allow_credentials=True.
- Prefijo /api/v1.
- GET /api/v1/health -> {"status": "ok"}.
"""

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import API_V1_PREFIX, get_settings
from app.core.exception_handlers import (
    generic_exception_handler,
    timeout_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.services.disconnect_tracking import DisconnectTrackingMiddleware
from app.routers import (
    algebra,
    calculus,
    complex_analysis,
    evaluate,
    graphing,
    health,
    matrices,
    matrix_spaces,
    ode,
    phase2,
    statistics,
)

configure_logging()

app = FastAPI(
    title="Calculadora Científica Web",
    version="0.1.0",
    openapi_url=f"{API_V1_PREFIX}/openapi.json",
    docs_url=f"{API_V1_PREFIX}/docs",
    redoc_url=f"{API_V1_PREFIX}/redoc",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Genera request_id/start_time ANTES de cualquier validación posterior."""
    request.state.request_id = str(uuid.uuid4())
    request.state.start_time = time.perf_counter()
    declared_size = request.headers.get("content-length")
    if request.method in {"POST", "PUT", "PATCH"} and declared_size is not None:
        try:
            oversized = int(declared_size) > 1024 * 1024
        except ValueError:
            oversized = False
        if oversized:
            return JSONResponse(
                status_code=413,
                content={"success": False, "request_id": request.state.request_id,
                         "error_code": "PAYLOAD_TOO_LARGE",
                         "error_message": "El cuerpo de la solicitud supera el límite de 1 MiB."},
                headers={"X-Request-ID": request.state.request_id},
            )
    if request.method in {"POST", "PUT", "PATCH"} and declared_size is None:
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 1024 * 1024:
                return JSONResponse(
                    status_code=413,
                    content={"success": False, "request_id": request.state.request_id,
                             "error_code": "PAYLOAD_TOO_LARGE",
                             "error_message": "El cuerpo de la solicitud supera el límite de 1 MiB."},
                    headers={"X-Request-ID": request.state.request_id},
                )
        request._body = bytes(body)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"

    path = request.url.path
    if path.startswith(API_V1_PREFIX) and not (
        path.endswith("/docs")
        or path.endswith("/redoc")
        or path.endswith("/openapi.json")
    ):
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; "
            "base-uri 'none'; form-action 'none'"
        )
    return response


app.add_middleware(DisconnectTrackingMiddleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(TimeoutError, timeout_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(evaluate.router, prefix=API_V1_PREFIX)
app.include_router(algebra.router, prefix=API_V1_PREFIX)
app.include_router(calculus.router, prefix=API_V1_PREFIX)
app.include_router(matrices.router, prefix=API_V1_PREFIX)
app.include_router(matrix_spaces.router, prefix=API_V1_PREFIX)
app.include_router(graphing.router, prefix=API_V1_PREFIX)
app.include_router(phase2.router, prefix=API_V1_PREFIX)
app.include_router(statistics.router, prefix=API_V1_PREFIX)
app.include_router(ode.router, prefix=API_V1_PREFIX)
app.include_router(complex_analysis.router, prefix=API_V1_PREFIX)
