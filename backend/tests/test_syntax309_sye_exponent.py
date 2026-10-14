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


def test_sye02_ascii_two_digit_exponent_backend_http():
    """SY-E-02 original ASCII 2^10 must be 1024, not 2^1 * 0."""
    row = ROWS["SY-E-02"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "2^10"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1024, abs=1e-9)


def test_sye03_power_with_explicit_substitution_http():
    """SY-E-03: translated power and substitution; natural-language LaTeX annotation not tested in UI."""
    row = ROWS["SY-E-03"]
    assert row["operacion"] == "valor"
    assert "x^{12}" in row["entrada"] and "x=2" in row["entrada"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "x^12", "substitutions": {"x": "2"}
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(4096, abs=1e-9)


def test_sye04_negative_exponent_http():
    """SY-E-04 explicit backend power only, not source LaTeX UI."""
    row = ROWS["SY-E-04"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "10^{-3}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "10^(-3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(0.001, abs=1e-12)
