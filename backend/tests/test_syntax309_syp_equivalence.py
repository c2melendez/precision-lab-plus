"""Syntax 309 SY-P symbolic equivalence through the real Plus HTTP endpoint.

Source IDs SY-P-29..31. This tests sampled mathematical equivalence;
structural echo and convention rows require separate acceptance.
"""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient
from app.main import app

SOURCE = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_sy_p_cases.jsonl"
ROWS = {
    case["id"]: case
    for case in (json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip())
}
# Explicit, traceable translation of the LaTeX source into Plus backend syntax.
CASES = {
    "SY-P-29": ("(x+1)(x-1)", "x^2-1"),
    "SY-P-30": ("x(x+1)", "x^2+x"),
    "SY-P-31": ("2(x)(3)", "6*x"),
}
SAMPLES = ("-3", "-1", "0", "2", "5")


def test_syp_equivalence_fixture_is_official():
    assert set(CASES).issubset(ROWS)
    assert all(ROWS[case_id]["operacion"] == "equivalente" for case_id in CASES)
    assert all(ROWS[case_id]["entrada"] for case_id in CASES)
    assert all(ROWS[case_id]["esperado"] for case_id in CASES)


@pytest.mark.parametrize("case_id", sorted(CASES))
@pytest.mark.parametrize("x", SAMPLES)
def test_syp_equivalence_via_plus_http(case_id, x):
    entered, oracle = CASES[case_id]
    with TestClient(app) as client:
        actual = client.post("/api/v1/evaluate", json={
            "expression": entered, "substitutions": {"x": x},
        })
        expected = client.post("/api/v1/evaluate", json={
            "expression": oracle, "substitutions": {"x": x},
        })
    assert actual.status_code == expected.status_code == 200, (case_id, x)
    got, want = actual.json(), expected.json()
    assert got["success"] is True, (case_id, x, got)
    assert want["success"] is True, (case_id, x, want)
    assert got["result_approx"] is not None, (case_id, x, got)
    assert want["result_approx"] is not None, (case_id, x, want)
    assert got["result_approx"] == pytest.approx(want["result_approx"], rel=1e-9, abs=1e-12)
