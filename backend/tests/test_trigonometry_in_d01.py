"""IN-D-01: scoped to the frozen period [0,2*pi), not all of R."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality


def test_in_d01_source_and_exact_open_interval():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-01 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == [
        "IN-D-01", r"`\sin x>\frac{1}{2},\quad x\in[0,2\pi)`",
        r"`\left(\frac{\pi}{6},\frac{5\pi}{6}\right)`",
    ]
    result = compute_inequality(parse_inequality_tree("sin(x)>1/2"), "x")
    expected = sp.Interval.open(sp.pi / 6, 5 * sp.pi / 6)
    assert result.solution_set == expected
    assert result.solution_set.is_subset(sp.Interval.Ropen(0, 2 * sp.pi)) is True
    assert result.solution_set.contains(sp.pi / 6) is sp.S.false
    assert result.solution_set.contains(5 * sp.pi / 6) is sp.S.false
    assert result.solution_set.contains(sp.pi / 2) is sp.S.true
    assert result.solution_set.contains(sp.pi) is sp.S.false


def test_in_d01_http_returns_exact_principal_period_interval():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": "sin(x)>1/2", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "inequality"
    assert body["request_id"]
    assert body["result_text"] == "Interval.open(pi/6, 5*pi/6)"
    assert body["result_latex"] == sp.latex(sp.Interval.open(sp.pi / 6, 5 * sp.pi / 6))


def test_in_d01_independent_sign_oracle():
    # On [0,2*pi), sin crosses 1/2 at pi/6 and 5*pi/6 and exceeds it only between.
    for angle, expected in [(0, False), (sp.pi/12, False), (sp.pi/3, True),
                            (sp.pi/2, True), (3*sp.pi/4, True), (sp.pi, False),
                            (3*sp.pi/2, False), (2*sp.pi, False)]:
        assert bool(sp.sin(angle) > sp.Rational(1, 2)) is expected
