"""TR324 definite integral numeric observations, not exact/display acceptance."""
import gzip
import json
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

ROOT = Path(__file__).resolve().parents[2]
ROWS = json.loads((ROOT / "qa/certification/tr324_definite_integrals.json").read_text())
SOURCE = gzip.decompress((ROOT / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
def anchor(row):
    line = next(line for line in SOURCE.splitlines() if line.startswith("| " + row["id"] + " |"))
    assert chr(96) + row["literal"] + chr(96) in line
    assert chr(96) + row["source_expected"] + chr(96) in line

def payload(row):
    expression = row["expression"]
    for alias, canonical in (("arcsin", "asin"), ("arccos", "acos"), ("arctan", "atan"), ("arccot", "acot")):
        expression = expression.replace(alias, canonical)
    return {"expression": expression, "variable": "x", "lower_bound": row["lower"], "upper_bound": row["upper"]}

@pytest.mark.parametrize("row", [r for r in ROWS if not r.get("capability")], ids=lambda r:r["id"])
def test_definite_real_value(row):
    anchor(row)
    with TestClient(app) as client:
        response = client.post("/api/v1/integral", json=payload(row))
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True, body
    assert body["result_text"] and body["result_latex"]
    assert "+ C" not in body["result_text"]
    got = sp.sympify(body["result_text"].replace("^", "**"), locals={"ln":sp.log})
    assert not got.free_symbols and not got.has(sp.Integral)
    assert got.is_real is True and got.is_finite is True, got
    expected = sp.sympify(row["exact_oracle"])
    assert float(sp.N(expected, 17)) == pytest.approx(row["numeric_oracle"], abs=1e-13, rel=1e-13)
    assert float(sp.N(got, 17)) == pytest.approx(row["numeric_oracle"], abs=1e-9, rel=1e-9)

@pytest.mark.parametrize("row", [r for r in ROWS if r.get("capability")], ids=lambda r:r["id"])
def test_capability_unsupported_infinite_bound(row):
    anchor(row)
    with TestClient(app) as client:
        body = client.post("/api/v1/integral", json=payload(row)).json()
    assert body["success"] is False
    assert body["error_code"] == "UNSUPPORTED_IN_PHASE_1"
    assert body.get("result_text") is None

def test_frozen_decimal_discrepancy():
    row = next(r for r in ROWS if r["id"] == "ID-HI-08")
    assert "0.307426799" in row["source_expected"]
    assert row["numeric_oracle"] == pytest.approx(0.30747679967138351, abs=1e-14)
    assert abs(row["numeric_oracle"] - 0.307426799) > .00005


@pytest.mark.parametrize("expression,lower,upper,expected", [
    ("ln(sin(y))", "pi/2", "0", sp.pi*sp.log(2)/2),
    ("ln(sin(y))", "0", "pi", -sp.pi*sp.log(2)),
    ("sech(y)^2", "1", "-1", -2*sp.tanh(1)),
    ("acosh(y)", "2", "1", sp.sqrt(3)-2*sp.acosh(2)),
])
def test_scoped_definite_exact_controls(expression, lower, upper, expected):
    with TestClient(app) as client:
        body = client.post("/api/v1/integral", json={"expression":expression,"variable":"y","lower_bound":lower,"upper_bound":upper}).json()
    assert body["success"] is True, body
    got = sp.sympify(body["result_text"].replace("^","**"), locals={"ln":sp.log})
    assert not got.has(sp.Integral) and not got.free_symbols
    assert sp.simplify(got-expected)==0
