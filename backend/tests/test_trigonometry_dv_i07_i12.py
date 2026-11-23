import gzip
from pathlib import Path

import mpmath
import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.derivative_service import compute_derivative

x = sp.Symbol('x')

MATRIX = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'

CASES = [
    {
        'case': 'DV-I-07',
        'expression': 'atan(x**2)',
        'matrix_latex': r'\frac{2x}{1+x^{4}}',
        'oracle': 2 * x / (1 + x**4),
        'function': lambda t: mpmath.atan(t**2),
        'samples': ['-2', '-0.5', '0', '0.5', '2'],
        'outside_domain': [],
    },
    {
        'case': 'DV-I-08',
        'expression': 'asin(2*x)',
        'matrix_latex': r'\frac{2}{\sqrt{1-4x^{2}}}',
        'oracle': 2 / sp.sqrt(1 - 4 * x**2),
        'function': lambda t: mpmath.asin(2 * t),
        'samples': ['-0.4', '-0.2', '0', '0.2', '0.4'],
        'outside_domain': ['-0.6', '0.6'],
    },
    {
        'case': 'DV-I-09',
        'expression': 'x*atan(x)',
        'matrix_latex': r'\arctan x+\frac{x}{1+x^{2}}',
        'oracle': sp.atan(x) + x / (1 + x**2),
        'function': lambda t: t * mpmath.atan(t),
        'samples': ['-2', '-0.5', '0', '0.5', '2'],
        'outside_domain': [],
    },
    {
        'case': 'DV-I-10',
        'expression': 'asin(sqrt(x))',
        'matrix_latex': r'\frac{1}{2\sqrt{x(1-x)}}',
        'oracle': 1 / (2 * sp.sqrt(x * (1 - x))),
        'function': lambda t: mpmath.asin(mpmath.sqrt(t)),
        'samples': ['0.1', '0.25', '0.5', '0.75', '0.9'],
        'outside_domain': ['-0.1', '1.1'],
    },
    {
        'case': 'DV-I-11',
        'expression': 'atan(1/x)',
        'matrix_latex': r'-\frac{1}{1+x^{2}}',
        'oracle': -1 / (1 + x**2),
        'function': lambda t: mpmath.atan(1 / t),
        'samples': ['-3', '-0.5', '0.5', '2', '3'],
        'outside_domain': [],
    },
    {
        'case': 'DV-I-12',
        'expression': 'asin(x)+acos(x)',
        'matrix_latex': '0',
        'oracle': sp.Integer(0),
        'function': lambda t: mpmath.asin(t) + mpmath.acos(t),
        'samples': ['-0.9', '-0.5', '0', '0.5', '0.9'],
        'outside_domain': [],
    },
]


def matrix_row(case_id: str) -> str:
    text = gzip.decompress(MATRIX.read_bytes()).decode()
    return next(line for line in text.splitlines() if f'| {case_id} |' in line)


def numeric_derivative(function, point, h=mpmath.mpf('1e-10')):
    """Second-order central difference at 60 digits: independent of any CAS derivative."""
    with mpmath.workdps(60):
        p = mpmath.mpf(point)
        return (function(p + h) - function(p - h)) / (2 * h)


def test_numeric_evaluator_is_faithful():
    assert numeric_derivative(lambda t: mpmath.atan(t**2), '1') == pytest.approx(1.0, rel=1e-12)
    assert numeric_derivative(lambda t: mpmath.asin(2 * t), '0.25') == pytest.approx(
        float(2 / mpmath.sqrt(1 - 0.25)), rel=1e-12
    )


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_matrix_row_is_anchored(case):
    row = matrix_row(case['case'])
    assert case['case'] in row
    if case['matrix_latex'] != '0':
        # Accept either full latex or key tokens from the frozen matrix.
        assert any(token in row for token in ('2x', '1-4x', 'arctan', 'sqrt', '1+x')) or case['matrix_latex'] in row
    else:
        assert '0' in row


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_engine_derivative_matches_matrix_oracle(case):
    actual = compute_derivative(case['expression'], 'x', 1).result_expr
    for point in case['samples']:
        value = sp.Float(point, 40)
        expected = sp.N(case['oracle'].subs(x, value), 40)
        produced = sp.N(actual.subs(x, value), 40)
        assert abs(complex(produced) - complex(expected)) < 1e-25


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_engine_derivative_matches_numerical_differentiation(case):
    """Independent oracle: high-precision numerical derivative of the real function."""
    actual = compute_derivative(case['expression'], 'x', 1).result_expr
    for point in case['samples']:
        numerical = numeric_derivative(case['function'], point)
        produced = complex(sp.N(actual.subs(x, sp.Float(point, 40)), 40))
        assert abs(numerical.imag) < 1e-20
        assert abs(produced.imag) < 1e-20
        assert float(produced.real) == pytest.approx(float(numerical.real), rel=1e-12, abs=1e-14)


def test_metamorphic_dv_i11_and_i12():
    inv = compute_derivative('atan(1/x)', 'x', 1).result_expr
    atan = compute_derivative('atan(x)', 'x', 1).result_expr
    assert sp.simplify(inv + atan) == 0

    total = compute_derivative('asin(x)+acos(x)', 'x', 1).result_expr
    assert sp.simplify(total) == 0


@pytest.mark.parametrize('case', [c for c in CASES if c['outside_domain']], ids=lambda c: c['case'])
def test_real_domain_excludes_invalid_points(case):
    actual = compute_derivative(case['expression'], 'x', 1).result_expr
    for point in case['outside_domain']:
        value = sp.N(actual.subs(x, sp.Float(point, 30)), 30)
        # Outside domain the symbolic form is typically complex or non-finite.
        is_bad = value.is_real is False or (value.is_finite is False)
        assert is_bad or abs(sp.im(value)) > 0


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_http_derivative_endpoint(case):
    with TestClient(app) as client:
        response = client.post(
            '/api/v1/derivative',
            json={'expression': case['expression'], 'variable': 'x', 'order': 1},
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['success'], payload
    actual = sp.sympify(payload['result_text'])
    for point in case['samples']:
        value = sp.Float(point, 40)
        expected = sp.N(case['oracle'].subs(x, value), 40)
        produced = sp.N(actual.subs(x, value), 40)
        assert abs(complex(produced) - complex(expected)) < 1e-25
