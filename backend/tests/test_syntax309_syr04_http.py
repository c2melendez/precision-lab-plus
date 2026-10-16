"""SY-R-04 original Spanish binding, exact MathResponse and text reentry."""
import os
import math
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

OFFICIAL = r"e^{-x^{2}}\ \text{con}\ x=1"

@pytest.mark.parametrize("payload, exact", [
    ({"expression": OFFICIAL}, sp.exp(-1)),
    ({"expression": "e^(-x^2)", "substitutions": {"x": "1"}}, sp.exp(-1)),
    ({"expression": "e^{-x^{2}} con x=2"}, sp.exp(-4)),
    ({"expression": "e^{-y^{2}} con y=-1"}, sp.exp(-1)),
    ({"expression": "2^{-x^{2}} con x=1"}, sp.Rational(1, 2)),
    ({"expression": "(e^(-x^2)) con x=(1)"}, sp.exp(-1)),
    ({"expression": "(2^(-y^2)) con y=(-2)"}, sp.Rational(1, 16)),
])
def test_syr04_source_exact_value_and_reentry(payload, exact):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={**payload, "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success and result.result_type.value == "scalar", result
        actual = sp.sympify(result.result_text)
        assert sp.simplify(actual - exact) == 0 and not actual.has(sp.Float), result
        assert result.result_approx is not None and math.isfinite(result.result_approx), result
        expected = float(exact)
        assert abs(result.result_approx - expected) <= 1e-9 * abs(expected), result
        if payload["expression"] == OFFICIAL:
            assert abs(result.result_approx - 0.3678794412) <= 1e-9 * 0.3678794412
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        assert again.status_code == 200, again.text
        restored = MathResponse.model_validate(again.json())
        assert restored.success and sp.simplify(sp.sympify(restored.result_text) - exact) == 0, restored

@pytest.mark.parametrize("payload", [
    {"expression": "x+1 con x=y"},
    {"expression": "x+1 con x=1/0"},
    {"expression": "x+1 con x=1", "substitutions": {"x": "2"}},
])
def test_syr04_rejects_non_numeric_non_finite_or_conflicting_bindings(payload):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json=payload)
        result = MathResponse.model_validate(response.json())
        assert not result.success, result
        assert result.error_code.value == "VALIDATION_ERROR" and result.error_message, result


def test_syr04_complete_mathresponse_parity_isolation_off_on(monkeypatch):
    snapshots = []
    for enabled in ("0", "1"):
        monkeypatch.setenv("SG28_EVALUATE_ISOLATION", enabled)
        with TestClient(app) as client:
            response = client.post("/api/v1/evaluate", json={"expression": OFFICIAL, "angle_unit": "rad"})
            assert response.status_code == 200, response.text
            result = MathResponse.model_validate(response.json())
            assert result.success, result
            assert result.input_text == OFFICIAL and result.input_latex is not None, result
            assert abs(result.result_approx - 0.3678794412) <= 1e-9 * 0.3678794412, result
            snapshots.append(result.model_dump(exclude={"request_id", "duration_ms"}))
    assert snapshots[0] == snapshots[1]
