"""IN-H-06: a closed symmetric interval for cosh(2*x) <= 3."""
import gzip
from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

BOUND = sp.log(1 + sp.sqrt(2))
EXPECTED = sp.Interval(-BOUND, BOUND)


def test_source_row():
    source = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
    with gzip.open(source, "rt", encoding="utf-8") as matrix:
        row = next(line for line in matrix if line.startswith("| IN-H-06 |"))
    assert [cell.strip().strip("`") for cell in row.split("|") if cell.strip()] == [
        "IN-H-06",
        r"\cosh(2x)\le 3",
        r"\left[-\ln\left(1+\sqrt{2}\right),\ \ln\left(1+\sqrt{2}\right)\right]",
    ]


def assert_closed_interval(solution):
    assert isinstance(solution, sp.Interval)
    assert not solution.left_open and not solution.right_open
    # The exponential is injective on the real line. Rewriting acosh
    # as a logarithm makes the exact comparison algebraic.
    for actual, expected in zip((solution.start, solution.end), (EXPECTED.start, EXPECTED.end)):
        assert sp.simplify(sp.exp(2 * actual.rewrite(sp.log)) - sp.exp(2 * expected)) == 0
        assert solution.contains(actual) is sp.S.true
    assert solution.contains(0) is sp.S.true
    for point in (-1, 1):
        assert sp.cosh(2 * point) > 3
        assert solution.contains(point) is sp.S.false


@pytest.mark.parametrize(("expression", "variable"), [("cosh(2*x)<=3", "x"), ("3>=cosh(2*t)", "t")])
def test_service_closed_interval(expression, variable):
    assert_closed_interval(compute_inequality(parse_inequality_tree(expression), variable).solution_set)


def test_literal_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": r"\cosh(2x)\le 3", "variable": "x"})
        normalized = client.post("/api/v1/inequality", json={"inequality": "cosh(2*x)<=3", "variable": "x"})
    assert response.status_code == normalized.status_code == 200
    body = response.json()
    other = normalized.json()
    assert body["success"] and other["success"], (body, other)
    assert body["operation"] == "inequality"
    result = compute_inequality(parse_inequality_tree("cosh(2*x)<=3"), "x").solution_set
    assert_closed_interval(result)
    assert body["result_text"] == other["result_text"] == str(result)
    assert body["result_latex"] == other["result_latex"] == sp.latex(result)
