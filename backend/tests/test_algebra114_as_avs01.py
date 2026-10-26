"""Algebra114 AS-AVS-01: |x|^2 simplifies to x^2 over the reals."""
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_avs_01_absolute_square_service_and_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(
        encoding="utf-8"
    )
    assert "| AS-AVS-01 | N1 | \\(|x|^{2}\\) | \\(x^{2}\\) |" in source
    original = "abs(x)**2"
    expected = sp.Symbol("x") ** 2

    service = simplify_expression(original)
    assert service.result_expr == expected
    assert not service.result_expr.has(sp.Abs)

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    observed = sp.sympify(payload["result_text"])
    assert observed == expected
    assert "Abs" not in payload["result_text"]
    for value in (-5, -1, 0, 2, 7):
        assert observed.subs(sp.Symbol("x"), value) == value * value
