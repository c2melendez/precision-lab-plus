"""Algebra229 AS-B-09 original factor 6x^2+5x-4 over Q, through HTTP."""
import ast
import gzip
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def _independent_integer_eval(expression: str, x_value: int) -> int:
    """Evaluate a small integer polynomial using Python AST and native integer arithmetic."""
    substituted = re.sub(r"\bx\b", f"({x_value})", expression)
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


def test_as_b09_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-09 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-09",
        "N2",
        "`factorizar`",
        "`6x^{2}+5x-4`",
        "`\\left(2 x - 1\\right) \\left(3 x + 4\\right)`",
        "",
        "",
    ]


def test_as_b09_factor_quadratic_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "6x^2+5x-4"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    assert result["result_latex"] == "\\left(2 x - 1\\right) \\left(3 x + 4\\right)"

    got = sp.sympify(result["result_text"])
    x = sp.symbols("x")
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
    assert sorted(sp.Poly(factor, x).degree() for factor in got.args) == [1, 1], result["result_text"]
    expanded = {sp.expand(factor) for factor in got.args}
    assert expanded == {2 * x - 1, 3 * x + 4}, result["result_text"]

    for x_value in (-11, -7, -3, -1, 0, 1, 2, 3, 4, 7):
        actual = _independent_integer_eval(result["result_text"], x_value)
        expected = 6 * x_value**2 + 5 * x_value - 4
        assert actual == expected, (x_value, result["result_text"], actual, expected)
