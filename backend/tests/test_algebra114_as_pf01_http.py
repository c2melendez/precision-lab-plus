"""AS-PF-01 end-to-end API test; UI exposure tracked separately."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app


def test_as_pf_01_http_partial_fractions():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-01 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": "(3*x+5)/((x+1)*(x+2))"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "partial_fractions"
    x = sp.Symbol("x")
    actual = sp.sympify(result["result_text"])
    assert sp.cancel(actual - (2/(x+1)+1/(x+2))) == 0
    assert actual.is_Add and len(actual.args) == 2
