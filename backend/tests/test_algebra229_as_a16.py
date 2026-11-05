"""Algebra229 AS-A-16 exact expansion of (1+i)^4."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def _multiply_gaussian(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _gaussian_power(base: tuple[int, int], exponent: int) -> tuple[int, int]:
    result = (1, 0)
    for _ in range(exponent):
        result = _multiply_gaussian(result, base)
    return result


def test_as_a16_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-16 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:6] == ["AS-A-16", "N2", "`expandir`", "`(1+i)^{4}`", "`-4`"]


def test_as_a16_expand_service_http_and_independent_gaussian_integer_oracle():
    assert _gaussian_power((1, 1), 4) == (-4, 0)

    original = "(1+i)^4"
    service = expand_expression(original)
    assert sp.simplify(service.result_expr - (-4)) == 0
    assert sp.simplify(service.result_expr - (1 + sp.I) ** 4) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": original})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    got = sp.sympify(result["result_text"], locals={"i": sp.I, "I": sp.I})
    assert sp.simplify(got - (-4)) == 0
    assert "**4" not in result["result_text"].replace(" ", "")

