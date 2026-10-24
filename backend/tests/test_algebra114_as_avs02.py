"""Algebra114 AS-AVS-02: |xy| equals |x||y| over the reals."""
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_avs_02_absolute_product_service_and_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(
        encoding="utf-8"
    )
    assert "| AS-AVS-02 | N2 | \\(|xy|\\) | \\(|x||y|\\) |" in source
    original = "abs(x*y)"
    x, y = sp.symbols("x y")
    expected = sp.Abs(x) * sp.Abs(y)
    samples = [(-3, 2), (-1, -4), (0, 5), (2, 7), (-2.5, -0.5)]

    service = simplify_expression(original)
    assert service.result_expr == expected
    for xv, yv in samples:
        value = float(sp.N(service.result_expr.subs({x: xv, y: yv})))
        assert abs(value - abs(xv) * abs(yv)) < 1e-12

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    observed = sp.sympify(payload["result_text"])
    assert observed == expected
    for xv, yv in samples:
        value = float(sp.N(observed.subs({x: xv, y: yv})))
        assert abs(value - abs(xv) * abs(yv)) < 1e-12
