"""Syntax309 SY-E first exponent witness: backend route only."""
import json
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}

def test_sye01_braced_two_digit_exponent_explicit_backend():
    """2^10=1024 at backend; original LaTeX 2^{10} is not tested at UI."""
    row = ROWS["SY-E-01"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "2^{10}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2^10"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1024, abs=1e-9)
