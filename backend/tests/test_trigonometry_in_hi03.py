import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

def test_source():
    s=gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-HI-03 | `\operatorname{arcosh} x<1`' in s

def test_service():
    r=compute_inequality(parse_inequality_tree('acosh(x)<1'),'x')
    assert r.solution_set==sp.Interval.Ropen(1,sp.cosh(1))
    assert r.solution_set.contains(1) is sp.S.true
    assert r.solution_set.contains(sp.cosh(1)) is sp.S.false
    assert r.solution_set.contains(0) is sp.S.false

def test_literal_http():
    with TestClient(app) as c:
        r=c.post('/api/v1/inequality',json={'inequality':r'\operatorname{arcosh} x<1','variable':'x'})
    assert r.status_code==200
    assert r.json()['success'],r.json()
    assert r.json()['result_text']==str(sp.Interval.Ropen(1,sp.cosh(1)))
