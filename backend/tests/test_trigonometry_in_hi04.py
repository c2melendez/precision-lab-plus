import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality


def test_source():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-HI-04 | `\operatorname{arcosh} x\ge 0` | `[1,\infty)`' in source


def test_service_domain():
    result = compute_inequality(parse_inequality_tree('acosh(x)>=0'), 'x').solution_set
    assert result == sp.Interval(1, sp.oo)
    assert result.contains(1) is sp.S.true
    assert result.contains(sp.Rational(999,1000)) is sp.S.false
    assert result.contains(2) is sp.S.true


def test_literal_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/inequality', json={'inequality':r'\operatorname{arcosh} x\ge 0', 'variable':'x'})
    assert response.status_code == 200
    assert response.json()['success'], response.json()
    assert response.json()['result_text'] == str(sp.Interval(1, sp.oo))
