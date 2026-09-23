"""S17 — API fuzzing/control de errores para Precision Lab Plus.

Objetivo:
- REG-011: csc(0) debe responder de forma controlada, nunca 500.
- REG-012: rutas de linsolve (/solve/system) deben manejar sistemas
  inconsistentes/indeterminados sin excepción cruda.
- Fuzzing determinista de payloads hostiles y límites de esquema.
"""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from hypothesis import given, seed, settings, strategies as st
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _assert_no_internal_leak(response):
    assert response.status_code != 500, response.text
    text = response.text.lower()
    for forbidden in (
        "traceback",
        "sympifyerror",
        "tokenerror",
        "typeerror",
        "zerodivisionerror",
        "internal server error",
    ):
        assert forbidden not in text, response.text


def _post(path, payload):
    response = client.post(path, json=payload)
    _assert_no_internal_leak(response)
    return response


def test_s17_reg011_csc_zero_is_controlled_domain_error():
    response = _post("/api/v1/evaluate", {"expression": "csc(0)", "angle_unit": "rad"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"
    assert body["request_id"]


@pytest.mark.parametrize(
    "expression",
    [
        "sec(pi/2)",
        "tan(pi/2)",
        "cot(0)",
    ],
)
def test_s17_related_trig_poles_never_crash(expression):
    response = _post("/api/v1/evaluate", {"expression": expression, "angle_unit": "rad"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"


def test_s17_reg012_linsolve_inconsistent_system_is_controlled():
    response = _post(
        "/api/v1/solve/system",
        {
            "equations": ["x+y=1", "x+y=2"],
            "variables": ["x", "y"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["result_data"] == []
    assert any("no tiene solución" in w.lower() for w in body["warnings"])


def test_s17_reg012_linsolve_indeterminate_system_is_controlled():
    response = _post(
        "/api/v1/solve/system",
        {
            "equations": ["x+y=1", "2*x+2*y=2"],
            "variables": ["x", "y"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["result_data"]) >= 1
    assert body["request_id"]


@pytest.mark.parametrize(
    "payload",
    [
        {"expression": "__import__('os')"},
        {"expression": "eval(1)"},
        {"expression": "Integral(x,x)"},
        {"expression": "foo.bar"},
        {"expression": "a" * 65},
        {"expression": "2**100000000"},
    ],
)
def test_s17_evaluate_hostile_payloads_are_controlled(payload):
    response = _post("/api/v1/evaluate", payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] in {"PARSE_ERROR", "COMPLEXITY_LIMIT"}


@pytest.mark.parametrize(
    "payload",
    [
        {
            "equations": ["eval(1)=0", "y=1"],
            "variables": ["x", "y"],
        },
        {
            "equations": ["x+y=1", "__import__('os')=0"],
            "variables": ["x", "y"],
        },
        {
            "equations": ["x+y=1", "2*x+2*y=2"],
            "variables": ["x", "__import__"],
        },
    ],
)
def test_s17_system_hostile_payloads_are_controlled(payload):
    response = _post("/api/v1/solve/system", payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}


@pytest.mark.parametrize(
    "path,payload",
    [
        ("/api/v1/evaluate", {}),
        ("/api/v1/evaluate", {"expression": ""}),
        ("/api/v1/evaluate", {"expression": "1", "angle_unit": "grad"}),
        ("/api/v1/solve/system", {"equations": ["x=1"], "variables": ["x"]}),
        (
            "/api/v1/solve/system",
            {
                "equations": ["x=1", "y=2", "z=3", "a=4", "b=5", "c=6", "d=7"],
                "variables": ["x", "y", "z", "a", "b", "c", "d"],
            },
        ),
    ],
)
def test_s17_schema_fuzzing_returns_422_not_500(path, payload):
    response = _post(path, payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Hypothesis dirigido — seed reproducible del módulo S17
# ---------------------------------------------------------------------------

S17_HYPOTHESIS_SEED = 170017


@seed(S17_HYPOTHESIS_SEED)
@settings(max_examples=40, deadline=None, database=None)
@given(
    a=st.integers(min_value=-1000, max_value=1000),
    b=st.integers(min_value=-1000, max_value=1000),
)
def test_s17_hypothesis_integer_addition_matches_arithmetic(a, b):
    response = _post("/api/v1/evaluate", {"expression": f"{a}+({b})"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True, body
    assert float(body["result_approx"]) == pytest.approx(float(a + b))


@seed(S17_HYPOTHESIS_SEED)
@settings(max_examples=24, deadline=None, database=None)
@given(
    x_value=st.integers(min_value=-25, max_value=25),
    y_value=st.integers(min_value=-25, max_value=25),
)
def test_s17_hypothesis_linsolve_unique_integer_system(x_value, y_value):
    response = _post(
        "/api/v1/solve/system",
        {
            "equations": [
                f"x+y={x_value + y_value}",
                f"x-y={x_value - y_value}",
            ],
            "variables": ["x", "y"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True, body
    assert len(body["result_data"]) == 1, body
    text = body["result_data"][0]["text"].replace(" ", "")
    assert f"x={x_value}" in text
    assert f"y={y_value}" in text
