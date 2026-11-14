"""Trigonometria EC-HI-08: artanh x=2 tiene la raiz real exacta tanh 2."""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.solve_service import ResultType, solve_equation

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
client = TestClient(app)


def _source_row(identifier: str) -> list:
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    line = next(
        (candidate for candidate in source.splitlines() if f"| {identifier} |" in candidate),
        "",
    )
    assert line, f"missing frozen source row {identifier}"
    cells = [cell.strip() for cell in line.split("|") if cell.strip()]
    assert len(cells) == 3, cells
    return cells


def test_ec_hi08_source_row_and_exact_root_are_frozen():
    cells = _source_row("EC-HI-08")
    assert cells[0] == "EC-HI-08", cells
    assert r"\operatorname{artanh} x=2" in cells[1], cells
    assert r"x=\tanh 2" in cells[2], cells
    assert "0.964027580" in cells[2], cells


def test_ec_hi08_service_returns_exactly_tanh_two():
    result = solve_equation("artanh(x)=2", "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    assert len(result.solutions) == 1, result.solutions
    root = sp.sympify(result.solutions[0].text.replace("^", "**"))
    assert sp.simplify(root - sp.tanh(2)) == 0, root
    assert abs(sp.N(root, 30) - sp.Float("0.9640275800758169")) < sp.Float("1e-15")


def test_ec_hi08_http_contract_returns_the_frozen_value():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "artanh(x)=2", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None
    assert len(body["result_data"]) == 1, body
    root = sp.sympify(body["result_data"][0]["text"].replace("^", "**"))
    assert sp.simplify(root - sp.tanh(2)) == 0, root

    # Independent oracle: atanh(tanh 2) = 2 and |tanh 2| < 1.
    assert sp.simplify(sp.atanh(sp.tanh(2)) - 2) == 0
    assert sp.Abs(sp.tanh(2)) < 1


def test_ec_hi08_accepts_the_atanh_alias_and_the_reversed_equality():
    alias = solve_equation("atanh(x)=2", "x")
    assert sp.simplify(sp.sympify(alias.solutions[0].text.replace("^", "**")) - sp.tanh(2)) == 0
    reversed_result = solve_equation("2=artanh(x)", "x")
    assert (
        sp.simplify(sp.sympify(reversed_result.solutions[0].text.replace("^", "**")) - sp.tanh(2)) == 0
    )
