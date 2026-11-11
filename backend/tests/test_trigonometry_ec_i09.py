"""Trigonometría EC-I-09: asin(x)=2 no tiene solución real."""
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


def test_ec_i09_source_row_and_no_real_solution_expectation_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-I-09 |" in source
    assert r"\arcsin x=2" in source
    assert "sin solución real" in source.lower()


def test_ec_i09_returns_empty_real_solution_set_and_contradiction():
    result = solve_equation("asin(x)=2", "x")
    assert result.result_type == ResultType.CONTRADICTION
    assert result.solutions == []

    response = client.post(
        "/api/v1/solve",
        json={"equation": "asin(x)=2", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "contradiction"
    assert not body["result_data"]

    # Independent range check: arcsin is bounded by [-pi/2, pi/2] on the reals.
    for probe in (0, 1, -1, sp.Rational(1, 2), sp.Rational(-1, 2)):
        value = sp.asin(probe)
        assert -sp.pi / 2 <= value <= sp.pi / 2
