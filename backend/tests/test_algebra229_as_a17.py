"""Algebra229 AS-A-17 exact fifth-power expansion over service and HTTP."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
COEFFICIENTS = (32, -80, 80, -40, 10, -1)


def _independent_integer_oracle(x_value: int, y_value: int) -> int:
    return sum(coefficient * x_value ** (5 - index) * y_value ** index for index, coefficient in enumerate(COEFFICIENTS))


def test_as_a17_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-17 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:6] == [
        "AS-A-17",
        "N2",
        "`expandir`",
        "`(2x-y)^{5}`",
        "`32 x^{5} - 80 x^{4} y + 80 x^{3} y^{2} - 40 x^{2} y^{3} + 10 x y^{4} - y^{5}`",
    ]


def test_as_a17_expand_service_http_and_independent_integer_oracle():
    original = "(2*x-y)^5"
    x, y = sp.symbols("x y")
    oracle = 32 * x**5 - 80 * x**4 * y + 80 * x**3 * y**2 - 40 * x**2 * y**3 + 10 * x * y**4 - y**5

    service = expand_expression(original)
    assert sp.expand(service.result_expr - oracle) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": original})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - oracle) == 0
    # x**5 and y**5 are valid expanded monomials; reject only the original binomial power.
    assert got != (2 * x - y) ** 5
    assert sp.expand(got) == got

    # Independent integer coefficients and native Python integer arithmetic, not SymPy.
    samples = ((-2, 1), (1, -3), (1, 1), (3, 2), (0, 2), (-1, -2), (2, -1))
    for x_value, y_value in samples:
        expected = _independent_integer_oracle(x_value, y_value)
        assert service.result_expr.subs({x: x_value, y: y_value}) == expected
        assert got.subs({x: x_value, y: y_value}) == expected

