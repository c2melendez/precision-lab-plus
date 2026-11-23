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
        'case': 'DV-I-04',
        'expression': 'acot(x)',
        'matrix_latex': r'-\frac{1}{1+x^{2}}',
        'oracle': -1 / (1 + x**2),
        'function': lambda t: mpmath.pi / 2 - mpmath.atan(t),
        'samples': ['-3', '-0.5', '0', '0.5', '3'],
        'outside_domain': [],
    },
    {
        'case': 'DV-I-05',
        'expression': 'asec(x)',
        'matrix_latex': r'\frac{1}{\lvert x\rvert\sqrt{x^{2}-1}}',
        'oracle': 1 / (sp.Abs(x) * sp.sqrt(x**2 - 1)),
        'function': mpmath.asec,
        'samples': ['-3', '-2', '2', '3'],
        'outside_domain': ['-0.5', '0.5'],
    },
    {
        'case': 'DV-I-06',
        'expression': 'acsc(x)',
        'matrix_latex': r'-\frac{1}{\lvert x\rvert\sqrt{x^{2}-1}}',
        'oracle': -1 / (sp.Abs(x) * sp.sqrt(x**2 - 1)),
        'function': mpmath.acsc,
        'samples': ['-3', '-2', '2', '3'],
        'outside_domain': ['-0.5', '0.5'],
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
    """The high-precision helper below must reproduce known closed forms."""
    assert numeric_derivative(mpmath.atan, '0.5') == pytest.approx(0.8, rel=1e-18)
    assert numeric_derivative(mpmath.acos, '0.5') == pytest.approx(float(-1 / mpmath.sqrt(1 - 0.25)), rel=1e-18)


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_matrix_row_is_anchored(case):
    assert case['matrix_latex'] in matrix_row(case['case'])


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_engine_derivative_matches_matrix_oracle(case):
    actual = compute_derivative(case['expression'], 'x', 1).result_expr
    for point in case['samples']:
        value = sp.Float(point, 40)
        expected = sp.N(case['oracle'].subs(x, value), 40)
        produced = sp.N(actual.subs(x, value), 40)
        assert abs(complex(produced) - complex(expected)) < 1e-30


@pytest.mark.parametrize('case', CASES, ids=[item['case'] for item in CASES])
def test_engine_derivative_matches_numerical_differentiation(case):
    """Independent oracle: high-precision numerical derivative of the real function."""
    actual = compute_derivative(case['expression'], 'x', 1).result_expr
    for point in case['samples']:
        numerical = numeric_derivative(case['function'], point)
        produced = complex(sp.N(actual.subs(x, sp.Float(point, 40)), 40))
        assert numerical.imag == 0
        assert produced.imag == 0
        assert float(produced.real) == pytest.approx(float(numerical.real), rel=1e-18)


def test_metamorphic_inverse_derivatives():
    acot = compute_derivative('acot(x)', 'x', 1).result_expr
    atan = compute_derivative('atan(x)', 'x', 1).result_expr
    asec = compute_derivative('asec(x)', 'x', 1).result_expr
    acsc = compute_derivative('acsc(x)', 'x', 1).result_expr
    assert sp.simplify(acot + atan) == 0
    assert sp.simplify(asec + acsc) == 0


@pytest.mark.parametrize('case', [c for c in CASES if c['outside_domain']], ids=['DV-I-05', 'DV-I-06'])
def test_real_domain_excludes_open_interval(case):
    actual = compute_derivative(case['expression'], 'x', 1).result_expr
    for point in case['outside_domain']:
        value = sp.N(actual.subs(x, sp.Float(point, 30)), 30)
        assert value.is_real is False
        assert sp.im(value) != 0


def test_arccot_remains_real_outside_the_arcsec_domain():
    actual = compute_derivative('acot(x)', 'x', 1).result_expr
    value = sp.N(actual.subs(x, sp.Float('0.5', 30)), 30)
    assert value.is_real is True
    assert complex(value) == pytest.approx(-0.8, rel=0, abs=1e-29)


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
        assert abs(complex(produced) - complex(expected)) < 1e-30
