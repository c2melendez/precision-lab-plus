"""Algebra229 AS-B-19 factor common multivariable factor x^2y-xy^2 over HTTP."""
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
    "x",
    "y",
    "\\left(x - y\\right)",
]


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


def test_as_b19_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-19 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-19",
        "N2",
        "`factorizar`",
        "`x^{2}y-xy^{2}`",
        "`x y \\left(x - y\\right)`",
        "",
        "",
    ]


def test_as_b19_factor_common_multivariable_http_and_independent_pair_oracle():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^2*y-x*y^2"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    latex = result["result_latex"]
    acceptable_latex = {" ".join(p) for p in itertools.permutations(FACTOR_LATEX)}
    assert latex in acceptable_latex, latex

    x, y = sp.symbols("x y")
    got = sp.sympify(result["result_text"])
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 3, result["result_text"]
    expanded_factors = {sp.expand(f) for f in got.args}
    assert expanded_factors == {x, y, x - y}, result["result_text"]
    assert sp.expand(got - (x**2 * y - x * y**2)) == 0

    pairs = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 3), (-2, 5), (4, -1), (-3, -3), (7, 2), (5, -6)]
    for x_val, y_val in pairs:
        actual = _independent_integer_eval(result["result_text"], {"x": x_val, "y": y_val})
        expected = x_val**2 * y_val - x_val * y_val**2
        assert actual == expected, (x_val, y_val, result["result_text"], actual, expected)
