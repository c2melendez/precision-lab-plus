"""TR324 hyperbolic derivatives: fixture anchoring and independent point oracles."""
import gzip
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.derivative_service import compute_derivative

MATRIX = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()

# Independent real-valued expressions from the matrix. Samples avoid singularities
# and lie inside each original function's differentiability domain.
CASES = [
    ('DV-H-01','sinh(x)',[-1,0,1],lambda x: math.cosh(x)),
    ('DV-H-02','cosh(x)',[-1,0,1],lambda x: math.sinh(x)),
    ('DV-H-03','tanh(x)',[-1,0,1],lambda x: 1/math.cosh(x)**2),
    ('DV-H-04','csch(x)',[-2,-1,1,2],lambda x: -math.cosh(x)/math.sinh(x)**2),
    ('DV-H-05','sech(x)',[-1,0,1],lambda x: -math.tanh(x)/math.cosh(x)),
    ('DV-H-06','coth(x)',[-2,-1,1,2],lambda x: -1/math.sinh(x)**2),
    ('DV-H-07','sinh(3*x)',[-1,0,1],lambda x: 3*math.cosh(3*x)),
    ('DV-H-08','ln(cosh(x))',[-1,0,1],lambda x: math.tanh(x)),
    ('DV-H-09','x*sinh(x)',[-1,0,1],lambda x: math.sinh(x)+x*math.cosh(x)),
    ('DV-H-10','tanh(x)^2',[-1,0,1],lambda x: 2*math.tanh(x)/math.cosh(x)**2),
    ('DV-H-11','exp(x)*cosh(x)',[-1,0,1],lambda x: math.exp(2*x)),
    ('DV-H-12','cosh(x)^2-sinh(x)^2',[-1,0,1],lambda x: 0),
    ('DV-HI-01','asinh(x)',[-2,0,2],lambda x: 1/math.sqrt(x*x+1)),
    ('DV-HI-02','acosh(x)',[1.1,2,5],lambda x: 1/math.sqrt(x*x-1)),
    ('DV-HI-03','atanh(x)',[-.8,0,.8],lambda x: 1/(1-x*x)),
    ('DV-HI-04','acoth(x)',[-2,-1.1,1.1,2],lambda x: 1/(1-x*x)),
    ('DV-HI-05','asech(x)',[.1,.5,.9],lambda x: -1/(x*math.sqrt(1-x*x))),
    ('DV-HI-06','acsch(x)',[-2,-1,1,2],lambda x: -1/(abs(x)*math.sqrt(1+x*x))),
    ('DV-HI-07','asinh(2*x)',[-1,0,1],lambda x: 2/math.sqrt(4*x*x+1)),
    ('DV-HI-08','acosh(3*x)',[.4,1,2],lambda x: 3/math.sqrt(9*x*x-1)),
    ('DV-HI-09','atanh(x^2)',[-.8,0,.8],lambda x: 2*x/(1-x**4)),
    ('DV-HI-10','x*asinh(x)-sqrt(x^2+1)',[-2,0,2],lambda x: math.asinh(x)),
]

EXPECTED = [
    r'\cosh x', r'\sinh x', r'\operatorname{sech}^{2}x',
    r'-\operatorname{csch} x\coth x', r'-\operatorname{sech} x\tanh x',
    r'-\operatorname{csch}^{2}x', r'3\cosh(3x)', r'\tanh x',
    r'\sinh x+x\cosh x', r'2\tanh x\operatorname{sech}^{2}x',
    r'e^{2x}', '0', r'\frac{1}{\sqrt{x^{2}+1}}',
    r'\frac{1}{\sqrt{x^{2}-1}}', r'\frac{1}{1-x^{2}}',
    r'\frac{1}{1-x^{2}}', r'-\frac{1}{x\sqrt{1-x^{2}}}',
    r'-\frac{1}{\lvert x\rvert\sqrt{1+x^{2}}}', r'\frac{2}{\sqrt{4x^{2}+1}}',
    r'\frac{3}{\sqrt{9x^{2}-1}}', r'\frac{2x}{1-x^{4}}', r'\operatorname{arsinh} x',
]
EXPECTED_BY_ID = dict(zip((case[0] for case in CASES), EXPECTED, strict=True))


@pytest.mark.parametrize('case,expression,samples,oracle', CASES, ids=[c[0] for c in CASES])
def test_matrix_and_service(case, expression, samples, oracle):
    import sympy as sp
    row = next(line for line in MATRIX.splitlines() if f'| {case} |' in line)
    assert len(row.split('|')) >= 4
    assert EXPECTED_BY_ID[case] in row.split('|')[3]
    actual = compute_derivative(expression, 'x', 1).result_expr
    for sample in samples:
        value = float(sp.N(actual.subs(sp.Symbol('x'), sample), 15))
        assert value == pytest.approx(oracle(sample), rel=1e-9, abs=1e-9), (case, sample, actual)


@pytest.mark.parametrize('case,expression,samples,oracle', CASES, ids=[c[0] for c in CASES])
def test_http(case, expression, samples, oracle):
    import sympy as sp
    with TestClient(app) as client:
        response = client.post('/api/v1/derivative', json={'expression': expression, 'variable': 'x', 'order': 1})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    actual = sp.sympify(response.json()['result_text'])
    for sample in samples:
        value = float(sp.N(actual.subs(sp.Symbol('x'), sample), 15))
        assert value == pytest.approx(oracle(sample), rel=1e-9, abs=1e-9), (case, sample, actual)
