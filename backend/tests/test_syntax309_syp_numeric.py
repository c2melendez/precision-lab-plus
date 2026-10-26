"""Syntax 309 SY-P: official numeric oracles through the Plus evaluate endpoint.

LaTeX from the source matrix is adapted explicitly to backend syntax. This
verifies backend evaluation, NOT the MathLive-to-backend conversion channel.
Structural/convention rows are intentionally excluded pending separate gates.
"""
import json
import math
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient
from app.main import app

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_sy_p_cases.jsonl"
ROWS = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]

# Backend syntax is not LaTeX. The adapter is explicit and reviewed by ID.
# Never silently modify the source input or its expected value.
EXPRESSIONS = {
    "SY-P-01": "2(3+4)",
    "SY-P-02": "2*pi",
    "SY-P-06": "(-3)^2",
    "SY-P-07": "-3^2",
    "SY-P-08": "2^(3^2)",
    "SY-P-09": "(2^3)^2",
    "SY-P-10": "2^(-1)",
    "SY-P-11": "5-3-1",
    "SY-P-12": "100/10/5",
    "SY-P-13": "2+3*4",
    "SY-P-14": "(2+3)*4",
    "SY-P-15": "-2^2+3",
    "SY-P-16": "+5",
    "SY-P-17": "1-(-1)",
    "SY-P-33": "2*3^2",
}
EXPECTED = {
    "SY-P-01": 14.0, "SY-P-02": 2 * math.pi,
    "SY-P-06": 9.0, "SY-P-07": -9.0, "SY-P-08": 512.0,
    "SY-P-09": 64.0, "SY-P-10": 0.5, "SY-P-11": 1.0,
    "SY-P-12": 2.0, "SY-P-13": 14.0, "SY-P-14": 20.0,
    "SY-P-15": -1.0, "SY-P-16": 5.0, "SY-P-17": 2.0,
    "SY-P-33": 18.0,
}
NUMERIC = [row for row in ROWS if row["operacion"] == "valor"]


def test_syp_numeric_fixture_has_exact_official_ids():
    assert len(ROWS) == 33
    assert len(NUMERIC) == 15
    assert len({row["id"] for row in ROWS}) == 33
    assert {row["id"] for row in NUMERIC} == set(EXPRESSIONS) == set(EXPECTED)
    assert len(ROWS) - len(NUMERIC) == 18


@pytest.mark.parametrize("row", NUMERIC, ids=lambda row: row["id"])
def test_syp_numeric_case_via_evaluate_http(row):
    case_id = row["id"]
    expression = EXPRESSIONS[case_id]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, row["entrada"], expression, data)
    assert data["result_approx"] is not None, (case_id, data)
    assert data["result_approx"] == pytest.approx(EXPECTED[case_id], rel=1e-9, abs=1e-12)
