"""Algebra229 AS-B-15 original factor x^3-x^2-x+1 over Q, through HTTP."""
import ast
import gzip
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def _independent_integer_eval(expression: str, x_val: int) -> int:
    """Evaluate a small integer polynomial in x using Python AST only."""
    substituted = re.sub(r"\bx\b", f"({x_val})", expression)
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


def test_as_b15_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-15 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-15",
        "N2",
        "`factorizar`",
        "`x^{3}-x^{2}-x+1`",
        "`\\left(x - 1\\right)^{2} \\left(x + 1\\right)`",
        "",
        "",
    ]


def test_as_b15_factor_x3_x2_x_1_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^3-x^2-x+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    latex = result["result_latex"]
    acceptable_latex = {
        "\\left(x - 1\\right)^{2} \\left(x + 1\\right)",
        "\\left(x + 1\\right) \\left(x - 1\\right)^{2}",
    }
    assert latex in acceptable_latex, latex

    got = sp.sympify(result["result_text"])
    x = sp.symbols("x")
    assert sp.expand(got - (x**3 - x**2 - x + 1)) == 0
    # Accept (x-1)^2 * (x+1) structure
    factored = sp.factor(x**3 - x**2 - x + 1)
    assert sp.expand(got - factored) == 0
    assert (x - 1) in sp.Mul.make_args(sp.expand(got)) or any(
        isinstance(a, sp.Pow) and a.base == x - 1 for a in sp.Mul.make_args(got)
    ) or sp.factor(got) == factored

    samples = [-3, -2, -1, 0, 1, 2, 3, 4, 5, -4]
    for xv in samples:
        actual = _independent_integer_eval(result["result_text"], xv)
        expected = xv**3 - xv**2 - xv + 1
        assert actual == expected, (xv, result["result_text"], actual, expected)
