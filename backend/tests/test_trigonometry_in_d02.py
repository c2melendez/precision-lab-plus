"""IN-D-02, scoped to the frozen period [0,2*pi), with both endpoints included."""
import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality


def test_in_d02_source_and_exact_closed_interval():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-02 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == [
        "IN-D-02", r"`\cos x\le 0,\quad x\in[0,2\pi)`",
        r"`\left[\frac{\pi}{2},\frac{3\pi}{2}\right]`",
    ]
    result = compute_inequality(parse_inequality_tree("cos(x)<=0"), "x")
    assert result.solution_set == sp.Interval(sp.pi/2, 3*sp.pi/2)
    for endpoint in [sp.pi/2, 3*sp.pi/2]:
        assert result.solution_set.contains(endpoint) is sp.S.true
        assert sp.cos(endpoint) == 0
    assert result.solution_set.is_subset(sp.Interval.Ropen(0, 2*sp.pi)) is True


def test_in_d02_http_exact_principal_period_interval():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": "cos(x)<=0", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "inequality"
    assert body["request_id"]
    assert body["result_text"] == "Interval(pi/2, 3*pi/2)"
    assert body["result_latex"] == sp.latex(sp.Interval(sp.pi/2, 3*sp.pi/2))


def test_in_d02_independent_sign_oracle():
    for angle, expected in [(0, False), (sp.pi/3, False), (sp.pi/2, True),
                            (sp.pi, True), (3*sp.pi/2, True), (7*sp.pi/4, False), (2*sp.pi, False)]:
        assert bool(sp.cos(angle) <= 0) is expected
