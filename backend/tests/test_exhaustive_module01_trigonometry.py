"""Suite exhaustiva original — Módulo 1: Trigonometría.

Archivo de QA: no modifica código de producto. Ejecuta valores conocidos,
modo grados y polos/dominios por la API pública.
"""

import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

KNOWN = [
    ("sin(0)", 0.0),
    ("sin(pi/2)", 1.0),
    ("cos(0)", 1.0),
    ("cos(pi)", -1.0),
    ("tan(pi/4)", 1.0),
    ("sec(0)", 1.0),
    ("csc(pi/2)", 1.0),
    ("cot(pi/4)", 1.0),
    ("asin(1)", math.pi / 2),
    ("acos(1)", 0.0),
    ("atan(1)", math.pi / 4),
    ("sinh(0)", 0.0),
    ("cosh(0)", 1.0),
    ("tanh(0)", 0.0),
    ("asinh(0)", 0.0),
    ("acosh(1)", 0.0),
    ("atanh(0)", 0.0),
    ("asech(1)", 0.0),
    ("acsch(1)", math.asinh(1)),
    ("acoth(2)", 0.5 * math.log(3)),
]

@pytest.mark.parametrize("expression,expected", KNOWN)
def test_module01_known_values(expression, expected):
    response = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, abs=1e-10)

@pytest.mark.parametrize("expression,expected", [
    ("sin(30)", 0.5),
    ("cos(60)", 0.5),
    ("tan(45)", 1.0),
])
def test_module01_degrees(expression, expected):
    response = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "deg"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, abs=1e-10)

@pytest.mark.parametrize("expression", [
    "tan(pi/2)",
    "sec(pi/2)",
    "csc(0)",
    "cot(0)",
    "atanh(1)",
    "asech(0)",
    "acoth(1)",
])
def test_module01_domain_edges_are_controlled(expression):
    response = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR", body
