"""Algebra229 AS-B-21 factor (x^2+1)^2-4x^2 over HTTP, exact row and independent integer oracle."""
import ast
import gzip
import itertools
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"

FACTOR_LATEX = [
    "\\left(x - 1\\right)^{2}",
    "\\left(x + 1\\right)^{2}",
]


def _independent_integer_eval(expression: str, values: dict) -> int:
    """Evaluate a small integer polynomial expression using Python AST."""
    substituted = expression
    for name, val in values.items():
        substituted = re.sub(rf"\b{name}\b", f"({val})", substituted)
    root = ast.parse(substituted, mode="eval").body

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Pow) and 0 <= right <= 8:
                return left**right
        raise AssertionError(f"Unsupported result expression node: {ast.dump(node)}")

    value = visit(root)
    assert type(value) is int
    return value


def test_as_b21_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-21 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-21",
        "N3",
        "`factorizar`",
        "`\\left(x^{2}+1\\right)^{2}-4x^{2}`",
        "`\\left(x - 1\\right)^{2} \\left(x + 1\\right)^{2}`",
        "",
        "",
    ]


def test_as_b21_factor_difference_of_squares_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "(x^2+1)^2-4*x^2"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    latex = result["result_latex"]
    acceptable_latex = {" ".join(p) for p in itertools.permutations(FACTOR_LATEX)}
    assert latex in acceptable_latex, latex

    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert isinstance(got, sp.Mul), result["result_text"]
    assert sp.expand(got - ((x**2 + 1) ** 2 - 4 * x**2)) == 0
    _, factors = sp.factor_list(got)
    assert sorted((sp.degree(f, x), m) for f, m in factors) == [(1, 2), (1, 2)], result["result_text"]
    assert {sp.expand(f) for f, _ in factors} == {x - 1, x + 1}, result["result_text"]

    samples = [0, 1, -1, 2, -2, 3, -3, 4, 5, 10]
    for x_val in samples:
        actual = _independent_integer_eval(result["result_text"], {"x": x_val})
        expected = (x_val**2 + 1) ** 2 - 4 * x_val**2
        assert actual == expected, (x_val, result["result_text"], actual, expected)
