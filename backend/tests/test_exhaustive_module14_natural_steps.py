"""Suite exhaustiva original — Módulo 14: texto natural de procedimientos.

QA-only. No modifica código de producto.
Recorre las familias que hoy generan steps detallados en Plus y verifica
que title/description sean texto de usuario, no identificadores técnicos.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

TECHNICAL_RULES = {
    "PowerRule",
    "ChainRule",
    "ProductRule",
    "QuotientRule",
    "MatrixMultiply",
    "RowElimination",
    "NormalizePivot",
    "IdentifyCoefficients",
    "Discriminant",
    "QuadraticFormula",
    "Normalize",
}


@pytest.mark.parametrize(
    "label,path,payload",
    [
        ("derivada", "/api/v1/derivative", {"expression": "x**3", "variable": "x", "order": 1}),
        ("integral", "/api/v1/integral", {"expression": "x**2", "variable": "x"}),
        ("ecuación", "/api/v1/solve", {"equation": "x**2-5*x+6=0", "variable": "x", "angle_unit": "rad"}),
        (
            "matriz",
            "/api/v1/matrix/operations",
            {
                "matrix_a": [["1", "2"], ["3", "4"]],
                "matrix_b": [["5", "6"], ["7", "8"]],
                "operation": "multiply",
            },
        ),
        ("factorización", "/api/v1/factor", {"expression": "x**2-5*x+6"}),
    ],
)
def test_m14_step_families_expose_natural_titles_and_descriptions(label, path, payload):
    r = client.post(path, json=payload)
    b = r.json()
    assert r.status_code == 200, (label, b)
    assert b["success"] is True, (label, b)
    steps = b.get("steps") or []
    assert steps, f"{label}: se esperaba al menos un paso"

    for step in steps:
        title = (step.get("title") or "").strip()
        description = (step.get("description") or "").strip()
        rule = (step.get("rule") or "").strip()
        assert title, (label, step)
        assert description, (label, step)
        assert title not in TECHNICAL_RULES, (label, step)
        assert description not in TECHNICAL_RULES, (label, step)
        for technical in TECHNICAL_RULES:
            assert technical not in title, (label, step)
            assert technical not in description, (label, step)
        # El backend puede conservar rule internamente; M14 exige que no sea
        # el texto de usuario. La ocultación visual se comprueba en frontend.
        if rule:
            assert title != rule or rule not in TECHNICAL_RULES, (label, step)
