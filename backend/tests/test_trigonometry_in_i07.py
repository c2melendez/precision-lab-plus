"""IN-I-07: arcsin(2x-1) >= 0 on principal domain."""
import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval(sp.Rational(1, 2), 1)

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row = next(line for line in source.splitlines() if '| IN-I-07 |' in line)
    assert [s.strip() for s in row.split('|') if s.strip()] == ['IN-I-07', r'`\arcsin(2x-1)\ge 0`', r'`\left[\frac{1}{2},1\right]`']

def test_service_domain_and_boundary():
    result = compute_inequality(parse_inequality_tree('asin(2*x-1)>=0'), 'x')
    assert result.solution_set == EXPECTED
    assert result.solution_set.contains(sp.Rational(1, 2)) is sp.S.true
    assert result.solution_set.contains(1) is sp.S.true
    assert result.solution_set.contains(0) is sp.S.false
    assert result.solution_set.contains(sp.Rational(3, 2)) is sp.S.false

def test_source_literal_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/inequality', json={'inequality': r'\arcsin(2x-1)\ge 0', 'variable': 'x'})
    assert response.status_code == 200
    body = response.json()
    assert body['success'], body
    assert body['result_text'] == str(EXPECTED) and body['result_latex'] == sp.latex(EXPECTED)

def test_independent_oracle():
    # arcsin(y) >= 0 iff y >= 0, y in [-1,1]
    y = sp.symbols('y')
    domain = sp.Interval(-1, 1)
    expected_y = sp.Interval(0, 1)
    assert domain.intersect(sp.Interval(0, sp.oo)) == expected_y
