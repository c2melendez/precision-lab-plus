"""SY-P structural interpretation witnesses via Plus evaluate HTTP.

Numeric substitution witnesses only; no frontend MathLive or echo certification.
"""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_sy_p_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(s) for s in DATA.read_text(encoding="utf-8").splitlines() if s.strip())}

# Original LaTeX translated explicitly to the Plus backend expression language.
CASES = {
    "SY-P-04": ("2*x^2", {"x": "3"}, 18.0),
    "SY-P-05": ("-x^2", {"x": "3"}, -9.0),
    "SY-P-20": ("(1/2)*x", {"x": "6"}, 3.0),
    "SY-P-22": ("1/(2*x)", {"x": "2"}, 0.25),
    "SY-P-26": ("x^2*y", {"x": "3", "y": "2"}, 18.0),
}


def test_syp_interpretation_source_ids():
    assert all(ROWS[id]["operacion"] == "interpretacion" for id in CASES)


@pytest.mark.parametrize("case_id", list(CASES))
def test_syp_interpretation_numeric_witness_via_http(case_id):
    expression, substitutions, expected = CASES[case_id]
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/evaluate",
            json={"expression": expression, "substitutions": substitutions},
        )
    assert response.status_code == 200, (case_id, response.text)
    body = response.json()
    assert body["success"] is True, (case_id, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


# These tests intentionally send concatenated variables to the real parser.
# Rewriting xy as x*y in the fixture would bypass the behavior under audit.
@pytest.mark.parametrize(
    "case_id,expression,substitutions,expected",
    [
        ("SY-P-24", "xy", {"x": "2", "y": "3"}, 6.0),
        ("SY-P-25", "xyz", {"x": "2", "y": "3", "z": "5"}, 30.0),
    ],
)
def test_syp_concatenated_variables_via_http(case_id, expression, substitutions, expected):
    assert ROWS[case_id]["operacion"] == "interpretacion"
    assert ROWS[case_id]["entrada"] == expression
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/evaluate",
            json={"expression": expression, "substitutions": substitutions},
        )
    assert response.status_code == 200, (case_id, response.text)
    body = response.json()
    assert body["success"] is True, (case_id, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)
