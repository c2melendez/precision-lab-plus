"""Matrices/Vectores MV-A-01..25: operaciones bÃ¡sicas con matrices.

Bilateral coverage for the MV-A rows of matriz_matrices_vectores. The frozen
source is LaTeX; the product's matrix surface is the /matrix/* API. Two
documented harness translations:

* LaTeX cells keep their exact value (the API accepts ``\\frac`` and ``a/b``).
* A scalar prefix ``k\\cdot A`` uses the same diagonal-matrix route the Plus
  frontend uses (BasicMode.tsx), i.e. ``(k*I) x A`` on /matrix/operations.
* MV-A-24 is a named-matrix expression; it is composed with the product's own
  multiply/subtract endpoints ((A+B)^2-(A^2+2AB+B^2) = BA-AB).
"""
from __future__ import annotations

import gzip
import json
import re
from fractions import Fraction
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_matrices_vectores.md.gz"
JSONL = ROOT / "qa/certification/matrices_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
MV_A = [row for row in ROWS if row["seccion"] == "A"]

MATRIX_RE = re.compile(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", re.S)
CELL_FRAC_RE = re.compile(r"^(-?)\\frac\{([+-]?\d+)\}\{([+-]?\d+)\}$")


def frozen_row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def matrices_of(expression: str) -> list[list[list[str]]]:
    out = []
    for body in MATRIX_RE.findall(expression):
        rows = [r.strip() for r in body.split("\\\\") if r.strip()]
        out.append([[cell.strip() for cell in row.split("&")] for row in rows])
    return out


def cell_fraction(cell: str) -> Fraction:
    compact = re.sub(r"\s+", "", cell)
    frac = CELL_FRAC_RE.fullmatch(compact)
    if frac:
        return Fraction(int(f"{frac.group(1)}{frac.group(2)}"), int(frac.group(3)))
    return Fraction(compact)


def expected_of(row: dict) -> list[list[Fraction]] | Fraction:
    if row["esperado"].startswith("\\begin"):
        body = MATRIX_RE.search(row["esperado"])
        assert body, row
        return [
            [cell_fraction(cell) for cell in line.split("&")]
            for line in (part.strip() for part in body.group(1).split("\\\\"))
            if line
        ]
    return Fraction(row["esperado"])


def _response(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _matrix(client: TestClient, payload: dict) -> list[list[Fraction]]:
    body = _response(client, "/api/v1/matrix/operations", payload)
    assert body["success"] is True, body
    return [[Fraction(cell) for cell in line] for line in body["result_data"]]


def _transpose(client: TestClient, matrix: list[list[str]]) -> list[list[Fraction]]:
    body = _response(client, "/api/v1/matrix/transpose", {"matrix": matrix})
    assert body["success"] is True, body
    return [[Fraction(cell) for cell in line] for line in body["result_data"]]


def _scalar(client: TestClient, path: str, payload: dict) -> Fraction:
    body = _response(client, path, payload)
    assert body["success"] is True, body
    return Fraction(body["result_text"])


def _run(client: TestClient, row: dict) -> list[list[Fraction]] | Fraction:
    expression = row["entrada"]
    cells = matrices_of(expression)
    operation = row["operacion"]
    if row["id"] == "MV-A-24":
        a = [["1", "2"], ["3", "4"]]
        b = [["0", "1"], ["1", "0"]]
        ab = _matrix(client, {"operation": "multiply", "matrix_a": a, "matrix_b": b})
        ba = _matrix(client, {"operation": "multiply", "matrix_a": b, "matrix_b": a})
        return [[ba[r][c] - ab[r][c] for c in range(len(ba[r]))] for r in range(len(ba))]
    if operation == "suma":
        return _matrix(client, {
            "operation": "subtract" if re.search(r"\\end\{pmatrix\}\s*-", expression) else "add",
            "matrix_a": cells[0], "matrix_b": cells[1],
        })
    if operation == "producto":
        prefix = expression.split("\\begin{pmatrix}")[0].strip()
        if prefix:
            size = len(cells[0])
            diagonal = [[prefix if r == c else "0" for c in range(size)] for r in range(size)]
            return _matrix(client, {"operation": "multiply", "matrix_a": diagonal, "matrix_b": cells[0]})
        return _matrix(client, {"operation": "multiply", "matrix_a": cells[0], "matrix_b": cells[1]})
    if operation == "potencia":
        if "^{T}" in expression:
            return _transpose(client, cells[0])
        exponent = re.search(r"\^\{(-?\d+)\}", expression)
        body = _response(client, "/api/v1/matrix/power", {
            "matrix": cells[0], "exponent": int(exponent.group(1)) if exponent else 1,
        })
        assert body["success"] is True, body
        return [[Fraction(c) for c in line] for line in body["result_data"]]
    if operation == "valor":
        return _scalar(client, "/api/v1/matrix/trace", {"matrix": cells[0]})
    if operation == "matriz":
        if expression.lstrip().startswith("\\operatorname{tr}"):
            return _scalar(client, "/api/v1/matrix/trace", {"matrix": cells[0]})
        if "^{T}" in expression:
            return _transpose(client, cells[0])
        if "\\cdot" in expression:
            return _matrix(client, {"operation": "multiply", "matrix_a": cells[0], "matrix_b": cells[1]})
        return _matrix(client, {
            "operation": "subtract" if re.search(r"\\end\{pmatrix\}\s*-", expression) else "add",
            "matrix_a": cells[0], "matrix_b": cells[1],
        })
    raise AssertionError(f"{row['id']}: unsupported operation {operation}")


def test_mv_a_jsonl_is_complete_and_matches_the_frozen_source():
    assert len(ROWS) == 153
    counts: dict[str, int] = {}
    for row in ROWS:
        counts[row["seccion"]] = counts.get(row["seccion"], 0) + 1
    assert counts == {"A": 25, "B": 22, "C": 19, "D": 17, "E": 12, "F": 17, "G": 22, "H": 12, "J": 7}
    assert len(MV_A) == 25
    for row in MV_A:
        line = frozen_row(row["id"])
        assert row["entrada"] in line, row["id"]
        assert row["esperado"] in line, row["id"]


@pytest.mark.parametrize("row", MV_A, ids=[row["id"] for row in MV_A])
def test_mv_a_rows_evaluate_through_the_matrix_api(row):
    with TestClient(app) as client:
        if row["operacion"] == "error":
            cells = matrices_of(row["entrada"])
            if row["id"] == "MV-A-20":
                path, payload = "/api/v1/matrix/operations", {
                    "operation": "add", "matrix_a": cells[0], "matrix_b": cells[1]}
            elif row["id"] == "MV-A-21":
                path, payload = "/api/v1/matrix/operations", {
                    "operation": "multiply", "matrix_a": cells[0], "matrix_b": cells[1]}
            elif row["id"] == "MV-A-22":
                path, payload = "/api/v1/matrix/inverse", {"matrix": cells[0]}
            else:
                path, payload = "/api/v1/matrix/power", {"matrix": cells[0], "exponent": 2}
            body = _response(client, path, payload)
            assert body["success"] is False, body
            assert body["error_code"] == "DIMENSION_MISMATCH", body
            assert body["error_message"], body
            return
        actual = _run(client, row)
        expected = expected_of(row)
        if isinstance(expected, Fraction):
            assert isinstance(actual, Fraction)
            assert actual == expected, (row["id"], actual, expected)
        else:
            assert isinstance(actual, list)
            assert actual == expected, (row["id"], actual, expected)


def test_mv_a_scalar_and_negative_power_keep_exact_values():
    with TestClient(app) as client:
        half = _run(client, next(row for row in MV_A if row["id"] == "MV-A-04"))
        assert half == [[Fraction(1, 2), Fraction(1)], [Fraction(3, 2), Fraction(2)]]
        inverse_squared = _run(client, next(row for row in MV_A if row["id"] == "MV-A-13"))
        assert inverse_squared == [
            [Fraction(11, 2), Fraction(-5, 2)],
            [Fraction(-15, 4), Fraction(7, 4)],
        ]

