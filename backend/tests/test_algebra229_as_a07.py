"""Algebra229 AS-A-07 original expansion with an independent arithmetic oracle."""
import gzip
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a07_source_row_is_exact():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-07 |"))
    expected_row = "| AS-A-07 | N2 | `expandir` | `(2x-3)^{4}` | `16 x^{4} - 96 x^{3} + 216 x^{2} - 216 x + 81` |  |"
    assert source_row == expected_row


def test_as_a07_expand_service_http_independent_arithmetic_oracle():
    original = "(2*x-3)**4"
    x = sp.symbols("x")
    symbolic_oracle = 16*x**4 - 96*x**3 + 216*x**2 - 216*x + 81

    service = expand_expression(original)
    assert sp.simplify(service.result_expr - symbolic_oracle) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - symbolic_oracle) == 0

    # Native Python integer arithmetic is independent from SymPy.
    for value in (-2, -1, 0, 1, 2, 3, 5):
        expected = (2*value - 3)**4
        service_actual = float(service.result_expr.subs(x, value))
        http_actual = float(http_expr.subs(x, value))
        assert math.isclose(service_actual, expected, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(http_actual, expected, rel_tol=1e-12, abs_tol=1e-12)
