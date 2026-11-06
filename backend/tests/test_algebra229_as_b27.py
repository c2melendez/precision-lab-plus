"""Algebra229 AS-B-27 factor(1001) over HTTP: exact row and independent prime oracle."""
import ast
import gzip
import re
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(1001)"
EXPECTED = "7*11*13"


def _factor_response() -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    return result


def _independent_prime_factorization(value: int) -> list[tuple[int, int]]:
    """Return prime/exponent pairs by trial division, independently of SymPy."""
    if type(value) is not int or value < 2:
        raise ValueError("Expected an integer >= 2")
    remaining = value
    factors = []
    divisor = 2
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            exponent = 0
            while remaining % divisor == 0:
                remaining //= divisor
                exponent += 1
            factors.append((divisor, exponent))
        divisor += 1
    if remaining > 1:
        factors.append((remaining, 1))
    return factors


def _parse_prime_powers(expression: str) -> list[tuple[int, int]]:
    return [
        (int(base), int(exponent or "1"))
        for base, exponent in re.findall(r"(\d+)(?:\^(\d+))?", expression)
    ]


def _independent_integer_eval(expression: str) -> int:
    """Evaluate the integer factor string with a small, restricted AST."""
    root = ast.parse(expression.replace("^", "**"), mode="eval").body

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Pow) and 0 <= right <= 16:
                return left**right
        raise AssertionError(f"Unsupported factor expression node: {ast.dump(node)}")

    result = visit(root)
    assert type(result) is int
    return result


def math_product(factors: list[tuple[int, int]]) -> int:
    product = 1
    for prime, exponent in factors:
        product *= prime**exponent
    return product


def test_as_b27_source_row_has_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-27 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-B-27",
        "N2",
        "`factorizar`",
        r"`\text{factorizar el entero }1001`",
        r"`7\cdot 11\cdot 13`",
        "",
    ], source_row
    assert cells[7:] == [""], source_row


def test_as_b27_factor_1001_http_returns_exact_ascii_form():
    result = _factor_response()
    assert result["result_text"].replace(" ", "") == EXPECTED, result["result_text"]


def test_as_b27_independent_prime_factorization_oracle_and_integer_evaluation():
    result = _factor_response()
    expression = result["result_text"].replace(" ", "")
    expected = _independent_prime_factorization(1001)
    actual = _parse_prime_powers(expression)
    assert expected == [(7, 1), (11, 1), (13, 1)]
    assert actual == expected, (expression, actual, expected)
    assert _independent_integer_eval(expression) == 1001
    assert math_product(actual) == 1001
