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
from app.services.rate_limit import (
    FixedWindowRateLimiter,
    client_key,
    is_exempt_path,
)
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

# EN-SG-32: one limiter per process, disabled unless RATE_LIMIT_REQUESTS > 0.
# Tests replace it through `app.state.rate_limiter`; nothing else mutates it.
app.state.rate_limiter = FixedWindowRateLimiter(
    requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
    trust_forwarded_for=settings.rate_limit_trust_forwarded_for,
)

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
    # EN-SG-32: opt-in throttling before routing, body reading and validation.
    limiter = getattr(request.app.state, "rate_limiter", None)
    rate_decision = None
    # CORS preflight is not client traffic: throttling it would turn a burst
    # into an apparent CORS failure instead of a 429.
    throttled_request = request.method != "OPTIONS" and not is_exempt_path(
        request.url.path
    )
    if limiter is not None and limiter.enabled and throttled_request:
        rate_decision = limiter.check(
            client_key(request, limiter.trust_forwarded_for)
        )
        if not rate_decision.allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "request_id": request.state.request_id,
                    "error_code": "RATE_LIMITED",
                    "error_message": (
                        "Demasiadas solicitudes en la ventana actual; "
                        "reintente mas tarde."
                    ),
                },
                headers={
                    "X-Request-ID": request.state.request_id,
                    "Retry-After": str(max(int(rate_decision.retry_after + 0.999), 1)),
                    "X-RateLimit-Limit": str(rate_decision.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(max(int(rate_decision.reset_after + 0.999), 1)),
                    "X-Content-Type-Options": "nosniff",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                    "X-Frame-Options": "DENY",
                },
            )

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
    if rate_decision is not None:
        response.headers["X-RateLimit-Limit"] = str(rate_decision.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_decision.remaining)
        response.headers["X-RateLimit-Reset"] = str(
            max(int(rate_decision.reset_after + 0.999), 1)
        )
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
