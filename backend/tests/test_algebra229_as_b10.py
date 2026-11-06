"""Algebra229 AS-B-10 original factor x^3+3x^2+3x+1 (perfect cube) over Q, through HTTP."""
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


def test_as_b10_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-10 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-10",
        "N2",
        "`factorizar`",
        "`x^{3}+3x^{2}+3x+1`",
        "`\\left(x + 1\\right)^{3}`",
        "",
        "",
    ]


def test_as_b10_factor_perfect_cube_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^3+3x^2+3x+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    assert result["result_latex"] == "\\left(x + 1\\right)^{3}"

    got = sp.sympify(result["result_text"])
    x = sp.symbols("x")
    assert got.is_Pow and got.exp == 3, result["result_text"]
    assert sp.expand(got.base - (x + 1)) == 0, result["result_text"]
    assert sp.expand(got - (x**3 + 3 * x**2 + 3 * x + 1)) == 0

    for x_value in (-11, -7, -3, -1, 0, 1, 2, 3, 4, 7):
        actual = _independent_integer_eval(result["result_text"], x_value)
        expected = x_value**3 + 3 * x_value**2 + 3 * x_value + 1
        assert actual == expected, (x_value, result["result_text"], actual, expected)
