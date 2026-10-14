"""SY-E-17: declared default principal complex branch through Plus HTTP."""
import json
import math
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
import sympy
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}

def test_sye17_default_principal_complex_power_http_and_response():
    row = ROWS["SY-E-17"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == "(-2)^{0.5}"
    assert "ℂ" in row["esperado"]
    expression = "(-2)^0.5"  # Explicit backend translation; original MathLive UI is separate.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    data = response.json()
    MathResponse.model_validate(data)
    assert data["success"] is True, data
    assert data["operation"] == "evaluate", data
    assert data["request_id"], data
    assert data["result_type"] == "scalar", data
    assert data["input_text"] == expression, data
    assert data["result_approx"] is None, data
    assert data["error_code"] is None and data["error_message"] is None, data
    assert isinstance(data["steps"], list) and isinstance(data["warnings"], list), data
    assert isinstance(data["has_detailed_steps"], bool), data
    assert math.isfinite(data["duration_ms"]) and data["duration_ms"] >= 0, data
    assert isinstance(data["result_latex"], str) and "i" in data["result_latex"], data
    assert isinstance(data["result_text"], str) and "I" in data["result_text"], data
    # Only parse returned notation; expected coordinates are independent constants.
    represented = sympy.sympify(data["result_text"], locals={"I": sympy.I, "sqrt": sympy.sqrt})
    assert not represented.free_symbols, data
    actual = complex(represented.evalf(17))
    assert math.isfinite(actual.real) and math.isfinite(actual.imag), data
    assert actual.real == pytest.approx(0, abs=1e-12), data
    assert actual.imag > 0, data
    assert actual.imag == pytest.approx(1.4142135623730951, rel=1e-12, abs=1e-12), data
    squared = actual * actual
    assert squared.real == pytest.approx(-2, abs=1e-12), data
    assert squared.imag == pytest.approx(0, abs=1e-12), data
