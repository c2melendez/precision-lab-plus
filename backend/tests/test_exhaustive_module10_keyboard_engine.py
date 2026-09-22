"""Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus backend).

QA-only. Expresa el contrato de las teclas activas; no modifica producto.
"""
import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def evaluate(expression):
    return client.post("/api/v1/evaluate", json={"expression": expression}).json()

@pytest.mark.parametrize(
    ("expression","expected"),
    [
        ("sin(pi/6)", 0.5), ("cos(pi/3)", 0.5), ("tan(pi/4)", 1.0),
        ("csc(pi/2)", 1.0), ("sec(0)", 1.0), ("cot(pi/4)", 1.0),
        ("asin(0.5)", math.pi/6), ("acos(0.5)", math.pi/3), ("atan(1)", math.pi/4),
        ("acsc(2)", math.pi/6), ("asec(2)", math.pi/3), ("acot(1)", math.pi/4),
        ("sinh(0)", 0.0), ("cosh(0)", 1.0), ("tanh(0)", 0.0),
        ("csch(1)", 1/math.sinh(1)), ("sech(0)", 1.0), ("coth(1)", 1/math.tanh(1)),
        ("asinh(1)", math.asinh(1)), ("acosh(2)", math.acosh(2)), ("atanh(0.5)", math.atanh(0.5)),
        ("acsch(2)", math.asinh(0.5)), ("asech(0.5)", math.acosh(2)), ("acoth(2)", math.atanh(0.5)),
    ],
)
def test_m10_all_trigonometric_keyboard_families(expression, expected):
    b = evaluate(expression)
    assert b["success"] is True, (expression,b)
    assert b["result_approx"] == pytest.approx(expected, rel=1e-8, abs=1e-8), (expression,b)

@pytest.mark.parametrize(
    ("expression","expected"),
    [
        ("ln(e)",1.0), ("log(100)",2.0), ("log(8,2)",3.0),
        ("exp(1)",math.e), ("sqrt(9)",3.0), ("sign(-4)",-1.0),
        ("mod(10,3)",1.0), ("lcm(6,8)",24.0), ("gcd(6,8)",2.0),
        ("5!",120.0),
    ],
)
def test_m10_algebra_keyboard_families(expression, expected):
    b=evaluate(expression)
    assert b["success"] is True, (expression,b)
    assert b["result_approx"] == pytest.approx(expected, rel=1e-8, abs=1e-8), (expression,b)

def test_m10_percent_key_means_percentage_not_modulo():
    b=evaluate("50%")
    assert b["success"] is True, b
    assert b["result_approx"] == pytest.approx(0.5, abs=1e-12), b

def test_m10_plus_minus_key_has_real_engine_semantics():
    b=evaluate("pm(5)")
    assert b["success"] is True, b
    text=(b.get("result_text") or "").replace(" ","")
    assert "5" in text and "-5" in text, b

def test_m10_complex_function_family_safe_values():
    for expression, expected in [
        ("re(2+3*i)",2.0), ("im(2+3*i)",3.0), ("arg(1+i)",math.pi/4),
        ("abs(3+4*i)",5.0),
    ]:
        b=evaluate(expression)
        assert b["success"] is True, (expression,b)
        assert b["result_approx"] == pytest.approx(expected, rel=1e-8, abs=1e-8), (expression,b)
