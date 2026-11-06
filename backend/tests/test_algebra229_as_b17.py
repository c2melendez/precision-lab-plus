"""Algebra229 AS-B-17 original factor a^3+b^3 over Q, through HTTP."""
import ast
import gzip
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def _independent_integer_eval(expression: str, values: dict) -> int:
    """Evaluate a small multi-variable integer polynomial using Python AST."""
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


def test_as_b17_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-17 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-17",
        "N2",
        "`factorizar`",
        "`a^{3}+b^{3}`",
        "`\\left(a + b\\right) \\left(a^{2} - a b + b^{2}\\right)`",
        "",
        "",
    ]


def test_as_b17_factor_a3_plus_b3_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "a^3+b^3"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    latex = result["result_latex"]
    acceptable_latex = {
        "\\left(a + b\\right) \\left(a^{2} - a b + b^{2}\\right)",
        "\\left(a^{2} - a b + b^{2}\\right) \\left(a + b\\right)",
    }
    assert latex in acceptable_latex, latex

    got = sp.sympify(result["result_text"])
    a, b = sp.symbols("a b")
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
    expanded_factors = {sp.expand(f) for f in got.args}
    assert expanded_factors == {a + b, a**2 - a * b + b**2}, result["result_text"]
    assert sp.expand(got - (a**3 + b**3)) == 0

    samples = [
        {"a": 0, "b": 0},
        {"a": 1, "b": 0},
        {"a": 0, "b": 1},
        {"a": 2, "b": 1},
        {"a": 3, "b": 2},
        {"a": -1, "b": 1},
        {"a": 4, "b": -2},
        {"a": -3, "b": -1},
        {"a": 5, "b": 3},
        {"a": 2, "b": 2},
    ]
    for vals in samples:
        actual = _independent_integer_eval(result["result_text"], vals)
        expected = vals["a"] ** 3 + vals["b"] ** 3
        assert actual == expected, (vals, result["result_text"], actual, expected)
