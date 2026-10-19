"""AS-RAT-02 exact conjugate rationalization via simplify service/HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_02_conjugate_rationalization():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-02 | N1 |" in source
    original = "1/(sqrt(2)+1)"
    expected = sp.sqrt(2)-1
    service = simplify_expression(original)
    assert sp.simplify(service.result_expr-expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"])-expected) == 0
