"""Algebra229 AS-A-06 original expand (x+y+z)^2 over HTTP with independent oracle."""
import gzip
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a06_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-06 |"))
    expected_row = "| AS-A-06 | N2 | `expandir` | `(x+y+z)^{2}` | `x^{2} + 2 x y + 2 x z + y^{2} + 2 y z + z^{2}` |  |"
    assert source_row == expected_row


def test_as_a06_expand_trinomial_square_service_http_independent_oracle():
    original = "(x+y+z)**2"
    x, y, z = sp.symbols("x y z")
    symbolic_oracle = x**2 + 2*x*y + 2*x*z + y**2 + 2*y*z + z**2

    service = expand_expression(original)
    assert sp.simplify(service.result_expr - symbolic_oracle) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - symbolic_oracle) == 0

    # Python arithmetic is the independent numeric expected-value oracle.
    samples = [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 1),
        (2, -1, 3),
        (-2, 4, -1),
        (1, 2, 3),
    ]
    for xv, yv, zv in samples:
        substitution = {x: xv, y: yv, z: zv}
        expected = float((xv + yv + zv) ** 2)
        service_actual = float(service.result_expr.subs(substitution))
        http_actual = float(http_expr.subs(substitution))
        assert math.isclose(service_actual, expected, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(http_actual, expected, rel_tol=1e-12, abs_tol=1e-12)
