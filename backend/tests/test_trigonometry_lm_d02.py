import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_source():
    s = gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row=next(line for line in s.splitlines() if '| LM-D-02 |' in line)
    assert r'\lim_{x\to 0}\frac{1-\cos x}{x^{2}}' in row
    assert r'\frac{1}{2}' in row


def test_exact_service_and_two_sides():
    for direction in ('both','left','right'):
        assert compute_limit('(1-cos(x))/x^2','x','0',direction).value == sp.Rational(1,2)


def test_http_limit():
    with TestClient(app) as c:
        response=c.post('/api/v1/limit',json={'expression':'(1-cos(x))/x^2','variable':'x','point':'0','direction':'both'})
    assert response.status_code==200,response.text
    assert response.json()['success'],response.json()
    assert response.json()['result_text']=='1/2'
