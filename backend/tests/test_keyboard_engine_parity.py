"""Paridad mínima entre inserciones del teclado virtual y el motor backend.

El teclado de Plus inserta sintaxis ASCII (`sin()`, `sqrt()`, `**2`, etc.).
Estos casos verifican que las funciones visibles más importantes siguen
siendo aceptadas por `/evaluate`, sin duplicar la cobertura matemática
detallada de `test_evaluate.py`.
"""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sin(pi/2)", 1.0),
        ("cos(0)", 1.0),
        ("tan(pi/4)", 1.0),
        ("asin(1)", 1.5707963267948966),
        ("ln(exp(1))", 1.0),
        ("ln(e)", 1.0),
        ("log(100)", 2.0),
        ("log(8,2)", 3.0),
        ("sqrt(9)", 3.0),
        ("abs(-7)", 7.0),
        ("5!", 120.0),
        ("mod(10,3)", 1.0),
        ("(2+3)**2", 25.0),
    ],
)
def test_virtual_keyboard_expression_reaches_evaluate_engine(expression, expected):
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-9)


@pytest.mark.parametrize("expression", ["eval(1)", "__import__('os')", "foo.bar"])
def test_keyboard_parity_does_not_weaken_parser_security(expression):
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    body = response.json()

    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
