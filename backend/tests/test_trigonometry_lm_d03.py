import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_source():
    s = gzip.decompress((Path(__file__).resolve().parents[2]/'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row=next(line for line in s.splitlines() if '| LM-D-03 |' in line)
    assert r'\lim_{x\to 0}\frac{\tan x}{x}' in row
    assert '`1`' in row


def test_service_and_sides():
    for direction in ('both','left','right'):
        assert compute_limit('tan(x)/x','x','0',direction).value == sp.Integer(1)


def test_http_limit():
    with TestClient(app) as c:
        response=c.post('/api/v1/limit',json={'expression':'tan(x)/x','variable':'x','point':'0','direction':'both'})
    assert response.status_code==200,response.text
    assert response.json()['success'],response.json()
    assert response.json()['result_text']=='1'
