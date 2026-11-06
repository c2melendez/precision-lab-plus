"""Algebra229 AS-B-06 original factor x^4+4 (Sophie Germain), through HTTP."""
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


def test_as_b06_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-06 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-06",
        "N3",
        "`factorizar`",
        "`x^{4}+4`",
        "`\\left(x^{2} - 2 x + 2\\right) \\left(x^{2} + 2 x + 2\\right)`",
        "Identidad de Sophie Germain.",
        "",
    ]


def test_as_b06_factor_sophie_germain_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^4+4"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    assert result["result_latex"] == "\\left(x^{2} - 2 x + 2\\right) \\left(x^{2} + 2 x + 2\\right)"

    got = sp.sympify(result["result_text"])
    x = sp.symbols("x")
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
    assert sorted(sp.Poly(factor, x).degree() for factor in got.args) == [2, 2], result["result_text"]
    expanded = {sp.expand(factor) for factor in got.args}
    assert expanded == {x**2 - 2 * x + 2, x**2 + 2 * x + 2}, result["result_text"]
    for factor in got.args:
        assert sp.discriminant(factor, x) < 0, (result["result_text"], factor)

    for x_value in (-11, -7, -3, -1, 0, 1, 2, 3, 4, 7):
        actual = _independent_integer_eval(result["result_text"], x_value)
        expected = x_value**4 + 4
        assert actual == expected, (x_value, result["result_text"], actual, expected)
