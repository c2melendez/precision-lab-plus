import gzip
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

def test_service():
    result=compute_inequality(parse_inequality_tree('sech(x)>1/2'),'x')
    assert result.solution_set == sp.Interval.open(-sp.asech(sp.Rational(1,2)),sp.asech(sp.Rational(1,2)))
    assert sp.simplify(sp.asech(sp.Rational(1,2)).rewrite(sp.log) - sp.log(2+sp.sqrt(3))) == 0

def test_literal_http():
    with TestClient(app) as c:
        r=c.post('/api/v1/inequality',json={'inequality':r'\operatorname{sech} x>\frac{1}{2}','variable':'x'})
    assert r.status_code==200
    assert r.json()['success'],r.json()


def test_source_row():
    source=gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    assert r'| IN-H-07 | `\operatorname{sech} x>\frac{1}{2}`' in source

def test_literal_rejects_unsafe_suffix():
    with pytest.raises((ValueError, TypeError)):
        parse_inequality_tree(r'\operatorname{sech} x>\frac{1}{2};open(1)')
