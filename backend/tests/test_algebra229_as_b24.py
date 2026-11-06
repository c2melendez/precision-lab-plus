"""Algebra229 AS-B-24: factor x^2-2 over R with sqrt(2), exact row and independent oracle."""
import ast
import gzip
import math
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(x^2-2) sobre ℝ"
EXPECTED = "(x-sqrt(2))*(x+sqrt(2))"
SAMPLES = [0, 1, -1, 2, -2, 3, -3, 4, 5, 10]


def _independent_real_eval(expression: str, values: dict) -> float:
    """Evaluate the returned real factorization using a restricted Python AST."""
    substituted = expression
    for name, val in values.items():
        substituted = re.sub(rf"\b{name}\b", f"({val})", substituted)
    root = ast.parse(substituted, mode="eval").body

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
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
            if isinstance(node.op, ast.Pow):
                return left**right
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "sqrt"
            and len(node.args) == 1
            and not node.keywords
        ):
            return math.sqrt(visit(node.args[0]))
        raise AssertionError(f"Unsupported result expression node: {ast.dump(node)}")

    return float(visit(root))


def _factor_response() -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    return result


def test_as_b24_source_row_has_seven_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-24 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:6] == [
        "AS-B-24",
        "N3",
        "`factorizar`",
        "`x^{2}-2\\ \\text{sobre }\\mathbb{R}`",
        "`\\left(x - \\sqrt{2}\\right) \\left(x + \\sqrt{2}\\right)`",
    ], source_row
    assert "Con raíces permitidas" in cells[6], source_row
    assert cells[7:] == [""], source_row


def test_as_b24_factor_x2_minus_2_over_reals_http_exact_output():
    result = _factor_response()
    assert result["result_text"].replace(" ", "") == EXPECTED, result["result_text"]
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**2 - 2)) == 0, result["result_text"]
    assert sp.Poly(got, x).as_expr().expand() == x**2 - 2
    assert "sqrt" in result["result_latex"].lower(), result["result_latex"]


def test_as_b24_independent_real_oracle_over_ten_integer_samples():
    result = _factor_response()
    result_text = result["result_text"].replace(" ", "")
    for x_val in SAMPLES:
        actual = _independent_real_eval(result_text, {"x": x_val})
        expected = x_val**2 - 2
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (
            x_val,
            result_text,
            actual,
            expected,
        )
    assert 2**2 < 8 < 3**2, "sqrt(2) is real and irrational"


