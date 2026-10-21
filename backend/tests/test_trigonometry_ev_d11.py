"""Trigonometry EV-D-11: sin^2(pi/8)+cos^2(pi/8) = 1 over HTTP evaluate (ASCII channel).

The official matrix entry is LaTeX. Plus certifies the HTTP /evaluate path
using the ASCII witness (sin(pi/8))^2+(cos(pi/8))^2; raw LaTeX ingestion is
not claimed here.
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
INPUT_ASCII = "sin(pi/8)^2+cos(pi/8)^2"
EXPECTED = sp.Integer(1)


def test_ev_d11_source_row_present_and_frozen():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in text.splitlines() if "| EV-D-11 |" in line), "")
    assert row, "EV-D-11 row missing from frozen trigonometry matrix"
    assert r"\sin^{2}\left(\frac{\pi}{8}\right)+\cos^{2}\left(\frac{\pi}{8}\right)" in row
    assert "| `1` |" in row


def test_ev_d11_identity_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    got = sp.sympify(payload["result_text"].replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
    assert payload["result_text"].strip() == "1"
