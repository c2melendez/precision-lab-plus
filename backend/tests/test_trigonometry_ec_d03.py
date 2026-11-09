"""Trigonometría EC-D-03: tan(x)=sqrt(3), familia periódica real completa."""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
client = TestClient(app)


def test_ec_d03_source_row_and_periodic_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-03 |" in source
    assert r"\tan x=\sqrt{3}" in source
    assert r"x=\frac{\pi}{3}+k\pi" in source
    assert r"k\in\mathbb{Z}" in source


def test_ec_d03_http_solve_returns_complete_integer_parameter_family():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "tan(x)=sqrt(3)", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None
    assert len(body["result_data"]) == 1

    family = body["result_data"][0]
    assert "ImageSet" in family["text"]
    assert "pi" in family["text"]
    assert "Integers" in family["text"]
    assert r"\mathbb{Z}" in family["latex"]
    assert r"\pi" in family["latex"]

    x = sp.Symbol("x", real=True)
    expected = sp.solveset(sp.tan(x) - sp.sqrt(3), x, domain=sp.S.Reals)
    assert isinstance(expected, sp.ImageSet)
    assert expected.lamda.variables
    parameter = expected.lamda.variables[0]
    for k in (-3, 0, 2):
        member = sp.simplify(expected.lamda.expr.subs(parameter, k))
        assert sp.simplify(member - (sp.pi / 3 + k * sp.pi)) == 0
        assert sp.simplify(sp.tan(member) - sp.sqrt(3)) == 0
