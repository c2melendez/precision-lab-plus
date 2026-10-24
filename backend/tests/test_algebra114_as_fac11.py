"""Algebra114 AS-FAC-11 original grouping factorization via real HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app


def test_as_fac_11_grouping_factorization_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-11 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**3+x**2+x+1"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x")
    actual = sp.sympify(payload["result_text"])
    expected = (x + 1)*(x*x + 1)
    assert sp.expand(actual - expected) == 0
    assert set(sp.factor_list(actual)[1]) == {(x + 1, 1), (x*x + 1, 1)}
