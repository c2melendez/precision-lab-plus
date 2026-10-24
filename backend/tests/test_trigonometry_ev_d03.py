"""Trigonometry EV-D-03: tan(pi/4) = 1 over HTTP evaluate (ASCII channel).

Official matrix entry is LaTeX; Plus /evaluate HTTP is certified here on the
ASCII witness tan(pi/4). Raw LaTeX ingestion is a separate conversion channel
and is not claimed by this scoped case.
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
INPUT_ASCII = "tan(pi/4)"
EXPECTED = sp.Integer(1)


def test_ev_d03_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EV-D-03 |" in text
    assert r"\tan\left(\frac{\pi}{4}\right)" in text
    assert re.search(r"\|\s*EV-D-03\s*\|[^\n]*\|\s*`1`\s*\|", text)


def test_ev_d03_tan_pi_over_4_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    got = sp.sympify(result["result_text"].replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
