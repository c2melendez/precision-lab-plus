"""Algebra229 AS-A-13 original expansion with independent arithmetic oracle."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a13_source_row_is_exact():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-13 |"))
    expected_row = r"| AS-A-13 | N2 | `expandir` | `(x+h)^{3}-x^{3}` | `h^{3} + 3 h^{2} x + 3 h x^{2}` |  |"
    assert source_row == expected_row


def test_as_a13_expand_service_http_independent_arithmetic_oracle():
    original = "(x+h)^3-x^3"
    x, h = sp.symbols("x h")
    symbolic_oracle = h**3 + 3 * h**2 * x + 3 * h * x**2

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
    samples = ((1, 2), (0, -1), (-2, 3), (2, 0), (-3, -2), (4, -1), (-1, 4), (3, 1))
    for x_value, h_value in samples:
        expected = h_value**3 + 3 * h_value**2 * x_value + 3 * h_value * x_value**2
        assert service.result_expr.subs({x: x_value, h: h_value}) == expected
        assert http_expr.subs({x: x_value, h: h_value}) == expected
