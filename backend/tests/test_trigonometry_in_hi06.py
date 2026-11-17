import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality


def test_source():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-HI-06 | `\operatorname{artanh} x<0` | `(-1,0)` |' in source


def test_service_domain_and_endpoints():
    result = compute_inequality(parse_inequality_tree('atanh(x)<0'), 'x').solution_set
    assert result == sp.Interval.open(-1,0)
    assert result.contains(-1) is sp.S.false
    assert result.contains(0) is sp.S.false
    assert result.contains(sp.Rational(-1,2)) is sp.S.true


def test_literal_http():
    with TestClient(app) as client:
        response=client.post('/api/v1/inequality',json={'inequality':r'\operatorname{artanh} x<0','variable':'x'})
    assert response.status_code==200
    assert response.json()['success'],response.json()
    assert response.json()['result_text']==str(sp.Interval.open(-1,0))
