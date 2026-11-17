import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality


def test_source():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-HI-05 | `\operatorname{artanh} x\ge\frac{1}{2}\ln 3`' in source


def test_service():
    result = compute_inequality(parse_inequality_tree('atanh(x)>=ln(3)/2'),'x').solution_set
    assert result.right == 1 and result.right_open and not result.left_open
    assert sp.simplify(result.left.rewrite(sp.exp) - sp.Rational(1,2)) == 0


def test_literal_http():
    with TestClient(app) as c:
        response=c.post('/api/v1/inequality',json={'inequality':r'\operatorname{artanh} x\ge\frac{1}{2}\ln 3','variable':'x'})
    assert response.status_code==200
    assert response.json()['success'],response.json()
    assert response.json()['result_text'] == str(sp.Interval.Ropen(sp.tanh(sp.log(3)/2),1))
