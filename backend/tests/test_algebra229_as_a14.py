"""Algebra229 AS-A-14 radical-square expansion with independent numeric oracle."""
import gzip
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a14_source_row_is_exact():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-14 |"))
    expected_row = r"| AS-A-14 | N2 | `expandir` | `\\left(\\sqrt{2}+\\sqrt{3}\\right)^{2}` | `2 \\sqrt{6} + 5` |  |"
    assert source_row == expected_row


def test_as_a14_expand_service_http_exact_and_independent_numeric_oracle():
    original = "(sqrt(2)+sqrt(3))^2"
    symbolic_oracle = 5 + 2 * sp.sqrt(6)

    service = expand_expression(original)
    assert sp.simplify(service.result_expr - symbolic_oracle) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - symbolic_oracle) == 0
    assert "**2" not in payload["result_text"].replace(" ", "")

    # Python math is independent from SymPy's symbolic simplifier.
    expected = 5 + 2 * math.sqrt(6)
    assert math.isclose(float(service.result_expr), expected, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(float(http_expr), expected, rel_tol=1e-12, abs_tol=1e-12)
