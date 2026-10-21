"""Trigonometry EV-D-07: sin(5*pi/4) = -sqrt(2)/2 over HTTP evaluate (ASCII channel).

The official matrix entry is LaTeX. Plus certifies the HTTP /evaluate path
using the ASCII witness sin(5*pi/4); raw LaTeX ingestion is not claimed here.
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
INPUT_ASCII = "sin(5*pi/4)"
EXPECTED = -sp.sqrt(2) / 2


def test_ev_d07_source_row_present_and_frozen():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in text.splitlines() if "| EV-D-07 |" in line), "")
    assert row, "EV-D-07 row missing from frozen trigonometry matrix"
    assert r"\sin\left(\frac{5\pi}{4}\right)" in row
    assert r"-\frac{\sqrt{2}}{2}" in row


def test_ev_d07_sin_5pi_over_4_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    text = payload["result_text"]
    # Exactness guard: the certified value is a radical, not a decimal approximation.
    assert not re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", text), text
    got = sp.sympify(text.replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
    assert abs(float(got) - float(EXPECTED)) < 1e-6
