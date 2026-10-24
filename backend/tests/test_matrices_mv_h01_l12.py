"""Matrices/Vectores MV-H-01..12: productos mixtos, 1×1, hermítica, rank/det
de estructuras, Hilbert, límites de tamaño y errores de parseo."""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_matrices_vectores.md.gz"
JSONL = ROOT / "qa/certification/matrices_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
MV_H = [row for row in ROWS if row["seccion"] == "H"]
MATRIX_RE = re.compile(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", re.S)


def frozen_row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def matrices_of(latex: str) -> list[list[list[str]]]:
    out: list[list[list[str]]] = []
    for match in MATRIX_RE.finditer(latex):
        rows = []
        for row in match.group(1).strip().split("\\\\"):
            rows.append([c.strip() for c in row.split("&")])
        out.append(rows)
    return out


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(f"/api/v1{path}", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _post_raw(client: TestClient, path: str, payload: dict):
    return client.post(f"/api/v1{path}", json=payload)


def test_mv_h_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    assert len(MV_H) == 12
    for row in MV_H:
        assert row["id"] in frozen_row(row["id"])


def test_mv_h_01_row_times_column():
    row = next(r for r in MV_H if r["id"] == "MV-H-01")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "multiply", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        assert sympy.Matrix(body["result_data"]) == sympy.Matrix([[32]])


def test_mv_h_02_column_times_row_outer():
    row = next(r for r in MV_H if r["id"] == "MV-H-02")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "multiply", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        expected = sympy.Matrix([[4, 5, 6], [8, 10, 12], [12, 15, 18]])
        assert sympy.Matrix(body["result_data"]) == expected


def test_mv_h_03_one_by_one_inverse():
    with TestClient(app) as client:
        body = _post(client, "/matrix/inverse", {"matrix": [["7"]]})
        assert body["success"] is True
        got = sympy.Matrix(body["result_data"])
        assert got == sympy.Matrix([[sympy.Rational(1, 7)]])


def test_mv_h_04_zero_matrix_not_invertible():
    with TestClient(app) as client:
        body = _post(client, "/matrix/inverse", {"matrix": [["0", "0"], ["0", "0"]]})
        assert body["success"] is False
        assert body["error_code"] == "SINGULAR_MATRIX"


def test_mv_h_05_projector_squared():
    cells = [["1/2", "1/2"], ["1/2", "1/2"]]
    with TestClient(app) as client:
        body = _post(client, "/matrix/power", {"matrix": cells, "exponent": 2})
        assert body["success"] is True
        got = sympy.Matrix([[sympy.sympify(c) for c in r] for r in body["result_data"]])
        expected = sympy.Matrix([[sympy.Rational(1, 2)] * 2] * 2)
        assert got == expected


def test_mv_h_06_hermitian_transpose():
    M = sympy.Matrix([[1, sympy.I], [2, -3 * sympy.I]])
    expected = sympy.Matrix([[1, 2], [-sympy.I, 3 * sympy.I]])
    assert M.H == expected


def test_mv_h_07_rank_aij_i_plus_j_10x10():
    A = sympy.Matrix(10, 10, lambda i, j: i + j + 2)
    assert A.rank() == 2


def test_mv_h_08_tridiagonal_det_10x10():
    T = sympy.zeros(10)
    for i in range(10):
        T[i, i] = 2
        if i:
            T[i, i - 1] = -1
        if i < 9:
            T[i, i + 1] = -1
    assert T.det() == 11


def test_mv_h_09_symbolic_4x4_det_has_24_terms():
    symbols = sympy.symbols("a b c d e f g h i j k l m n o p")
    M = sympy.Matrix(4, 4, symbols)
    expanded = sympy.expand(M.det())
    terms = expanded.as_ordered_terms() if expanded.func is sympy.Add else [expanded]
    assert len(terms) == 24


def test_mv_h_10_hilbert_inverse_exact_integers():
    H = sympy.Matrix(8, 8, lambda i, j: sympy.Rational(1, i + j + 1))
    inv = H.inv()
    assert all(x.is_integer for x in inv)
    H4 = sympy.Matrix(4, 4, lambda i, j: sympy.Rational(1, i + j + 1))
    cells = [[str(H4[i, j]) for j in range(4)] for i in range(4)]
    with TestClient(app) as client:
        body = _post(client, "/matrix/inverse", {"matrix": cells})
        assert body["success"] is True
        got = sympy.Matrix([[sympy.sympify(c) for c in r] for r in body["result_data"]])
        assert got == H4.inv()
        assert all(x.is_integer for x in got)


def test_mv_h_11_oversized_rejected_without_hang():
    huge = [["1"] * 7 for _ in range(7)]
    with TestClient(app) as client:
        response = _post_raw(client, "/matrix/determinant", {"matrix": huge})
        assert response.status_code == 422


def test_mv_h_12_invalid_cell_rejected():
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {
                "operation": "multiply",
                "matrix_a": [["1", "2"], ["3", "x"]],
                "matrix_b": [["abc", "1"], ["0", "1"]],
            },
        )
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"
