"""Algebra229 AS-B-29 factor(123456789) over HTTP: exact row and independent prime oracle."""
import ast
import gzip
import re
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(123456789)"
ORIGINAL = 123456789
EXPECTED = "3^2*3607*3803"


def _factor_response() -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    return result


def _trial_division_factorization(value: int) -> list[tuple[int, int]]:
    """Factor an integer by trial division, independently of SymPy."""
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


def _is_prime_by_trial_division(value: int) -> bool:
    if type(value) is not int or value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def _parse_prime_powers(expression: str) -> list[tuple[int, int]]:
    return [
        (int(base), int(exponent or "1"))
        for base, exponent in re.findall(r"(\d+)(?:\^(\d+))?", expression)
    ]


def _independent_integer_eval(expression: str) -> int:
    """Evaluate a factor expression with a restricted AST, not SymPy."""
    root = ast.parse(expression.replace("^", "**"), mode="eval").body

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            return visit(node.left) * visit(node.right)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            base, exponent = visit(node.left), visit(node.right)
            if 0 <= exponent <= 32:
                return base**exponent
        raise AssertionError(f"Unsupported factor expression node: {ast.dump(node)}")

    result = visit(root)
    assert type(result) is int
    return result


def test_as_b29_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-29 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-B-29",
        "N2",
        "`factorizar`",
        r"`\text{factorizar el entero }123456789`",
        r"`3^{2}\cdot 3607\cdot 3803`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_b29_http_returns_exact_ascii_factorization():
    result = _factor_response()
    assert re.sub(r"\s+", "", result["result_text"]) == EXPECTED, result["result_text"]


def test_as_b29_independent_prime_oracle_checks_multiplicities_and_product():
    result = _factor_response()
    expression = re.sub(r"\s+", "", result["result_text"])
    expected = _trial_division_factorization(ORIGINAL)
    actual = _parse_prime_powers(expression)
    assert expected == [(3, 2), (3607, 1), (3803, 1)]
    assert actual == expected, (expression, actual, expected)
    assert all(_is_prime_by_trial_division(prime) for prime, _ in actual)
    assert _independent_integer_eval(expression) == ORIGINAL
    assert math_product(actual) == ORIGINAL


def math_product(factors: list[tuple[int, int]]) -> int:
    product = 1
    for prime, exponent in factors:
        product *= prime**exponent
    return product

