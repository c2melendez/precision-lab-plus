"""Matrices/Vectores MV-B-01..22: determinantes.

Bilateral coverage for the MV-B rows of matriz_matrices_vectores. The frozen
source is LaTeX; the product's matrix surface is the /matrix/* API. Documented
harness translations:

* Numeric cells keep their exact value (the API accepts ``\\frac`` and ``a/b``);
  decimal cells are also exact (SymPy rationalizes them).
* Symbolic cells are translated to the backend syntax the Plus frontend already
  sends (``latexToBackendSyntax``): ``a^{2}`` -> ``a^2``, ``\\cos\\theta`` ->
  ``cos(theta)``, ``-\\sin\\theta`` -> ``-sin(theta)``.
* MV-B-13 and MV-B-14 are composed with the product's own endpoints, like
  MV-A-24: ``det(2A)`` = determinant of ``(2I)xA``; ``det(AB)`` =
  determinant of the product.
* Symbolic results are accepted up to exact algebraic equivalence (G2
  convention); rows that the source asks to be factored are additionally
  checked with ``sympy.factor``.
"""
from __future__ import annotations

import gzip
import json
import re
from fractions import Fraction
from pathlib import Path

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_matrices_vectores.md.gz"
JSONL = ROOT / "qa/certification/matrices_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
MV_B = [row for row in ROWS if row["seccion"] == "B"]

