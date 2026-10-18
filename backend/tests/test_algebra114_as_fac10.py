"""Algebra114 AS-FAC-10 original sum of cubes with two variables via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app


def test_as_fac_10_sum_of_cubes_two_variables_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-10 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**3+y**3"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y = sp.symbols("x y")
    actual = sp.sympify(result["result_text"])
    expected = (x+y)*(x*x-x*y+y*y)
    assert sp.expand(actual-expected) == 0
    assert set(sp.factor_list(actual)[1]) == {(x+y, 1), (x*x-x*y+y*y, 1)}
