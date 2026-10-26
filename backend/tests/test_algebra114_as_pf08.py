"""Algebra114 AS-PF-08 improper rational and original excluded points."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_08_improper_fraction_service_http_domain():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-08 | N3 |" in source
    x = sp.Symbol("x")
    original = "x**4/(x**2-1)"
    expected = x**2+1+sp.Rational(1,2)/(x-1)-sp.Rational(1,2)/(x+1)
    # Exclusions derive from the original denominator, never cancelled terms.
    assert set(sp.solve(sp.denom(sp.sympify(original)), x)) == {-1, 1}
    service = partial_fraction_expression(original)
    assert sp.cancel(service.result_expr-expected) == 0
    assert service.result_expr.is_Add and len(service.result_expr.args) >= 3
    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.cancel(actual-expected) == 0
    assert actual.is_Add and len(actual.args) >= 3
