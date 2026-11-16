"""IN-H-01: positive hyperbolic sine on the real line."""
import gzip
from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.open(0, sp.oo)


def test_source_row():
    source = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
    with gzip.open(source, "rt", encoding="utf-8") as matrix:
        row = next(line.strip() for line in matrix if line.startswith("| IN-H-01 |"))
    assert row == r"| IN-H-01 | `\sinh x>0` | `(0,\infty)` |"


@pytest.mark.parametrize(("expression", "variable"), [("sinh(x)>0", "x"), ("0<sinh(t)", "t")])
def test_service_sign_and_strict_boundary(expression, variable):
    result = compute_inequality(parse_inequality_tree(expression), variable)
    assert result.solution_set == EXPECTED
    for point in (-1, 0, 1):
        # Independent oracle: sign of exp(2*x)-1, since 2*exp(x) > 0.
        assert result.solution_set.contains(point) == (sp.exp(2 * point) > 1)


def test_source_literal_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": r"\sinh x>0", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"], body
    assert body["result_text"] == str(EXPECTED)
    assert body["result_latex"] == sp.latex(EXPECTED)
