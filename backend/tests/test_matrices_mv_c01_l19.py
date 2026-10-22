"""Matrices/Vectores MV-C-01..19: inversa, adjunta, cofactores y ecuaciones.

Bilateral coverage for the MV-C rows of matriz_matrices_vectores. The frozen
source is LaTeX; the product's matrix surface is the /matrix/* API.

Documented harness translations:

* Numeric cells keep their exact value (the API accepts ``\\frac`` and
  ``a/b``); decimal cells are exact (SymPy rationalizes them).
* Symbolic cells are translated to the backend syntax the Plus frontend
  sends: ``\\cos\\theta`` -> ``cos(theta)``.
* Symbolic results are accepted up to exact algebraic equivalence (G2).
  MV-C-08/10/11 are checked against explicit SymPy matrices; the rest are
  checked cell-by-cell as exact rationals.
* MV-C-18/19 use the dedicated ``/matrix/solve-equation`` endpoint with
  ``x_side="left"`` (X*A = B) and ``"right"`` (A*X = B), respectively.
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
MV_C = [row for row in ROWS if row["seccion"] == "C"]

MATRIX_RE = re.compile(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", re.S)
CELL_FRAC_RE = re.compile(r"^(-?)\\frac\{([+-]?\d+)\}\{([+-]?\d+)\}$")
SYMBOLIC_FUNCTION_RE = re.compile(r"\\(sin|cos|tan)\s*\\?([A-Za-z]+)")
SYMBOLIC_EXPONENT_RE = re.compile(r"\^\{([^{}]+)\}")

A, B, C, D, THETA = sympy.symbols("a b c d theta")


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


def _inverse(client: TestClient, matrix: list[list[str]]) -> dict:
    return _response(client, "/api/v1/matrix/inverse", {"matrix": matrix})


def _adjugate(client: TestClient, matrix: list[list[str]]) -> dict:
    return _response(client, "/api/v1/matrix/adjugate", {"matrix": matrix})


def _cofactor(client: TestClient, matrix: list[list[str]]) -> dict:
    return _response(client, "/api/v1/matrix/cofactor", {"matrix": matrix})


def _solve(client: TestClient, matrix_a: list[list[str]], matrix_b: list[list[str]], x_side: str) -> dict:
    return _response(
        client,
        "/api/v1/matrix/solve-equation",
        {"matrix_a": matrix_a, "matrix_b": matrix_b, "x_side": x_side},
    )


def _run(client: TestClient, row: dict) -> dict:
    cells = matrices_of(row["entrada"])
    if row["id"] == "MV-C-18":
        return _solve(client, cells[0], cells[1], "left")
    if row["id"] == "MV-C-19":
        return _solve(client, cells[0], cells[1], "right")
    if row["id"] in {"MV-C-14", "MV-C-15"}:
        return _adjugate(client, cells[0])
    if row["id"] == "MV-C-16":
        return _cofactor(client, cells[0])
    return _inverse(client, cells[0])


SYMBOLIC_EXPECTED = {
    "MV-C-08": sympy.Matrix([
        [sympy.Rational(1, 2), -sympy.I / 2],
        [-sympy.I / 2, sympy.Rational(1, 2)],
    ]),
    "MV-C-10": sympy.Matrix([
        [D / (A * D - B * C), -B / (A * D - B * C)],
        [-C / (A * D - B * C), A / (A * D - B * C)],
    ]),
    "MV-C-11": sympy.Matrix([
        [sympy.cos(THETA), sympy.sin(THETA)],
        [-sympy.sin(THETA), sympy.cos(THETA)],
    ]),
}


def test_mv_c_jsonl_is_complete_and_matches_the_frozen_source():
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
    assert len(MV_C) == 19
    for row in MV_C:
        line = frozen_row(row["id"])
        assert row["entrada"] in line, row["id"]
        assert row["esperado"] in line, row["id"]


@pytest.mark.parametrize("row", MV_C, ids=[row["id"] for row in MV_C])
def test_mv_c_rows_evaluate_through_the_matrix_api(row):
    with TestClient(app) as client:
        body = _run(client, row)

        if row["operacion"] == "error":
            assert body["success"] is False, body
            assert body["error_code"] == "SINGULAR_MATRIX", body
            assert body["error_message"], body
            return

        assert body["success"] is True, body
        assert body["result_type"] == "matrix", body

        if row["id"] in SYMBOLIC_EXPECTED:
            expected = SYMBOLIC_EXPECTED[row["id"]]
            actual = sympy.Matrix([[sympy.sympify(cell) for cell in result_row] for result_row in body["result_data"]])
            assert actual.shape == expected.shape, (row["id"], actual, expected)
            for r in range(expected.rows):
                for c in range(expected.cols):
                    assert sympy.simplify(actual[r, c] - expected[r, c]) == 0, (
                        row["id"],
                        r,
                        c,
                        actual[r, c],
                        expected[r, c],
                    )
            return

        expected_cells = matrices_of(row["esperado"])[0]
        actual_cells = body["result_data"]
        assert len(actual_cells) == len(expected_cells), (row["id"], actual_cells)
        for r, expected_row in enumerate(expected_cells):
            assert len(actual_cells[r]) == len(expected_row), (row["id"], actual_cells)
            for c, expected_cell in enumerate(expected_row):
                assert Fraction(actual_cells[r][c]) == fraction_value(expected_cell), (
                    row["id"],
                    r,
                    c,
                    actual_cells[r][c],
                    expected_cell,
                )


def test_mv_c_keeps_exact_numeric_and_complex_results():
    with TestClient(app) as client:
        hilbert4 = _run(client, next(row for row in MV_C if row["id"] == "MV-C-07"))
        assert Fraction(hilbert4["result_data"][2][2]) == 6480

        complex_row = _run(client, next(row for row in MV_C if row["id"] == "MV-C-08"))
        assert complex_row["result_data"] == [["1/2", "-I/2"], ["-I/2", "1/2"]], complex_row

        decimals = _run(client, next(row for row in MV_C if row["id"] == "MV-C-09"))
        assert [[Fraction(cell) for cell in row] for row in decimals["result_data"]] == [
            [Fraction(2), Fraction(-4)],
            [Fraction(-4), Fraction(10)],
        ]


def test_mv_c_solves_matrix_equations_with_the_correct_product_order():
    with TestClient(app) as client:
        row18 = next(row for row in MV_C if row["id"] == "MV-C-18")
        left = _run(client, row18)
        assert left["result_data"] == [["-1", "2"], ["-2", "3"]], left

        row19 = next(row for row in MV_C if row["id"] == "MV-C-19")
        right = _run(client, row19)
        assert right["result_data"] == [["-3", "-4"], ["4", "5"]], right


def test_mv_c_symbolic_support_is_scoped_to_inverse_and_determinant():
    with TestClient(app) as client:
        # La inversa simbólica es la ampliación acotada de MV-C.
        inverse_body = _inverse(client, [["a", "b"], ["c", "d"]])
        assert inverse_body["success"] is True, inverse_body

        oversized = [[f"a{i}{j}" for j in range(5)] for i in range(5)]
        oversized_body = _inverse(client, oversized)
        assert oversized_body["success"] is False, oversized_body
        assert oversized_body["error_code"] == "UNSUPPORTED_OPERATION", oversized_body

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

        adjugate_body = _adjugate(client, [["a", "0"], ["0", "1"]])
        assert adjugate_body["success"] is False, adjugate_body
        assert adjugate_body["error_code"] == "PARSE_ERROR", adjugate_body

        cofactor_body = _cofactor(client, [["a", "0"], ["0", "1"]])
        assert cofactor_body["success"] is False, cofactor_body
        assert cofactor_body["error_code"] == "PARSE_ERROR", cofactor_body

        # El determinante simbólico sigue funcionando (regresión MV-B).
        determinant = _response(
            client,
            "/api/v1/matrix/determinant",
            {"matrix": [["cos(theta)", "-sin(theta)"], ["sin(theta)", "cos(theta)"]]},
        )
        assert determinant["success"] is True, determinant
        assert determinant["result_text"] == "1", determinant


def test_mv_c_rejects_singular_inverse_and_equation():
    with TestClient(app) as client:
        inverse_body = _inverse(client, [["1", "2"], ["2", "4"]])
        assert inverse_body["success"] is False, inverse_body
        assert inverse_body["error_code"] == "SINGULAR_MATRIX", inverse_body

        equation_body = _solve(
            client,
            [["1", "2"], ["2", "4"]],
            [["5", "6"], ["7", "8"]],
            "left",
        )
        assert equation_body["success"] is False, equation_body
        assert equation_body["error_code"] == "SINGULAR_MATRIX", equation_body
