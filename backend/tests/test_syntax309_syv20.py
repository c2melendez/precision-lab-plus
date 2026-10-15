"""SY-V-20: symbolic binomial identity, domain and HTTP reentry."""
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


def test_syv20_symbolic_binomial_general_identity_domain_and_reentry():
    row = ROWS["SY-V-20"]
    assert row["entrada"] == r"\binom{n}{2}"
    assert row["operacion"] == "equivalente" and row["esperado"] == r"\frac{n(n-1)}{2}"
    n = sp.Symbol("n")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "nCr(n,2)"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["operation"] == "evaluate", data
        assert data["result_type"] == "scalar" and data["result_approx"] is None, data
        assert data["request_id"] and data["error_code"] is None, data
        assert "binomial" not in data["result_text"] and "nCr" not in data["result_text"], data
        value = sp.sympify(data["result_text"].replace("^", "**"))
        assert value.free_symbols == {n}
        assert sp.simplify(value - n*(n-1)/2) == 0
        assert value.subs(n, 0) == 0 and value.subs(n, 1) == 0
        assert sp.simplify(value.subs(n, n+1) - value - n) == 0
        assert any("n" in w and "entero no negativo" in w for w in data["warnings"]), data
        for count in [2, 3, 5, 10]:
            independent_pairs = sum(1 for a in range(count) for b in range(a+1, count))
            assert value.subs(n, count) == independent_pairs
        repeat = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeat.status_code == 200, repeat.text
        again = repeat.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["request_id"] != data["request_id"], again
        assert sp.simplify(sp.sympify(again["result_text"]) - value) == 0


def test_syv20_binomial_substitution_domain_is_not_silently_generalized():
    with TestClient(app) as client:
        for raw, expected in [("0", 0), ("1", 0), ("5", 10), ("10", 45)]:
            response = client.post("/api/v1/evaluate", json={
                "expression": "nCr(n,2)", "substitutions": {"n": raw}})
            assert response.status_code == 200, response.text
            data = response.json()
            MathResponse.model_validate(data)
            assert data["success"] is True and sp.sympify(data["result_text"]) == expected, data
        for raw in ["-1", "1/2"]:
            data = client.post("/api/v1/evaluate", json={
                "expression": "nCr(n,2)", "substitutions": {"n": raw}}).json()
            MathResponse.model_validate(data)
            assert data["success"] is False and data["error_code"] == "DOMAIN_ERROR", data