MATRIX_RE = re.compile(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", re.S)
CELL_FRAC_RE = re.compile(r"^(-?)\\frac\{([+-]?\d+)\}\{([+-]?\d+)\}$")
SYMBOLIC_FUNCTION_RE = re.compile(r"\\(sin|cos|tan)\s*\\?([A-Za-z]+)")
SYMBOLIC_EXPONENT_RE = re.compile(r"\^\{([^{}]+)\}")


def frozen_row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def backend_cell(cell: str) -> str:
    """LaTeX cell -> the backend syntax the Plus frontend sends."""
    compact = re.sub(r"\s+", "", cell)
    frac = CELL_FRAC_RE.fullmatch(compact)
    if frac:
        return f"{frac.group(1)}{frac.group(2)}/{frac.group(3)}"
    compact = compact.replace("\\left", "").replace("\\right", "")
    compact = SYMBOLIC_FUNCTION_RE.sub(lambda m: f"{m.group(1)}({m.group(2)})", compact)
    compact = SYMBOLIC_EXPONENT_RE.sub(lambda m: f"^{m.group(1)}", compact)
    return compact


def matrices_of(expression: str) -> list[list[list[str]]]:
    out = []
    for body in MATRIX_RE.findall(expression):
        rows = [r.strip() for r in body.split("\\\\") if r.strip()]
        out.append([[backend_cell(cell) for cell in row.split("&")] for row in rows])
    return out


def fraction_value(text: str) -> Fraction:
    compact = re.sub(r"\s+", "", text)
    frac = CELL_FRAC_RE.fullmatch(compact)
    if frac:
        return Fraction(int(f"{frac.group(1)}{frac.group(2)}"), int(frac.group(3)))
    return Fraction(compact)


def _response(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _determinant(client: TestClient, matrix: list[list[str]]) -> dict:
    return _response(client, "/api/v1/matrix/determinant", {"matrix": matrix})


def _multiply(client: TestClient, a: list[list[str]], b: list[list[str]]) -> list[list[str]]:
    body = _response(
        client,
        "/api/v1/matrix/operations",
        {"operation": "multiply", "matrix_a": a, "matrix_b": b},
    )
    assert body["success"] is True, body
    return body["result_data"]


def _run(client: TestClient, row: dict) -> dict:
    cells = matrices_of(row["entrada"])
    if row["id"] == "MV-B-13":
        size = len(cells[0])
        diagonal = [[("2" if r == c else "0") for c in range(size)] for r in range(size)]
        return _determinant(client, _multiply(client, diagonal, cells[0]))
    if row["id"] == "MV-B-14":
        return _determinant(client, _multiply(client, cells[0], cells[1]))
    return _determinant(client, cells[0])


SYMBOLIC_EXPECTED = {
    "MV-B-16": sympy.sympify("a*d - b*c"),
    "MV-B-17": sympy.sympify("1 - x**2"),
    "MV-B-18": sympy.sympify("-(a - b)*(a - c)*(b - c)"),
    "MV-B-19": sympy.sympify("(a - 1)**2*(a + 2)"),
    "MV-B-20": sympy.Integer(1),
    "MV-B-21": sympy.Integer(0),
}
FACTORED_ROWS = {"MV-B-18", "MV-B-19"}


def test_mv_b_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    counts: dict[str, int] = {}
    for row in ROWS:
        counts[row["seccion"]] = counts.get(row["seccion"], 0) + 1
    assert counts == {
        "A": 25,
        "B": 22,
        "C": 19,
        "D": 17,
        "E": 12,
        "F": 17,
        "G": 22,
        "H": 12,
        "J": 7,
    }
    assert len(MV_B) == 22
    for row in MV_B:
        line = frozen_row(row["id"])
        assert row["entrada"] in line, row["id"]
        assert row["esperado"] in line, row["id"]


@pytest.mark.parametrize("row", MV_B, ids=[row["id"] for row in MV_B])
def test_mv_b_rows_evaluate_through_the_matrix_api(row):
    with TestClient(app) as client:
        body = _run(client, row)

        if row["operacion"] == "error":
            assert body["success"] is False, body
            assert body["error_code"] == "DIMENSION_MISMATCH", body
            assert body["error_message"], body
            return

        assert body["success"] is True, body

        if row["id"] in SYMBOLIC_EXPECTED:
            actual = sympy.sympify(body["result_text"])
            expected = SYMBOLIC_EXPECTED[row["id"]]
            assert sympy.simplify(actual - expected) == 0, (row["id"], actual, expected)
            if row["id"] in FACTORED_ROWS:
                assert actual.is_Mul, (row["id"], actual)
                assert len(actual.args) >= 2, (row["id"], actual)
            return

        assert Fraction(body["result_text"]) == fraction_value(row["esperado"]), (row["id"], body)


def test_mv_b_keeps_exact_numeric_and_simplifies_symbolic_rows():
    with TestClient(app) as client:
        hilbert4 = _run(client, next(row for row in MV_B if row["id"] == "MV-B-09"))
        assert Fraction(hilbert4["result_text"]) == Fraction(1, 6048000)
        hilbert5 = _run(client, next(row for row in MV_B if row["id"] == "MV-B-10"))
        assert Fraction(hilbert5["result_text"]) == Fraction(1, 266716800000)
        decimals = _run(client, next(row for row in MV_B if row["id"] == "MV-B-15"))
        assert Fraction(decimals["result_text"]) == Fraction(-1, 50)

        trig = _run(client, next(row for row in MV_B if row["id"] == "MV-B-20"))
        assert trig["result_text"] == "1"
        assert trig["result_latex"] == "1"
        complex_row = _run(client, next(row for row in MV_B if row["id"] == "MV-B-21"))
        assert complex_row["result_text"] == "0"

        symbolic = _run(client, next(row for row in MV_B if row["id"] == "MV-B-16"))
        assert symbolic["result_approx"] is None, symbolic


def test_mv_b_symbolic_support_is_scoped_to_determinant_and_inverse():
    with TestClient(app) as client:
        # El resto de operaciones conserva el contrato numérico estricto.
        add_body = _response(
            client,
            "/api/v1/matrix/operations",
            {
                "operation": "add",
                "matrix_a": [["a", "0"], ["0", "1"]],
                "matrix_b": [["1", "0"], ["0", "1"]],
            },
        )
        assert add_body["success"] is False, add_body
        assert add_body["error_code"] == "PARSE_ERROR", add_body

        # MV-C-10/11 ampl��a el contrato simb��lico a la inversa; MV-B solo
        # fijaba que las dem��s operaciones siguieran siendo num��ricas.
        inverse_body = _response(
            client, "/api/v1/matrix/inverse", {"matrix": [["a", "0"], ["0", "1"]]}
        )
        assert inverse_body["success"] is True, inverse_body

        # Determinante: variables y trigonométricas elementales sí; el resto
        # de funciones del parser general sigue bloqueado en la celda.
        allowed = _determinant(
            client,
            [["cos(theta)", "-sin(theta)"], ["sin(theta)", "cos(theta)"]],
        )
        assert allowed["success"] is True, allowed
        assert allowed["result_text"] == "1", allowed

        blocked = _determinant(client, [["exp(x)", "0"], ["0", "1"]])
        assert blocked["success"] is False, blocked
        assert blocked["error_code"] == "PARSE_ERROR", blocked


def test_mv_b_rejects_non_square_symbolic_determinant():
    with TestClient(app) as client:
        body = _determinant(client, [["a", "b", "c"], ["d", "e", "f"]])
        assert body["success"] is False, body
        assert body["error_code"] == "DIMENSION_MISMATCH", body
        assert "cuadrada" in body["error_message"].lower(), body
