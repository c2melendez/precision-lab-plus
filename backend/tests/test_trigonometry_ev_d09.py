"""Trigonometry EV-D-09: cos(2) approx -0.416146837 over HTTP evaluate (ASCII channel).

The official matrix entry documents an approximation (`\\approx -0.416146837`,
9 decimals). Plus certifies that the HTTP path keeps the exact symbolic form
cos(2) and that its high-precision numeric value matches the documented
rounding within half a unit of the last documented digit.
"""
from pathlib import Path
import gzip
import re

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
INPUT_ASCII = "cos(2)"
DOCUMENTED = sp.Float("-0.416146837")
DOCUMENTED_DECIMALS = 9
# Protocol rule 3: half a unit of the last documented digit.
TOLERANCE = 5e-10


def test_ev_d09_source_row_present_and_frozen():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in text.splitlines() if "| EV-D-09 |" in line), "")
    assert row, "EV-D-09 row missing from frozen trigonometry matrix"
    assert r"\cos(2)" in row
    assert r"\approx" in row
    assert "-0.416146837" in row


def test_ev_d09_documented_value_is_correct_rounding():
    assert round(float(sp.cos(2)), DOCUMENTED_DECIMALS) == float(DOCUMENTED)


def test_ev_d09_cos_two_http_ascii_keeps_exact_form_and_matches_documented():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    text = payload["result_text"]
    # Approx rows still require an exact form: a decimal-only output does not certify.
    assert not re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", text), text
    got = sp.sympify(text.replace("^", "**"))
    assert sp.simplify(got - sp.cos(2)) == 0
    assert abs(float(sp.N(got, 30)) - float(DOCUMENTED)) <= TOLERANCE
