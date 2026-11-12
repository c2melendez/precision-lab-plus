"""Trigonometría EC-H-10: tanh(x)=2 no tiene solución real."""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.solve_service import ResultType, solve_equation

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
client = TestClient(app)


def test_ec_h10_source_row_and_no_real_solution_expectation_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-H-10 |" in source
    assert r"\tanh x=2" in source
    assert "sin solución real" in source.lower()


def test_ec_h10_returns_empty_real_solution_set_and_contradiction():
    result = solve_equation("tanh(x)=2", "x")
    assert result.result_type == ResultType.CONTRADICTION
    assert result.solutions == []

    response = client.post(
        "/api/v1/solve",
        json={"equation": "tanh(x)=2", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "contradiction"
    assert not body["result_data"]

    # Independent range check: |tanh(x)| < 1 for every real x.
    for probe in (0, 1, -1, 2, -3, 10):
        assert abs(sp.tanh(probe)) < 1
