"""Algebra114 AS-FAC-08 original Sophie Germain factorization via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app


def test_as_fac_08_sophie_germain_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-08 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**4+4"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x")
    actual = sp.sympify(payload["result_text"])
    expected = (x*x - 2*x + 2)*(x*x + 2*x + 2)
    assert sp.simplify(actual - expected) == 0
    assert set(sp.factor_list(actual)[1]) == {(x*x - 2*x + 2, 1), (x*x + 2*x + 2, 1)}
