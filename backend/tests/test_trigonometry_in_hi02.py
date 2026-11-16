import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

def test_source():
    s=gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-HI-02 | `\operatorname{arsinh} x\le 0`' in s

def test_service():
    r=compute_inequality(parse_inequality_tree('asinh(x)<=0'),'x')
    assert r.solution_set==sp.Interval(-sp.oo,0)
    assert r.solution_set.contains(0) is sp.S.true

def test_literal_http():
    with TestClient(app) as c:
        r=c.post('/api/v1/inequality',json={'inequality':r'\operatorname{arsinh} x\le 0','variable':'x'})
    assert r.status_code==200
    assert r.json()['success'],r.json()
