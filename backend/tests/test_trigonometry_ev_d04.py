"""Trigonometry EV-D-04: csc(pi/6) = 2 over HTTP evaluate (ASCII channel).

The official matrix entry is LaTeX. Plus certifies the HTTP /evaluate path
using the ASCII witness csc(pi/6); raw LaTeX ingestion is not claimed here.
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
INPUT_ASCII = "csc(pi/6)"
EXPECTED = sp.Integer(2)


def test_ev_d04_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EV-D-04 |" in text
    assert r"\csc\left(\frac{\pi}{6}\right)" in text
    assert re.search(r"\|\s*EV-D-04\s*\|[^\n]*\|\s*`2`\s*\|", text)


def test_ev_d04_csc_pi_over_6_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    got = sp.sympify(result["result_text"].replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
