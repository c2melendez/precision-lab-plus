"""AS-PF-05 improper fraction: exact quotient and original domain exclusions."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_05_improper_fraction_service_http_and_original_domain():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-05 | N3 |" in source
    x = sp.Symbol("x")
    original = "(x**3+1)/(x**2-1)"
    expected = x+1/(x-1)
    domain_exclusions = {sp.Integer(-1), sp.Integer(1)}
    # Preserve domain from the *original* expression, not cancelled result.
    assert set(sp.solve(sp.denom(sp.sympify(original)), x)) == domain_exclusions
    service = partial_fraction_expression(original)
    assert sp.cancel(service.result_expr-expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.cancel(sp.sympify(payload["result_text"])-expected) == 0
