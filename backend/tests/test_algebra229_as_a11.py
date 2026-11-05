"""Algebra229 AS-A-11 original expansion with independent arithmetic oracle."""
import gzip
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a11_source_row_is_exact():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-11 |"))
    expected_row = (
        r"| AS-A-11 | N2 | `expandir` | `(a+b+c)^{3}` | "
        r"`a^{3} + 3 a^{2} b + 3 a^{2} c + 3 a b^{2} + 6 a b c + 3 a c^{2} + b^{3} + 3 b^{2} c + 3 b c^{2} + c^{3}` |  |"
    )
    assert source_row == expected_row


def test_as_a11_expand_service_http_independent_arithmetic_oracle():
    original = "(a+b+c)^3"
    a, b, c = sp.symbols("a b c")
    symbolic_oracle = (
        a**3 + 3*a**2*b + 3*a**2*c + 3*a*b**2 + 6*a*b*c
        + 3*a*c**2 + b**3 + 3*b**2*c + 3*b*c**2 + c**3
    )

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
    for values in (
        (1, 2, 3),
        (0, -1, 2),
        (-2, 1, -1),
        (2, 2, 2),
        (-1, -1, -1),
        (3, 0, -2),
        (-3, 2, 1),
        (4, -2, 0),
    ):
        expected = (values[0] + values[1] + values[2])**3
        substitution = dict(zip((a, b, c), values))
        service_actual = float(service.result_expr.subs(substitution))
        http_actual = float(http_expr.subs(substitution))
        assert math.isclose(service_actual, expected, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(http_actual, expected, rel_tol=1e-12, abs_tol=1e-12)
