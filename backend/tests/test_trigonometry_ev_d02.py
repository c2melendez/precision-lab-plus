"""Trigonometry EV-D-02: cos(pi/3) = 1/2 over HTTP evaluate (ASCII channel).

Official matrix entry is LaTeX; Plus /evaluate HTTP is certified here on the
ASCII witness cos(pi/3). Raw LaTeX ingestion is a separate conversion channel
and is not claimed by this scoped case.
"""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
INPUT_ASCII = "cos(pi/3)"
EXPECTED = sp.Rational(1, 2)


def test_ev_d02_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EV-D-02 |" in text
    assert r"\cos\left(\frac{\pi}{3}\right)" in text
    assert r"\frac{1}{2}" in text


def test_ev_d02_cos_pi_over_3_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    got = sp.sympify(result["result_text"].replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
