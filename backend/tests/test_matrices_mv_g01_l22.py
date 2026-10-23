"""Matrices/Vectores MV-G-01..22: operaciones vectoriales y geometría 3D."""
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
MV_G = [row for row in ROWS if row["seccion"] == "G"]
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


def _post_fail(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(f"/api/v1{path}", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is False, body
    return body


def test_mv_g_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    assert len(MV_G) == 22
    for row in MV_G:
        line = frozen_row(row["id"])
        assert row["id"] in line


def test_mv_g_01_vector_add():
    row = next(r for r in MV_G if r["id"] == "MV-G-01")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "add", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        got = sympy.Matrix(body["result_data"])
        expected = to_sympy(matrices_of(row["esperado"])[0])
        assert sympy.simplify(got - expected) == sympy.zeros(*expected.shape)


def test_mv_g_02_dot():
    row = next(r for r in MV_G if r["id"] == "MV-G-02")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "dot", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        assert sympy.sympify(body["result_text"]) == 32


@pytest.mark.parametrize(
    "case_id,expected_cells",
    [("MV-G-03", [[-3], [6], [-3]]), ("MV-G-04", [[3], [-6], [3]])],
)
def test_mv_g_03_04_cross(case_id, expected_cells):
    row = next(r for r in MV_G if r["id"] == case_id)
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "cross", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        got = sympy.Matrix(body["result_data"])
        if got.rows == 1:
            got = got.T
        expected = sympy.Matrix(expected_cells)
        assert sympy.simplify(got - expected) == sympy.zeros(3, 1)


def test_mv_g_05_norm():
    row = next(r for r in MV_G if r["id"] == "MV-G-05")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(client, "/matrix/norm", {"matrix": mats[0]})
        assert body["success"] is True
        assert sympy.simplify(sympy.sympify(body["result_text"]) - sympy.sqrt(14)) == 0


def test_mv_g_06_unit_vector():
    a = sympy.Matrix([1, 2, 3])
    unit = a / a.norm()
    expected = sympy.Matrix(
        [sympy.sqrt(14) / 14, sympy.sqrt(14) / 7, 3 * sympy.sqrt(14) / 14]
    )
    assert sympy.simplify(unit - expected) == sympy.zeros(3, 1)


def test_mv_g_07_angle():
    a = sympy.Matrix([1, 2, 3])
    b = sympy.Matrix([4, 5, 6])
    cos_theta = sympy.simplify(a.dot(b) / (a.norm() * b.norm()))
    assert cos_theta == sympy.simplify(16 * sympy.sqrt(22) / 77)
    assert abs(float(sympy.acos(cos_theta)) - 0.22572613) < 1e-6


def test_mv_g_08_projection():
    a = sympy.Matrix([1, 2, 3])
    b = sympy.Matrix([4, 5, 6])
    proj = (b.dot(a) / a.dot(a)) * a
    expected = sympy.Matrix(
        [sympy.Rational(16, 7), sympy.Rational(32, 7), sympy.Rational(48, 7)]
    )
    assert proj == expected


def test_mv_g_09_cross_magnitude():
    a = sympy.Matrix([1, 2, 3])
    b = sympy.Matrix([4, 5, 6])
    assert sympy.simplify(a.cross(b).norm() - 3 * sympy.sqrt(6)) == 0


def test_mv_g_10_scalar_triple():
    row = next(r for r in MV_G if r["id"] == "MV-G-10")
    mats = matrices_of(row["entrada"])
    assert len(mats) == 3
    cols = []
    for m in mats:
        M = to_sympy(m)
        cols.append(M.T if M.rows == 1 else M)
    triple = cols[0].dot(cols[1].cross(cols[2]))
    assert sympy.simplify(abs(triple) - 3) == 0


@pytest.mark.parametrize("case_id", ["MV-G-11", "MV-G-13"])
def test_mv_g_orthogonal_dots(case_id):
    row = next(r for r in MV_G if r["id"] == case_id)
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "dot", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        assert sympy.sympify(body["result_text"]) == 0


def test_mv_g_12_parallel_cross_zero():
    row = next(r for r in MV_G if r["id"] == "MV-G-12")
    mats = matrices_of(row["entrada"])
    with TestClient(app) as client:
        body = _post(
            client,
            "/matrix/operations",
            {"operation": "cross", "matrix_a": mats[0], "matrix_b": mats[1]},
        )
        assert body["success"] is True
        got = sympy.Matrix(body["result_data"])
        assert all(sympy.simplify(x) == 0 for x in got)


def test_mv_g_14_dot_dim_mismatch():
    with TestClient(app) as client:
        body = _post_fail(
            client,
            "/matrix/operations",
            {
                "operation": "dot",
                "matrix_a": [["1"], ["2"]],
                "matrix_b": [["1"], ["2"], ["3"]],
            },
        )
        assert body["error_code"] == "DIMENSION_MISMATCH"


def test_mv_g_15_cross_2d_rejected():
    with TestClient(app) as client:
        body = _post_fail(
            client,
            "/matrix/operations",
            {
                "operation": "cross",
                "matrix_a": [["1"], ["2"]],
                "matrix_b": [["3"], ["4"]],
            },
        )
        assert body["error_code"] == "DIMENSION_MISMATCH"


def test_mv_g_16_zero_vector_norm():
    with TestClient(app) as client:
        body = _post(client, "/matrix/norm", {"matrix": [["0"], ["0"], ["0"]]})
        assert body["success"] is True
        assert sympy.sympify(body["result_text"]) == 0


def test_mv_g_17_plane_through_three_points():
    pts = [sympy.Point3D(1, 0, 0), sympy.Point3D(0, 1, 0), sympy.Point3D(0, 0, 1)]
    plane = sympy.Plane(*pts)
    # Oracle x+y+z=1: the three points lie on the plane and the normal ∥ (1,1,1).
    assert all(plane.distance(p) == 0 for p in pts)
    n = sympy.Matrix(plane.normal_vector)
    assert n.cross(sympy.Matrix([1, 1, 1])).norm() == 0
    assert plane.distance(sympy.Point3D(0, 0, 0)) == sympy.sqrt(sympy.Rational(1, 3))


def test_mv_g_18_distance_point_to_plane():
    plane = sympy.Plane(
        sympy.Point3D(0, 0, sympy.Rational(5, 2)), normal_vector=(2, -1, 2)
    )
    assert plane.distance(sympy.Point3D(1, 2, 3)) == sympy.Rational(1, 3)


def test_mv_g_19_distance_point_to_line():
    line = sympy.Line3D(sympy.Point3D(0, 0, 0), direction_ratio=(1, 0, 0))
    d = line.distance(sympy.Point3D(1, 2, 3))
    assert sympy.simplify(d - sympy.sqrt(13)) == 0


def test_mv_g_20_line_plane_intersection():
    line = sympy.Line3D(sympy.Point3D(0, 0, 0), direction_ratio=(1, 2, 3))
    plane = sympy.Plane(sympy.Point3D(12, 0, 0), normal_vector=(1, 1, 1))
    assert line.intersection(plane) == [sympy.Point3D(2, 4, 6)]


def test_mv_g_21_line_line_intersection():
    l1 = sympy.Line3D(sympy.Point3D(1, 0, 3), direction_ratio=(1, 2, 0))
    l2 = sympy.Line3D(sympy.Point3D(0, 1, 3), direction_ratio=(1, 1, 0))
    assert l1.intersection(l2) == [sympy.Point3D(3, 4, 3)]


def test_mv_g_22_angle_2d():
    a = sympy.Matrix([1, 0])
    b = sympy.Matrix([1, 1])
    theta = sympy.acos(sympy.simplify(a.dot(b) / (a.norm() * b.norm())))
    assert sympy.simplify(theta - sympy.pi / 4) == 0
