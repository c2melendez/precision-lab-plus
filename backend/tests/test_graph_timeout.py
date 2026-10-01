"""Regression coverage for graph analysis that used to block the API."""
import os
import threading
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from fastapi.testclient import TestClient
from app.core.math_timeout import run_math_operation
from app.main import app


def _graph_with_stalled_range():
    from app.services import graph_service

    def stalled_range(*args, **kwargs):
        while True:
            pass

    graph_service.function_range = stalled_range
    graph_service._TOTAL_ANALYSIS_BUDGET_S = 0.2
    return graph_service.compute_graph(["x+1"], "x", -1, 1, 51)


def test_stalled_analysis_retains_curve_and_does_not_leak_into_next_request():
    from app.services import graph_service

    # Exercise the real process boundary and inner alarm. The old executor
    # waited forever on shutdown, so the outer 5s guard raised TimeoutError.
    result = run_math_operation(_graph_with_stalled_range, timeout_s=5)
    trace = result.graph_data.traces[0]
    assert len(trace.x) == 51
    assert all(abs(y - (x + 1)) < 1e-9 for x, y in zip(trace.x, trace.y))
    assert result.graph_data.analysis[0].domain_text is not None
    assert result.graph_data.analysis[0].range_text is None
    next_result = run_math_operation(
        graph_service.compute_graph, ["x"], "x", -1, 1, 51, timeout_s=5
    )
    assert len(next_result.graph_data.traces[0].x) == 51
    assert next_result.graph_data.analysis[0].range_text is not None


def test_graph_timeout_does_not_block_health_and_next_graph_succeeds(monkeypatch):
    from app.routers import graphing

    entered = threading.Event()
    release = threading.Event()

    def stalled_operation(*args, **kwargs):
        entered.set()
        if not release.wait(timeout=5):
            raise AssertionError("Test did not release graph operation.")
        raise TimeoutError("Controlled graph timeout.")

    with monkeypatch.context() as scoped:
        scoped.setattr(graphing, "run_math_operation", stalled_operation)
        with TestClient(app) as shared_client, ThreadPoolExecutor(max_workers=2) as pool:
            graph = pool.submit(
                shared_client.post, "/api/v1/graph/2d",
                json={"expressions": ["x"], "samples": 51},
            )
            try:
                assert entered.wait(timeout=3)
                health = pool.submit(shared_client.get, "/api/v1/health")
                assert health.result(timeout=1).status_code == 200
            finally:
                release.set()
            body = graph.result(timeout=3).json()
            assert body["success"] is False
            assert body["error_code"] == "TIMEOUT"
            assert body["operation"] == "graph_2d"

    with TestClient(app) as recovered_client:
        response = recovered_client.post(
            "/api/v1/graph/2d", json={"expressions": ["x"], "samples": 51}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
