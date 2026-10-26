"""Contrato mínimo EDCX-B6 para semántica de logaritmos y respuestas complejas.

Estos tests cubren solo el comportamiento HTTP observable; no certifican por sí
solos las 53 filas B6 ni la semántica multivaluada de logaritmo.
"""
import math

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _evaluate(expression: str):
    return client.post("/api/v1/evaluate", json={"expression": expression})


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("log(100)", 2.0),  # logaritmo base 10 según el parser del producto
        ("ln(e)", 1.0),     # logaritmo natural
        ("Log(100)", math.log(100.0)),  # Log: logaritmo complejo principal
    ],
)
def test_b6_log_notation_has_distinct_documented_semantics(expression, expected):
    response = _evaluate(expression)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_b6_complex_log_result_uses_text_latex_not_real_approx_field():
    response = _evaluate("Log(-1)")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] is None
    assert body["result_text"]
    assert body["result_latex"]


def test_b6_principal_log_zero_is_reported_as_domain_error():
    response = _evaluate("Log(0)")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"
