"""Matrices/Vectores MV-J-01..07: rotaciones, reflexión, shear, composición trig."""
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
MV_J = [row for row in ROWS if row["seccion"] == "J"]
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


def test_mv_j_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    assert len(MV_J) == 7
    for row in MV_J:
        assert row["id"] in frozen_row(row["id"])
    # Catálogo completo A–H + J (sin I)
    sections = {r["seccion"] for r in ROWS}
    assert sections == {"A", "B", "C", "D", "E", "F", "G", "H", "J"}


def test_mv_j_01_rotation_90_of_e1():
    row = next(r for r in MV_J if r["id"] == "MV-J-01")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "multiply", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        assert sympy.Matrix(body["result_data"]) == sympy.Matrix([[0], [1]])


def test_mv_j_02_rotation_det_is_one():
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/determinant",
            {"matrix": [["0", "-1"], ["1", "0"]]},
        )
        assert body["success"] is True
        assert sympy.sympify(body["result_text"]) == 1


def test_mv_j_03_rotation_to_fourth_is_identity():
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/power",
            {"matrix": [["0", "-1"], ["1", "0"]], "exponent": 4},
        )
        assert body["success"] is True
        got = sympy.Matrix(body["result_data"])
        assert got == sympy.eye(2)


def test_mv_j_04_reflection():
    row = next(r for r in MV_J if r["id"] == "MV-J-04")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "multiply", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        assert sympy.Matrix(body["result_data"]) == sympy.Matrix([[3], [-2]])


def test_mv_j_05_shear():
    row = next(r for r in MV_J if r["id"] == "MV-J-05")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "multiply", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        assert sympy.Matrix(body["result_data"]) == sympy.Matrix([[3], [1]])


def test_mv_j_06_rotation_composition_angle_sum():
    # Producto de rotaciones = rotación de la suma (oráculo SymPy;
    # /matrix/operations no admite símbolos libres en celdas).
    theta, phi = sympy.symbols("theta phi", real=True)
    R = lambda a: sympy.Matrix(
        [[sympy.cos(a), -sympy.sin(a)], [sympy.sin(a), sympy.cos(a)]]
    )
    product = sympy.simplify(R(theta) * R(phi))
    expected = R(theta + phi)
    assert sympy.simplify(product - expected) == sympy.zeros(2)


def test_mv_j_07_diagonal_det():
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/determinant",
            {"matrix": [["2", "0"], ["0", "3"]]},
        )
        assert body["success"] is True
        assert sympy.sympify(body["result_text"]) == 6
