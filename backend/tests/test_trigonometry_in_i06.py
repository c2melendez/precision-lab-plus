"""IN-I-06 uses the matrix's real principal arccot branch (0, pi)."""
import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.open(1, sp.oo)

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row = next(line for line in source.splitlines() if '| IN-I-06 |' in line)
    assert [s.strip() for s in row.split('|') if s.strip()] == ['IN-I-06', r'`\operatorname{arccot} x<\frac{\pi}{4}`', r'`(1,\infty)`']

def test_service_principal_branch():
    result = compute_inequality(parse_inequality_tree('acot(x)<pi/4'), 'x')
    assert result.solution_set == EXPECTED
    for value in [-1, 0, 1]:
        assert result.solution_set.contains(value) is sp.S.false
    assert result.solution_set.contains(2) is sp.S.true

def test_source_literal_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/inequality', json={'inequality':r'\operatorname{arccot} x<\frac{\pi}{4}', 'variable':'x'})
    assert response.status_code == 200
    body = response.json()
    assert body['success'], body
    assert body['result_text'] == str(EXPECTED) and body['result_latex'] == sp.latex(EXPECTED)

def test_independent_principal_branch_oracle():
    principal = lambda x: sp.pi/2 - sp.atan(x)
    assert principal(-1) > sp.pi/4 and principal(0) > sp.pi/4
    assert principal(1) == sp.pi/4 and principal(2) < sp.pi/4


def test_neighboring_comparisons_keep_fallback():
    from unittest.mock import patch
    for text in ["acot(x)<=pi/4", "acot(x)<pi/3", "acot(2*x)<pi/4"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(text), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345)

def test_literal_rejects_unsafe_suffix():
    import pytest
    with pytest.raises((ValueError, TypeError)):
        parse_inequality_tree(r"\operatorname{arccot} x<\frac{\pi}{4};open(1)")
