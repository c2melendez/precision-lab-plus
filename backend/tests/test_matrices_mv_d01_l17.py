"""Matrices/Vectores MV-D-01..17: sistemas, rref, LU y Gram-Schmidt.

Bilateral coverage for the MV-D rows of matriz_matrices_vectores. The frozen
source is LaTeX; the product surfaces are ``/solve/system`` and ``/matrix/*``.

Documented harness translations:

* LaTeX ``cases`` rows are converted to the plain equation syntax the Plus
  frontend sends (``\\frac{x}{2}`` -> ``(x)/(2)``). D-13 additionally inserts
  the multiplication sign in ``ay`` -> ``a*y``.
* Systems may have a different number of equations and variables:
  underdetermined (D-04/06/07/11) and overdetermined (D-09/10) are part of
  the product contract.
* Parametric solutions keep the product's free variable (``z``/``y``); the
  oracle uses ``t``. The test accepts the exact same solution set after the
  documented parameter renaming, never a different basis.
* Gram-Schmidt is defined over the matrix rows; the frozen oracle lists the
  resulting vectors as columns, so the test transposes the orientation.
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
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_matrices_vectores.md.gz"
JSONL = ROOT / "qa/certification/matrices_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
MV_D = [row for row in ROWS if row["seccion"] == "D"]
SYSTEM_ROWS = [row for row in MV_D if row["operacion"] == "resolver"]

MATRIX_RE = re.compile(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", re.S)
CELL_FRAC_RE = re.compile(r"^(-?)\\frac\{([+-]?\d+)\}\{([+-]?\d+)\}$")
FRAC_RE = re.compile(r"\\frac\{([^{}]+)\}\{([^{}]+)\}")
T = sympy.Symbol("t")
TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def frozen_row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def backend_cell(cell: str) -> str:
    compact = re.sub(r"\s+", "", cell)
    frac = CELL_FRAC_RE.fullmatch(compact)
    if frac:
        return f"{frac.group(1)}{frac.group(2)}/{frac.group(3)}"
    return compact.replace("\\left", "").replace("\\right", "")


def matrices_of(expression: str) -> list[list[list[str]]]:
    out = []
    for body in MATRIX_RE.findall(expression):
        rows = [row.strip() for row in body.split("\\\\") if row.strip()]
        out.append([[backend_cell(cell) for cell in row.split("&")] for row in rows])
    return out


def latex_to_sympy(source: str) -> sympy.Expr:
    text = source.replace("\\left", "").replace("\\right", "")
    text = text.replace("\\,", " ").replace("\\ ", " ").replace("\\cdot", "*")
    previous = None
    while previous != text:
        previous = text
        text = FRAC_RE.sub(lambda match: f"(({match.group(1)})/({match.group(2)}))", text)
    text = text.replace("\\neq", "!=").replace("≠", "!=")
    return parse_expr(text, transformations=TRANSFORMS, local_dict={"t": T})


def system_variables(row: dict) -> list[str]:
    match = re.search(r"\(([a-z](?:\s*,\s*[a-z])*)\)=", row["esperado"])
    if match:
        return [name.strip() for name in match.group(1).split(",")]
    if row["id"] in {"MV-D-05", "MV-D-10"}:
        return ["x", "y"]
    raise AssertionError(row["id"])


def system_equations(row: dict) -> list[str]:
    source = row["entrada"]
    match = re.fullmatch(r"\\begin\{cases\}(.*?)\\end\{cases\}", source, re.S)
    assert match is not None, row["id"]
    equations = []
    for equation in match.group(1).split("\\\\"):
        text = equation.strip()
        previous = None
        while previous != text:
            previous = text
            text = FRAC_RE.sub(lambda m: f"(({m.group(1)})/({m.group(2)}))", text)
        text = text.replace("\\left", "").replace("\\right", "").replace("\\,", " ")
        if row["id"] == "MV-D-13":
            text = re.sub(r"([a-z])([a-z])(?==)", r"\1*\2", text)
        equations.append(text)
    return equations


def expected_tuple(row: dict) -> list[sympy.Expr] | None:
    after_equals = row["esperado"].split("=", 1)[1]
    match = re.search(r"\\left\((.*?)\\right\)", after_equals, re.S)
    if not match:
        return None
    return [latex_to_sympy(value) for value in re.split(r",\\?\s+", match.group(1).strip()) if value]


def assignments_from_text(text: str) -> dict[str, sympy.Expr]:
    result: dict[str, sympy.Expr] = {}
    for assignment in text.split(", "):
        name, value = assignment.split("=", 1)
        result[name.strip()] = parse_expr(value.strip(), transformations=TRANSFORMS, local_dict={"t": T})
    return result


def actual_tuple(body: dict) -> list[sympy.Expr]:
    text = body["result_data"][0]["text"]
    return [value for value in assignments_from_text(text).values()]


def _response(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _run_system(client: TestClient, row: dict) -> dict:
    return _response(
        client,
        "/api/v1/solve/system",
        {"equations": system_equations(row), "variables": system_variables(row)},
    )


def test_mv_d_jsonl_is_complete_and_matches_the_frozen_source():
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
    assert len(MV_D) == 17
    assert len(SYSTEM_ROWS) == 13
    for row in MV_D:
        line = frozen_row(row["id"])
        assert row["entrada"] in line, row["id"]
        assert row["esperado"] in line, row["id"]


@pytest.mark.parametrize("row", SYSTEM_ROWS, ids=[row["id"] for row in SYSTEM_ROWS])
def test_mv_d_systems_evaluate_through_the_real_api(row):
    with TestClient(app) as client:
        body = _run_system(client, row)

    if row["id"] in {"MV-D-05", "MV-D-10"}:
        assert body["success"] is True, body
        assert body["result_data"] == [], body
        assert any(
            "no tiene solución" in warning.lower() or "inconsistente" in warning.lower()
            for warning in body["warnings"]
        ), body
        return

    assert body["success"] is True, body
    if row["id"] == "MV-D-13":
        assert len(body["result_data"]) == 2, body
        generic = next(item for item in body["result_data"] if "a!=1" in item["text"])
        special = next(item for item in body["result_data"] if "a=1" in item["text"])
        expected_generic = [re.search(r"\((\d+),(\d+)\)", row["esperado"]).group(1), re.search(r"\((\d+),(\d+)\)", row["esperado"]).group(2)]
        generic_values = assignments_from_text(generic["text"].split(": ", 1)[1])
        assert [sympy.simplify(value) for value in generic_values.values()] == [
            sympy.Integer(expected_generic[0]),
            sympy.Integer(expected_generic[1]),
        ]
        assert "infinitas soluciones" in special["text"]
        special_values = assignments_from_text(special["text"].split(": ", 1)[1].split(" (", 1)[0])
        assert sympy.simplify(special_values["x"] + special_values["y"] - 1) == 0
        return

    expected = expected_tuple(row)
    assert expected is not None, row["id"]
    actual = actual_tuple(body)
    assert len(actual) == len(expected), (row["id"], body)

    if row["esperado"].endswith(r"t\in\mathbb{R}"):
        free_symbols = set().union(*(value.free_symbols for value in actual))
        assert len(free_symbols) == 1, (row["id"], actual, free_symbols)
        actual = [value.subs(next(iter(free_symbols)), T) for value in actual]
    for actual_value, expected_value in zip(actual, expected):
        assert sympy.simplify(actual_value - expected_value) == 0, (
            row["id"],
            actual_value,
            expected_value,
        )


def test_mv_d_rref_rows_are_exact():
    with TestClient(app) as client:
        for row in [row for row in MV_D if row["id"] in {"MV-D-14", "MV-D-15"}]:
            body = _response(client, "/api/v1/matrix/rref", {"matrix": matrices_of(row["entrada"])[0]})
            assert body["success"] is True, body
            expected = matrices_of(row["esperado"])[0]
            assert len(body["result_data"]) == len(expected), row["id"]
            for actual_row, expected_row in zip(body["result_data"], expected):
                assert [Fraction(cell) for cell in actual_row] == [Fraction(cell) for cell in expected_row], row["id"]


def test_mv_d_lu_is_verified_without_pivoting():
    row = next(row for row in MV_D if row["id"] == "MV-D-16")
    with TestClient(app) as client:
        body = _response(client, "/api/v1/matrix/lu", {"matrix": matrices_of(row["entrada"])[0]})

    assert body["success"] is True, body
    expected = matrices_of(row["esperado"])
    assert len(expected) == 2
    assert set(body["result_matrices"]) == {"L", "U"}
    for name, matrix in zip(("L", "U"), expected):
        assert body["result_matrices"][name] == matrix, (name, body)
    assert body["result_latex"]


def test_mv_d_lu_reports_zero_pivot_instead_of_pivoting():
    with TestClient(app) as client:
        body = _response(client, "/api/v1/matrix/lu", {"matrix": [["0", "1"], ["1", "0"]]})
    assert body["success"] is False, body
    assert body["error_code"] == "UNSUPPORTED_OPERATION", body
    assert "pivote" in body["error_message"].lower(), body


def test_mv_d_gram_schmidt_is_orthogonal_without_normalizing():
    row = next(row for row in MV_D if row["id"] == "MV-D-17")
    vectors = [
        match.group(1).split(",")
        for match in re.finditer(r"\(([0-9]+(?:\s*,\s*[0-9]+)+)\)", row["entrada"])
    ]
    with TestClient(app) as client:
        body = _response(client, "/api/v1/matrix/gram-schmidt", {"matrix": vectors})

    assert body["success"] is True, body
    expected_columns = matrices_of(row["esperado"])
    expected = [[column[coordinate][0] for coordinate in range(len(column))] for column in expected_columns]
    assert len(body["result_data"]) == len(expected), body
    for actual_row, expected_row in zip(body["result_data"], expected):
        assert [Fraction(cell) for cell in actual_row] == [Fraction(cell) for cell in expected_row], body
    for index, first in enumerate(body["result_data"]):
        for second in body["result_data"][index + 1 :]:
            dot = sum(Fraction(a) * Fraction(b) for a, b in zip(first, second))
            assert dot == 0, (first, second)
