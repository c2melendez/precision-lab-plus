"""SY-V-17: closed form, natural-number domain and HTTP reentry."""
import json
import os
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {v["id"]: v for v in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}


def test_syv17_symbolic_closed_form_general_identity_and_reentry():
    row = ROWS["SY-V-17"]
    assert row["entrada"] == r"\sum_{k=1}^{n}k"
    assert row["operacion"] == "equivalente"
    assert row["esperado"] == r"\frac{n(n+1)}{2}"
    expression = "sum(k,k,1,n)"  # Original converter is tested independently.
    n = sp.Symbol("n")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["operation"] == "evaluate", data
        assert data["result_type"] == "scalar" and data["input_text"] == expression, data
        assert data["request_id"] and data["result_approx"] is None, data
        assert data["error_code"] is None and data["error_message"] is None, data
        assert any("n" in w and "entero no negativo" in w for w in data["warnings"]), data
        value = sp.sympify(data["result_text"].replace("^", "**"))
        assert value.free_symbols == {n}, data
        assert sp.simplify(value - n*(n+1)/2) == 0, data
        # Base and recurrence establish the general natural-number identity.
        assert value.subs(n, 0) == 0
        assert sp.simplify(value.subs(n, n+1) - value - (n+1)) == 0
        for count in [0, 1, 2, 10, 20]:
            assert value.subs(n, count) == sum(range(1, count+1))
        repeat = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeat.status_code == 200, repeat.text
        again = repeat.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["request_id"] != data["request_id"], again
        assert sp.simplify(sp.sympify(again["result_text"]) - value) == 0, again


def test_syv17_scope_domain_substitutions_and_finite_range_guard():
    with TestClient(app) as client:
        renamed = client.post("/api/v1/evaluate", json={"expression": "sum(j,j,1,m)"}).json()
        MathResponse.model_validate(renamed)
        assert renamed["success"] is True, renamed
        m = sp.Symbol("m")
        assert sp.simplify(sp.sympify(renamed["result_text"]) - m*(m+1)/2) == 0
        for raw, expected in [("0", 0), ("10", 55), ("1000000", 500000500000)]:
            response = client.post("/api/v1/evaluate", json={
                "expression": "sum(k,k,1,n)", "substitutions": {"n": raw}})
            assert response.status_code == 200, response.text
            body = response.json()
            MathResponse.model_validate(body)
            assert body["success"] is True, body
            assert sp.sympify(body["result_text"]) == expected, body
        for raw in ["-1", "1/2"]:
            body = client.post("/api/v1/evaluate", json={
                "expression": "sum(k,k,1,n)", "substitutions": {"n": raw}}).json()
            MathResponse.model_validate(body)
            assert body["success"] is False and body["error_code"] == "DOMAIN_ERROR", body
        for source in ["sum(k^2,k,1,n)", "sum(k,k,2,n)", "sum(k,k,1,k)"]:
            body = client.post("/api/v1/evaluate", json={"expression": source}).json()
            MathResponse.model_validate(body)
            assert body["success"] is False, body
        guard = client.post("/api/v1/evaluate", json={"expression": "sum(k,k,1,10002)"}).json()
        MathResponse.model_validate(guard)
        assert guard["success"] is False and guard["error_code"] == "COMPLEXITY_LIMIT", guard
