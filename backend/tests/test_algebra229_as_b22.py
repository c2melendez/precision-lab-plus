"""Algebra229 AS-B-22 factor x^2+1 over HTTP: exact row, unchanged result, independent integer oracle."""
import ast
import gzip
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
SAMPLES = [0, 1, -1, 2, -2, 3, -3, 4, 5, 10]


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


def _factor_response() -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^2+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    return result


def test_as_b22_source_row_has_exact_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-22 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert cells[1:8] == [
        "AS-B-22",
        "N1",
        "`factorizar`",
        "`x^{2}+1`",
        "`x^{2} + 1`",
        "Irreducible sobre ℚ y ℝ: debe quedar igual.",
        "",
    ]


def test_as_b22_factor_x2_plus_1_http_result_is_unchanged():
    result = _factor_response()
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**2 + 1)) == 0, result["result_text"]
    assert isinstance(got, sp.Add), result["result_text"]
    latex = result["result_latex"]
    assert "x" in latex, latex
    assert "\\left(" not in latex and "\\cdot" not in latex and "\\times" not in latex, latex


def test_as_b22_irreducible_discriminant_oracle_and_independent_integer_samples():
    result = _factor_response()
    x = sp.symbols("x")
    coeffs = sp.Poly(sp.sympify(result["result_text"]), x).all_coeffs()
    assert coeffs == [1, 0, 1], result["result_text"]
    a, b, c = coeffs
    assert b * b - 4 * a * c == -4, "discriminant must be negative: no real roots"
    for x_val in SAMPLES:
        actual = _independent_integer_eval(result["result_text"], {"x": x_val})
        expected = x_val**2 + 1
        assert actual == expected, (x_val, result["result_text"], actual, expected)
        assert actual >= 1, (x_val, actual)
