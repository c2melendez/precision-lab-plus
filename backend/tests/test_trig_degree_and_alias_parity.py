"""AUD-SING-02: degree-mode reciprocal trigonometry and inverse-hyperbolic spellings.

Bilateral audit after the Lite fixes:
- With angle_unit="deg", sec/csc/cot must convert the angle exactly like
  sin/cos/tan (Plus already did; Lite used to interpret degrees as radians).
- "arcsinh/arccosh/arctanh" spellings: Plus rejects them with PARSE_ERROR
  (clear error, never a silent product); Lite resolves them to the real
  inverse hyperbolic function. Neither engine returns a wrong numeric value.
"""
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app


def _evaluate(client: TestClient, expression: str, angle_unit: str = "rad") -> dict:
    response = client.post(
        "/api/v1/evaluate", json={"expression": expression, "angle_unit": angle_unit}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_deg_cot_45_is_one():
    with TestClient(app) as client:
        payload = _evaluate(client, "cot(45)", "deg")
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"].replace("^", "**")) - 1) == 0


def test_deg_csc_30_is_two():
    with TestClient(app) as client:
        payload = _evaluate(client, "csc(30)", "deg")
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"].replace("^", "**")) - 2) == 0


def test_deg_sec_60_is_two():
    with TestClient(app) as client:
        payload = _evaluate(client, "sec(60)", "deg")
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"].replace("^", "**")) - 2) == 0


def test_deg_sec_90_is_domain_error():
    with TestClient(app) as client:
        payload = _evaluate(client, "sec(90)", "deg")
    assert payload["success"] is False, payload
    assert payload["error_code"] == "DOMAIN_ERROR", payload


def test_inverse_hyperbolic_alias_spellings_error_clearly_never_silently():
    for expression in ("arcsinh(1)", "arccosh(2)", "arctanh(0.5)"):
        with TestClient(app) as client:
            payload = _evaluate(client, expression)
        assert payload["success"] is False, (expression, payload)
        assert payload["error_code"] in {"PARSE_ERROR", "UNSUPPORTED_OPERATION"}, payload
        assert payload.get("result_text") in (None, ""), payload
