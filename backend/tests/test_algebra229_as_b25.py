"""Algebra229 AS-B-25: complex factorization only for explicit 'sobre ℂ' input."""
import ast
import gzip
import re
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(x^2+1) sobre ℂ"
EXPECTED = "(x-i)*(x+i)"
SAMPLES = [-10, -3, -1, 0, 1, 2, 5, 10]


def _independent_complex_eval(expression: str, x_value: int) -> complex:
    """Evaluate the rendered factorization with a restricted AST (never eval)."""
    substituted = re.sub(r"\bx\b", f"({x_value})", expression)
    root = ast.parse(substituted, mode="eval").body

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id == "i":
            return 1j
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
        raise AssertionError(f"Unsupported complex-result AST node: {ast.dump(node)}")

    return complex(visit(root))


def _factor_response(expression: str = INPUT) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": expression})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "factor", result
    assert result["request_id"], result
    return result


def test_as_b25_matches_all_seven_semantic_cells_of_frozen_source_row():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-25 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-B-25",
        "N3",
        "`factorizar`",
        "`x^{2}+1\\ \\text{sobre }\\mathbb{C}`",
        "`\\left(x - i\\right) \\left(x + i\\right)`",
        "Sobre ℂ se descompone.",
    ], source_row
    assert cells[7:] == [""], source_row


def test_as_b25_complex_factorization_http_exact_form_and_symbolic_equivalence():
    result = _factor_response()
    assert result["result_text"].replace(" ", "") == EXPECTED, result["result_text"]
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"], locals={"i": sp.I})
    assert sp.expand(got - (x**2 + 1)) == 0, result["result_text"]


def test_as_b25_independent_complex_ast_oracle_over_eight_integer_samples():
    result = _factor_response()
    expression = result["result_text"].replace(" ", "")
    for x_value in SAMPLES:
        actual = _independent_complex_eval(expression, x_value)
        expected = complex(x_value**2 + 1, 0)
        assert abs(actual - expected) < 1e-12, (x_value, expression, actual, expected)


def test_as_b25_plain_x2_plus_1_is_not_factored_over_complex_by_default():
    result = _factor_response("x^2+1")
    assert result["result_text"].replace(" ", "") != EXPECTED
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"], locals={"i": sp.I})
    assert sp.expand(got - (x**2 + 1)) == 0, result["result_text"]
