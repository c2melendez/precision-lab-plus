import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

def test_source():
    s=gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-H-04 | `\sinh x<-1`' in s

def test_service():
    r=compute_inequality(parse_inequality_tree('sinh(x)<-1'),'x')
    b=-sp.asinh(1)
    assert r.solution_set.left == -sp.oo and r.solution_set.right_open
    assert sp.simplify(sp.expand_log(r.solution_set.right-b, force=True)) == 0
    assert sp.simplify(sp.asinh(1).rewrite(sp.log)-sp.log(1+sp.sqrt(2)))==0
    assert r.solution_set.contains(r.solution_set.right) is sp.S.false

def test_literal_http():
    with TestClient(app) as c:
        r=c.post('/api/v1/inequality',json={'inequality':r'\sinh x<-1','variable':'x'})
    assert r.status_code==200
    assert r.json()['success'],r.json()
