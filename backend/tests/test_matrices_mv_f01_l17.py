"""Matrices/Vectores MV-F-01..17: valores/vectores propios, polinomio característico,
Cayley–Hamilton, diagonalización y potencias."""
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
MV_F = [row for row in ROWS if row["seccion"] == "F"]
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


def to_sympy(cells: list[list[str]]) -> sympy.Matrix:
    return sympy.Matrix([[sympy.sympify(c) for c in row] for row in cells])


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(f"/api/v1{path}", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _eigen_pairs_match(matrix: sympy.Matrix) -> None:
    actual = matrix.eigenvects()
    assert actual, "empty spectrum"
    assert sum(m for _, m, _ in actual) == matrix.rows
    for val, mult, vecs in actual:
        assert len(vecs) >= 1
        assert all(v.norm() != 0 for v in vecs)
        for v in vecs:
            assert sympy.simplify((matrix - val * sympy.eye(matrix.rows)) * v) == sympy.Matrix.zeros(
                matrix.rows, 1
            )


def test_mv_f_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    assert len(MV_F) == 17
    for row in MV_F:
        line = frozen_row(row["id"])
        assert row["id"] in line
        assert row["entrada"] in line


@pytest.mark.parametrize("row", MV_F[:10], ids=lambda r: r["id"])
def test_mv_f_eigen_rows(row):
    matrix = to_sympy(matrices_of(row["entrada"])[0])
    _eigen_pairs_match(matrix)
    with TestClient(app) as client:
        body = _post(client, "/matrix/eigen", {"matrix": matrices_of(row["entrada"])[0]})
        assert body["success"] is True
        assert body["operation"] == "matrix_eigen"
        for val, _mult, _vecs in matrix.eigenvects():
            assert str(val) in body["result_text"] or sympy.latex(val) in body.get("result_latex", "")


def test_mv_f_11_characteristic_polynomial():
    row = next(r for r in MV_F if r["id"] == "MV-F-11")
    matrix = to_sympy(matrices_of(row["entrada"])[0])
    lam = sympy.symbols("lam")
    char = sympy.expand((lam * sympy.eye(2) - matrix).det())
    expected = sympy.sympify("lam**2 - 5*lam - 2")
    assert sympy.expand(char - expected) == 0
    assert sympy.expand(matrix.charpoly(lam).as_expr() - expected) == 0


def test_mv_f_12_cayley_hamilton():
    row = next(r for r in MV_F if r["id"] == "MV-F-12")
    cells = matrices_of(row["entrada"])[0]
    matrix = to_sympy(cells)
    residual = sympy.simplify(matrix**2 - 5 * matrix - 2 * sympy.eye(2))
    assert residual == sympy.zeros(2)
    with TestClient(app) as client:
        powered = _post(client, "/matrix/power", {"matrix": cells, "exponent": 2})
        assert powered["success"] is True
        a2 = sympy.Matrix([[sympy.sympify(c) for c in r] for r in powered["result_data"]])
        assert sympy.simplify(a2 - 5 * matrix - 2 * sympy.eye(2)) == sympy.zeros(2)


def test_mv_f_13_diagonalization():
    row = next(r for r in MV_F if r["id"] == "MV-F-13")
    matrix = to_sympy(matrices_of(row["entrada"])[0])
    P, D = matrix.diagonalize()
    assert D.is_diagonal()
    assert sorted(D.diagonal()) == [2, 5]
    assert sympy.simplify(P * D * P.inv() - matrix) == sympy.zeros(2)
    expected_mats = matrices_of(row["esperado"])
    P_oracle = to_sympy(expected_mats[0])
    D_oracle = to_sympy(expected_mats[1])
    assert sorted(D_oracle.diagonal()) == [2, 5]
    for col in range(P_oracle.cols):
        v = P_oracle.col(col)
        lam = D_oracle[col, col]
        assert sympy.simplify((matrix - lam * sympy.eye(2)) * v) == sympy.zeros(2, 1)


@pytest.mark.parametrize(
    "case_id,exponent",
    [("MV-F-14", 10), ("MV-F-15", 30), ("MV-F-16", 5), ("MV-F-17", 2)],
)
def test_mv_f_power_rows(case_id: str, exponent: int):
    row = next(r for r in MV_F if r["id"] == case_id)
    cells = matrices_of(row["entrada"])[0]
    expected = to_sympy(matrices_of(row["esperado"])[0])
    with TestClient(app) as client:
        body = _post(client, "/matrix/power", {"matrix": cells, "exponent": exponent})
        assert body["success"] is True
        got = sympy.Matrix([[sympy.sympify(c) for c in row_] for row_ in body["result_data"]])
        assert sympy.simplify(got - expected) == sympy.zeros(*expected.shape)
