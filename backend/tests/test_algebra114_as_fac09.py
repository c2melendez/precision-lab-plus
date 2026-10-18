"""AS-FAC-09: original x^4+1 real-domain factorization, not rational irreducibility."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app


def test_as_fac_09_real_irrational_quadratic_factors_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-09 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**4+1"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x")
    actual = sp.sympify(payload["result_text"])
    left = x*x + sp.sqrt(2)*x + 1
    right = x*x - sp.sqrt(2)*x + 1
    assert sp.expand(actual - (left*right)) == 0
    # Equivalence alone would also accept the unfactored x**4+1.
    assert actual.is_Mul, f"Real factorization missing: {actual}"
    assert {sp.expand(f) for f in actual.args} == {left, right}
