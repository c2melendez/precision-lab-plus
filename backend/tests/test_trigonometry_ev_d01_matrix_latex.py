"""EV-D-01 matrix entry: \\sin\\left(\\frac{\\pi}{6}\\right) -> 1/2 sent as the matrix LaTeX literal.

Test-first focal case for the exact frozen input (radians). The ASCII witness
sin(pi/6) is covered by test_trigonometry_ev_d01.py; this file checks that the
LaTeX literal of the matrix row is evaluated over HTTP /evaluate too.
"""
import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

LATEX_LITERAL = r"\sin\left(\frac{\pi}{6}\right)"


@pytest.mark.xfail(
    strict=True,
    reason="BLOCKED: ingesta LaTeX (\\left, \\frac, \\pi) en /evaluate fuera del alcance de certificacion; EV-D-01 BLOCKED en Plus",
)
def test_ev_d01_matrix_latex_literal_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": LATEX_LITERAL})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    got = sp.sympify(payload["result_text"].replace("^", "**"))
    assert sp.simplify(got - sp.Rational(1, 2)) == 0, payload
