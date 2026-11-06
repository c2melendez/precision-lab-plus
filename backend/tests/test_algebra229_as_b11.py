"""Algebra229 AS-B-11 original factor ax+ay+bx+by (grouping) over Q, through HTTP."""
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


def test_as_b11_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-11 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-11",
        "N2",
        "`factorizar`",
        "`ax+ay+bx+by`",
        "`\\left(a + b\\right) \\left(x + y\\right)`",
        "Agrupación de términos.",
        "",
    ]


def test_as_b11_factor_grouping_http_and_independent_integer_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "a*x+a*y+b*x+b*y"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    assert result["result_latex"] == "\\left(a + b\\right) \\left(x + y\\right)"

    got = sp.sympify(result["result_text"])
    a, b, x, y = sp.symbols("a b x y")
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
    expanded_factors = {sp.expand(f) for f in got.args}
    assert expanded_factors == {a + b, x + y}, result["result_text"]
    assert sp.expand(got - (a * x + a * y + b * x + b * y)) == 0

    samples = [
        {"a": 1, "b": 2, "x": 3, "y": 4},
        {"a": 0, "b": 0, "x": 0, "y": 0},
        {"a": -1, "b": 2, "x": -3, "y": 4},
        {"a": 5, "b": -2, "x": 0, "y": 1},
        {"a": 2, "b": 2, "x": 2, "y": 2},
        {"a": -4, "b": -1, "x": 3, "y": 0},
        {"a": 7, "b": 0, "x": -2, "y": 5},
        {"a": 1, "b": -1, "x": 1, "y": -1},
        {"a": 0, "b": 3, "x": 4, "y": -5},
        {"a": 6, "b": 1, "x": -1, "y": 2},
    ]
    for vals in samples:
        actual = _independent_integer_eval(result["result_text"], vals)
        expected = vals["a"] * vals["x"] + vals["a"] * vals["y"] + vals["b"] * vals["x"] + vals["b"] * vals["y"]
        assert actual == expected, (vals, result["result_text"], actual, expected)
