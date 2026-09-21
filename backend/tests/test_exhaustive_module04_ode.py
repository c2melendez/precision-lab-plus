"""Suite exhaustiva original — Módulo 4: EDO.

QA-only. No modifica código de producto.
"""
import sympy
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def ode(expr: str):
    return client.post("/api/v1/ode", json={"expression": expr})

def test_m4_first_order_general_and_ic():
    r = ode("y'=2x")
    b = r.json()
    assert r.status_code == 200 and b["success"] is True
    assert "x**2" in b["result_text"] and "C1" in b["result_text"]

    r = ode("y'=2x, y(0)=1")
    b = r.json()
    assert r.status_code == 200 and b["success"] is True
    assert "x**2 + 1" in b["result_text"]

def test_m4_second_order_homogeneous_and_nonhomogeneous():
    for expr in ["y''+3y'+2y=0", "y''+3y'+2y=4"]:
        r = ode(expr)
        b = r.json()
        assert r.status_code == 200 and b["success"] is True, b
        assert "Eq(y(x)," in b["result_text"]

def test_m4_plus_extended_first_order_depends_on_y():
    r = ode("y'=y")
    b = r.json()
    assert r.status_code == 200 and b["success"] is True
    assert "exp(x)" in b["result_text"]

def test_m4_second_order_one_ic_warns_remaining_constant():
    r = ode("y''+3y'+2y=0, y(0)=1")
    b = r.json()
    assert r.status_code == 200 and b["success"] is True
    assert b["warnings"], b

def test_m4_rejections_are_explicit():
    order3 = ode("y'''=0").json()
    assert order3["success"] is False
    assert order3["error_code"] == "UNSUPPORTED_OPERATION"

    no_derivative = ode("y=2x").json()
    assert no_derivative["success"] is False
    assert no_derivative["error_code"] == "PARSE_ERROR"

def test_m4_general_evaluate_does_not_invoke_dsolve():
    r = client.post("/api/v1/evaluate", json={"expression":"dsolve(x)","angle_unit":"rad"})
    b = r.json()
    assert r.status_code == 200
    assert b["success"] is False
    assert b["error_code"] == "PARSE_ERROR"
