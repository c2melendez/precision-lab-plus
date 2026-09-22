"""Suite exhaustiva original — Módulo 3: Cálculo.

QA-only. No modifica código de producto.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

def test_m3_derivatives_known_and_boundary():
    r = post("derivative", {"expression":"x**3","variable":"x","order":1})
    assert r.status_code == 200
    assert r.json()["result_text"] == "3*x**2"

    r = post("derivative", {"expression":"x**5","variable":"x","order":4})
    assert r.status_code == 200
    assert r.json()["result_text"] == "120*x"

    # El contrato Pydantic limita order a 1..5; order=6 se rechaza en la
    # frontera HTTP antes de entrar al motor, por lo que el código correcto
    # es 422 (no MathResponse 200 con VALIDATION_ERROR).
    r = post("derivative", {"expression":"x**2","variable":"x","order":6})
    assert r.status_code == 422

def test_m3_integrals_known_and_boundary():
    r = post("integral", {"expression":"x**2","variable":"x"})
    body = r.json()
    assert r.status_code == 200 and body["success"] is True
    assert body["result_text"] == "x**3/3 + C"

    r = post("integral", {"expression":"x**2","variable":"x","lower_bound":"0","upper_bound":"2"})
    body = r.json()
    assert r.status_code == 200 and body["success"] is True
    assert body["result_text"] == "8/3"

    r = post("integral", {"expression":"x","variable":"x","lower_bound":"0"})
    body = r.json()
    assert body["success"] is False
    assert body["error_code"] == "VALIDATION_ERROR"

def test_m3_limits_known_infinity_and_lateral():
    cases = [
        ({"expression":"sin(x)/x","variable":"x","point":"0","direction":"both"}, "1"),
        ({"expression":"1/x","variable":"x","point":"oo","direction":"both"}, "0"),
        ({"expression":"1/x","variable":"x","point":"0","direction":"right"}, "oo"),
        ({"expression":"1/x","variable":"x","point":"0","direction":"left"}, "-oo"),
    ]
    for payload, expected in cases:
        r = post("limit", payload)
        body = r.json()
        assert r.status_code == 200 and body["success"] is True, body
        assert body["result_text"] == expected, body

def test_m3_two_sided_nonexistent_limit_is_dne():
    r = post("limit", {"expression":"1/x","variable":"x","point":"0","direction":"both"})
    body = r.json()
    assert r.status_code == 200
    assert body["success"] is True
    assert body["result_text"] == "DNE", body

def test_m3_calculus_constructs_rejected_from_general_evaluate():
    for expression in [
        "Derivative(x**2,x)",
        "Integral(x,x)",
        "Sum(i,(i,1,5))",
        "Product(i,(i,1,4))",
        "Limit(sin(x)/x,x,0)",
    ]:
        r = post("evaluate", {"expression":expression,"angle_unit":"rad"})
        body = r.json()
        assert r.status_code == 200
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"
