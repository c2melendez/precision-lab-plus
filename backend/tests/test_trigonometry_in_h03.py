import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

BOUND=sp.log(3)/2
EXPECTED=sp.Interval(-sp.oo,BOUND)

def test_source():
    source=gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-H-03 | `\tanh x\le\frac{1}{2}`' in source

def test_service():
    result=compute_inequality(parse_inequality_tree('tanh(x)<=1/2'),'x')
    assert result.solution_set == sp.Interval(-sp.oo,sp.atanh(sp.Rational(1,2)))
    assert sp.simplify(sp.atanh(sp.Rational(1,2)).rewrite(sp.log)-BOUND)==0
    assert result.solution_set.contains(sp.atanh(sp.Rational(1,2))) is sp.S.true

def test_literal_http():
    with TestClient(app) as c:
        r=c.post('/api/v1/inequality',json={'inequality':r'\tanh x\le\frac{1}{2}','variable':'x'})
    assert r.status_code == 200
    assert r.json()['success'],r.json()
