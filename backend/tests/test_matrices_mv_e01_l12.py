"""Matrices/Vectores MV-E-01..12: rango, núcleo y espacio columna."""
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
MV_E = [row for row in ROWS if row["seccion"] == "E"]
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


def _span_equals(actual_rows: list[list[str]], expected_columns: list[list[list[str]]]) -> bool:
    if not actual_rows and not expected_columns:
        return True
    actual = sympy.Matrix([[sympy.Rational(c) for c in row] for row in actual_rows]).T
    expected_cols = [[sympy.Rational(row[0]) for row in col_matrix] for col_matrix in expected_columns]
    expected = sympy.Matrix.hstack(*[sympy.Matrix(col) for col in expected_cols])
    joint = actual.row_join(expected)
    return actual.rank() == expected.rank() == joint.rank()


def test_mv_e_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    assert len(MV_E) == 12
    for row in MV_E:
        line = frozen_row(row["id"])
        assert row["entrada"] in line, row["id"]
        assert row["id"] in line


@pytest.mark.parametrize(
    "row",
    [r for r in MV_E if r["id"] in {f"MV-E-{i:02d}" for i in range(1, 8)}],
    ids=lambda r: r["id"],
)
def test_mv_e_numeric_rank_rows(row):
    matrix = matrices_of(row["entrada"])[0]
    with TestClient(app) as client:
        body = _post(client, "/matrix/rank", {"matrix": matrix})
    assert body["success"] is True, body
    assert str(body["result_text"]) == str(row["esperado"]), (row["id"], body)


def test_mv_e_08_parametric_rank():
    row = next(r for r in MV_E if r["id"] == "MV-E-08")
    matrix = matrices_of(row["entrada"])[0]
    with TestClient(app) as client:
        generic = _post(client, "/matrix/rank", {"matrix": matrix})
        assert generic["success"] is True, generic
        assert str(generic["result_text"]) == "2", generic
        for value, expected in (("1", "1"), ("-1", "1"), ("0", "2"), ("3", "2")):
            specialized = [[c.replace("a", value) for c in row_cells] for row_cells in matrix]
            body = _post(client, "/matrix/rank", {"matrix": specialized})
            assert body["success"] is True, body
            assert str(body["result_text"]) == expected, (value, body)


def test_mv_e_09_kernel_basis_span():
    row = next(r for r in MV_E if r["id"] == "MV-E-09")
    matrix = matrices_of(row["entrada"])[0]
    expected = matrices_of(row["esperado"])
    with TestClient(app) as client:
        body = _post(client, "/matrix/nullspace", {"matrix": matrix})
    assert body["success"] is True, body
    assert _span_equals(body["result_data"], expected), body


def test_mv_e_10_columnspace_basis_span():
    row = next(r for r in MV_E if r["id"] == "MV-E-10")
    matrix = matrices_of(row["entrada"])[0]
    expected = matrices_of(row["esperado"])
    with TestClient(app) as client:
        body = _post(client, "/matrix/columnspace", {"matrix": matrix})
    assert body["success"] is True, body
    assert _span_equals(body["result_data"], expected), body


def test_mv_e_11_kernel_basis_two_vectors():
    row = next(r for r in MV_E if r["id"] == "MV-E-11")
    matrix = matrices_of(row["entrada"])[0]
    expected = matrices_of(row["esperado"])
    with TestClient(app) as client:
        body = _post(client, "/matrix/nullspace", {"matrix": matrix})
    assert body["success"] is True, body
    assert len(body["result_data"]) == 2, body
    assert _span_equals(body["result_data"], expected), body


def test_mv_e_12_rank_nullity():
    row = next(r for r in MV_E if r["id"] == "MV-E-12")
    matrix = matrices_of(row["entrada"])[0]
    with TestClient(app) as client:
        rank_body = _post(client, "/matrix/rank", {"matrix": matrix})
        ker_body = _post(client, "/matrix/nullspace", {"matrix": matrix})
    assert rank_body["success"] and ker_body["success"]
    assert int(rank_body["result_text"]) + len(ker_body["result_data"]) == int(row["esperado"]) == 4
