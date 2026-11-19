import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_source():
    s = gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row=next(line for line in s.splitlines() if '| LM-D-04 |' in line)
    assert r'\lim_{x\to 0}\frac{\sin 3x}{\sin 5x}' in row
    assert r'\frac{3}{5}' in row


def test_service_and_sides():
    for direction in ('both','left','right'):
        assert compute_limit('sin(3*x)/sin(5*x)','x','0',direction).value == sp.Rational(3,5)


def test_http_limit():
    with TestClient(app) as c:
        response=c.post('/api/v1/limit',json={'expression':'sin(3*x)/sin(5*x)','variable':'x','point':'0','direction':'both'})
    assert response.status_code==200,response.text
    assert response.json()['success'],response.json()
    assert response.json()['result_text']=='3/5'
