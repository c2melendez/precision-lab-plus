"""S20 — rendimiento y robustez backend Plus.

Primera corrida: genera baseline del runner, no impone umbrales porcentuales
arbitrarios. Sí bloquea semántica incorrecta, hangs duros y rutas que exceden
el presupuesto de seguridad de la propia prueba.
"""

from __future__ import annotations

import json
import os
import platform
import resource
import signal
import statistics
import time
from pathlib import Path
from typing import Any, Callable

from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from app.main import app  # noqa: E402


REPORT_DIR = Path(__file__).resolve().parents[2] / "reports" / "s20"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = REPORT_DIR / "backend-performance.json"

HARD_BUDGET_S = 5.0
SHORT_REPETITIONS = 25


class HardTimeout(RuntimeError):
    pass


def _alarm_handler(_signum, _frame):
    raise HardTimeout(f"Operación excedió el presupuesto duro de {HARD_BUDGET_S:.1f}s")


def timed(fn: Callable[[], Any]) -> tuple[Any, float]:
    old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.setitimer(signal.ITIMER_REAL, HARD_BUDGET_S)
    started = time.perf_counter()
    try:
        result = fn()
        elapsed_ms = (time.perf_counter() - started) * 1000
        return result, elapsed_ms
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def percentile_nearest_rank(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) * q) + 0.999999) - 1))
    return ordered[index]


def cpu_model() -> str | None:
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


def total_ram_bytes() -> int | None:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024
    except OSError:
        return None
    return None


client = TestClient(app, raise_server_exceptions=False)


def post(path: str, payload: dict[str, Any]):
    return client.post(f"/api/v1{path}", json=payload)


def assert_success(response, label: str):
    body = response.json()
    assert response.status_code == 200, f"{label}: HTTP {response.status_code}: {body}"
    assert body.get("success") is True, f"{label}: {body}"
    return body


def assert_complexity(response, label: str):
    body = response.json()
    assert response.status_code == 200, f"{label}: HTTP {response.status_code}: {body}"
    assert body.get("success") is False, f"{label}: esperaba error controlado: {body}"
    assert body.get("error_code") == "COMPLEXITY_LIMIT", f"{label}: {body}"
    return body


def main() -> None:
    short_cases = ["2+2", "3+4", "6*7", "9-5", "8/2"]
    samples: list[float] = []
    for i in range(SHORT_REPETITIONS):
        expr = short_cases[i % len(short_cases)]
        response, elapsed = timed(lambda e=expr: post("/evaluate", {"expression": e, "angle_unit": "rad"}))
        assert_success(response, f"short:{expr}")
        samples.append(elapsed)

    large_expr = "+".join(["1"] * 200)  # 399 chars, cerca del máximo contractual 500.
    large_response, large_ms = timed(
        lambda: post("/evaluate", {"expression": large_expr, "angle_unit": "rad"})
    )
    large_body = assert_success(large_response, "large-expression")
    assert large_body.get("result_approx") == 200

    sum100k_response, sum100k_ms = timed(
        lambda: post("/evaluate", {"expression": "sum(i,i,1,100000)", "angle_unit": "rad"})
    )
    assert_complexity(sum100k_response, "sum-100k")

    product100k_response, product100k_ms = timed(
        lambda: post("/evaluate", {"expression": "product(i,i,1,100000)", "angle_unit": "rad"})
    )
    assert_complexity(product100k_response, "product-100k")

    sum10k_response, sum10k_ms = timed(
        lambda: post("/evaluate", {"expression": "sum(i,i,1,10000)", "angle_unit": "rad"})
    )
    sum10k_body = assert_success(sum10k_response, "sum-10k")
    assert str(sum10k_body.get("result_text")) == "50005000", sum10k_body

    product10k_response, product10k_ms = timed(
        lambda: post("/evaluate", {"expression": "product(1,i,1,10000)", "angle_unit": "rad"})
    )
    product10k_body = assert_success(product10k_response, "product-10k")
    assert str(product10k_body.get("result_text")) == "1", product10k_body

    matrix = [
        ["2", "1", "3", "4", "5", "6"],
        ["0", "3", "2", "1", "4", "5"],
        ["0", "0", "5", "2", "1", "3"],
        ["0", "0", "0", "7", "2", "1"],
        ["0", "0", "0", "0", "11", "4"],
        ["0", "0", "0", "0", "0", "13"],
    ]
    matrix_response, matrix_ms = timed(lambda: post("/matrix/determinant", {"matrix": matrix}))
    matrix_body = assert_success(matrix_response, "matrix-6x6")
    assert "30030" in str(matrix_body.get("result_text") or matrix_body.get("result_latex"))

    values = [float(i) for i in range(1, 201)]
    stats_response, stats_ms = timed(
        lambda: post(
            "/statistics/descriptive",
            {"values": values, "stat": "mean", "variance_kind": "population"},
        )
    )
    stats_body = assert_success(stats_response, "statistics-200")
    assert abs(float(stats_body.get("result_approx")) - 100.5) < 1e-9

    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report = {
        "schema_version": 1,
        "module": "S20",
        "plus_sha": os.getenv("GITHUB_SHA"),
        "lite_sha": os.getenv("S20_LITE_SHA"),
        "runner": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "cpu_model": cpu_model(),
            "ram_total_bytes": total_ram_bytes(),
            "process_max_rss_bytes": rss_kb * 1024,
        },
        "short_route": {
            "repetitions": SHORT_REPETITIONS,
            "median_ms": statistics.median(samples),
            "p95_ms": percentile_nearest_rank(samples, 0.95),
            "max_ms": max(samples),
            "samples_ms": samples,
        },
        "sentinels": {
            "large_expression_ms": large_ms,
            "sum_100000": {"outcome": "COMPLEXITY_LIMIT", "elapsed_ms": sum100k_ms},
            "product_100000": {"outcome": "COMPLEXITY_LIMIT", "elapsed_ms": product100k_ms},
            "sum_10000": {"outcome": "success", "elapsed_ms": sum10k_ms, "result": "50005000"},
            "product_10000": {"outcome": "success", "elapsed_ms": product10k_ms, "result": "1"},
            "matrix_6x6_determinant_ms": matrix_ms,
            "statistics_200_mean_ms": stats_ms,
        },
        "hard_budget_seconds": HARD_BUDGET_S,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
