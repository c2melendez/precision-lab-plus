"""Syntax309 SY-F initial numeric witnesses through Plus HTTP.

Official LaTeX is translated explicitly into backend notation. This validates
backend evaluation only, not MathLive or UI interpretation.
"""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}
WITNESSES = [("SY-F-09", "sin(pi/6)", 0.5), ("SY-F-06", "(sin(pi/6))^(-1)", 2.0)]

def test_syf_source_and_scope():
    assert sum(r["seccion"] == "F" for r in ROWS.values()) == 48
    for case_id, _, _ in WITNESSES:
        assert ROWS[case_id]["operacion"] == "valor"

@pytest.mark.parametrize("case_id,expression,expected", WITNESSES)
def test_syf_numeric_witness_via_http(case_id, expression, expected):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


def test_syf03_sine_argument_power_not_function_power():
    """SY-F-03: numeric substitution distinguishes sin(x^2) from sin(x)^2."""
    import math
    assert ROWS["SY-F-03"]["operacion"] == "interpretacion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "sin(x^2)", "substitutions": {"x": "2"}
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(math.sin(4), rel=1e-9, abs=1e-12)
    assert data["result_approx"] != pytest.approx(math.sin(2) ** 2, abs=1e-4)


@pytest.mark.parametrize("case_id,expression,expected", [
    ("SY-F-04", "(sin(pi/6))^2", 0.25),
    ("SY-F-05", "asin(1/2)", 0.5235987755982988),
])
def test_syf04_05_function_power_and_inverse_via_http(case_id, expression, expected):
    """Explicit backend syntax witnesses; NOT an assertion about MathLive parsing."""
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


def test_syf07_inverse_tangent_numeric_via_http():
    """Explicit backend syntax witness, separate from MathLive interpretation."""
    import math
    assert ROWS["SY-F-07"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "atan(1)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(math.pi / 4, rel=1e-9, abs=1e-12)
    assert data["result_approx"] != pytest.approx(1 / math.tan(1), abs=1e-4)


@pytest.mark.parametrize("case_id,expression,value,expected,different", [
    ("SY-F-01", "sin(x)+1", "2", 1 + __import__("math").sin(2), __import__("math").sin(3)),
    ("SY-F-02", "sin(x)*cos(x)", "1", __import__("math").sin(1)*__import__("math").cos(1), __import__("math").sin(__import__("math").cos(1))),
    ("SY-F-08", "sin(2*x)", "1", __import__("math").sin(2), 2*__import__("math").sin(1)),
])
def test_syf01_02_08_explicit_scope_backend_witness(case_id, expression, value, expected, different):
    """Backend-only control: original LaTeX grouping must be checked by frontend/parser tests."""
    assert ROWS[case_id]["operacion"] in ("interpretacion", "convencion")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression, "substitutions": {"x": value}
        })
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, abs=1e-9, rel=1e-9)
    assert data["result_approx"] != pytest.approx(different, abs=1e-4)

 
@pytest.mark.parametrize("case_id,expression", [
    ("SY-F-10", "sin(pi/6)"),
    ("SY-F-11", "sin(30*pi/180)"),
])
def test_syf10_11_explicit_degree_translation_http(case_id, expression):
    """Backend translation witness only; original degree glyph needs a UI/parser gate."""
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(0.5, abs=1e-10)


@pytest.mark.parametrize("value", ["0", "0.7", "2"])
def test_syf12_pythagorean_identity_http(value):
    """At independent input values, cosine squared plus sine squared must equal one."""
    assert ROWS["SY-F-12"]["operacion"] == "equivalente"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "cos(x)^2+sin(x)^2",
            "substitutions": {"x": value},
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("case_id,expression,expected,incorrect", [
    ("SY-F-13", "ln(x^2)", __import__("math").log(4), __import__("math").log(2)**2),
    ("SY-F-14", "(ln(x))^2", __import__("math").log(2)**2, __import__("math").log(4)),
])
def test_syf13_14_log_power_grouping_http(case_id, expression, expected, incorrect):
    """Backend semantic witnesses only; original LaTeX grouping is a frontend concern."""
    assert ROWS[case_id]["operacion"] == ("interpretacion" if case_id == "SY-F-13" else "convencion")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression, "substitutions": {"x": "2"},
        })
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, abs=1e-9, rel=1e-9)
    assert data["result_approx"] != pytest.approx(incorrect, abs=1e-4)


@pytest.mark.parametrize("case_id,expression,expected", [
    ("SY-F-15", "log(100)", 2.0),
    ("SY-F-16", "log(8,2)", 3.0),
    ("SY-F-17", "log(1000,10)", 3.0),
])
def test_syf15_17_logarithm_base_contract_http(case_id, expression, expected):
    """Explicit HTTP syntax tests: common log defaults to ten, bases remain explicit."""
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, abs=1e-10)


@pytest.mark.parametrize("case_id,expression,substitutions,expected", [
    ("SY-F-18", "log(x,2)+1", {"x": "8"}, 4.0),
    ("SY-F-19", "log(b,a)", {"a": "2", "b": "8"}, 3.0),
    ("SY-F-20", "ln(e)", {}, 1.0),
])
def test_syf18_20_log_precedence_base_change_and_natural_e_http(case_id, expression, substitutions, expected):
    """Backend syntax controls; source LaTeX still requires a separate frontend parser gate."""
    assert ROWS[case_id]["operacion"] in ("interpretacion", "equivalente", "valor")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression, "substitutions": substitutions,
        })
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-10)
    if case_id == "SY-F-18":
        import math
        assert data["result_approx"] != pytest.approx(math.log2(9), abs=1e-4)


@pytest.mark.parametrize("case_id,expression", [
    ("SY-F-21", "asinh(1)"),
    ("SY-F-22", "asinh(1)"),
])
def test_syf21_22_inverse_hyperbolic_sine_http(case_id, expression):
    """Backend numerical witness; source MathLive notation requires separate E2E."""
    import math
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(math.asinh(1), abs=1e-9)


@pytest.mark.parametrize("x", ["0", "1", "2"])
def test_syf23_hyperbolic_identity_http(x):
    import math
    assert ROWS["SY-F-23"]["operacion"] == "equivalente"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "cosh(x)^2-sinh(x)^2",
            "substitutions": {"x": x},
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("case_id,expression,expected", [
    ("SY-F-24", "sech(0)", 1.0),
    ("SY-F-25", "exp(2)", __import__("math").exp(2)),
    ("SY-F-26", "exp(ln(3))", 3.0),
])
def test_syf24_26_hyperbolic_and_exponential_http(case_id, expression, expected):
    """Explicit backend syntax witness, independent of original MathLive LaTeX."""
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, abs=1e-9, rel=1e-9)


@pytest.mark.parametrize("x", ["0.4", "1.2"])
def test_syf27_adjacent_sine_product_http(x):
    import math
    assert ROWS["SY-F-27"]["operacion"] == "equivalente"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "sin(x)*sin(x)", "substitutions": {"x": x}})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(math.sin(float(x)) ** 2, abs=1e-9)
    assert data["result_approx"] != pytest.approx(math.sin(float(x)**2), abs=1e-4)

def test_syf28_nested_trigonometric_http():
    import math
    assert ROWS["SY-F-28"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "sin(cos(tan(0)))"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(math.sin(1), abs=1e-9)


def test_syf29_arcsin_outside_real_domain_http():
    """SY-F-29: a real-domain error or an explicitly declared complex result.

    A 200 response containing a silent real scalar/NaN is not acceptable.
    This is a backend-only witness, not certification of source \\arcsin2 LaTeX.
    """
    assert ROWS["SY-F-29"]["operacion"] == "error"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "asin(2)"})
    assert response.status_code < 500, response.text
    data = response.json()
    if data.get("success") is False:
        assert data.get("error_code") == "DOMAIN_ERROR", data
        assert isinstance(data.get("error_message"), str) and data["error_message"].strip(), data
    else:
        # Complex output must be unambiguously marked; a real scalar isn't a
        # valid value for arcsin(2) on the real domain.
        import math
        approx = data.get("result_approx")
        assert approx is None or not (isinstance(approx, (int, float)) and math.isfinite(approx)), data
        assert "i" in str(data.get("result_text", "")) or "I" in str(data.get("result_text", "")) or "complex" in str(data.get("result_type", "")).lower(), data


@pytest.mark.parametrize("x,y", [("9", "2"), ("16", "3")])
def test_syf30_root_scope_multiplies_outside_radical_http(x, y):
    """Explicit backend scope witness; original source LaTeX is checked in Lite."""
    import math
    assert ROWS["SY-F-30"]["operacion"] == "interpretacion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "sqrt(x)*y", "substitutions": {"x": x, "y": y}
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(math.sqrt(float(x)) * float(y), abs=1e-9)
    assert data["result_approx"] != pytest.approx(math.sqrt(float(x) * float(y)), abs=1e-4)


def test_syf31_sqrt_three_http():
    """SY-F-31 backend meaning; no claim about frontend unbraced-LaTeX parsing."""
    import math
    assert ROWS["SY-F-31"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "sqrt(3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(math.sqrt(3), abs=1e-9)


@pytest.mark.parametrize("case_id,expression,expected", [
    ("SY-F-32", "root(8,3)", 2.0),
    ("SY-F-33", "cbrt(-8)", -2.0),
    ("SY-F-34", "root(16,4)", 2.0),
])
def test_syf32_34_indexed_roots_http(case_id, expression, expected):
    """Explicit HTTP backend notation only, not MathLive source-LaTeX parsing."""
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (case_id, response.text)
    data = response.json()
    assert data["success"] is True, (case_id, data)
    assert data["result_approx"] == pytest.approx(expected, abs=1e-9)


def test_syf35_nested_square_roots_http():
    """SY-F-35 backend numerical witness; no claim for source MathLive LaTeX."""
    assert ROWS["SY-F-35"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "sqrt(sqrt(16))"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(2.0, abs=1e-9)


def test_syf33_generic_root_keeps_declared_complex_principal_branch():
    """Explicit root(-8,3) is the existing complex-principal operator.

    Original indexed-radical input needs an independent frontend routing gate
    for the real-odd-index contract; do not silently conflate the operators.
    """
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "root(-8,3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data.get("result_approx") is None, data
    import sympy
    complex_value = complex(sympy.N(sympy.sympify(data["result_text"])))
    assert abs(complex_value.imag) > 1e-9, data


@pytest.mark.parametrize("expression,expected", [
    ("sqrt((-3)^2)", 3.0),
    ("sqrt((3)^2)", 3.0),
    ("cbrt((-3)^3)", -3.0),
    ("cbrt((3)^3)", 3.0),
    ("root((-2)^4,4)", 2.0),
])
def test_syf36_real_indexed_root_parity_explicit_backend(expression, expected):
    """Real even/odd root parity on concrete witnesses; source LaTeX unverified."""
    assert ROWS["SY-F-36"]["operacion"] == "equivalente"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, (expression, response.text)
    data = response.json()
    assert data["success"] is True, (expression, data)
    assert data["result_approx"] == pytest.approx(expected, abs=1e-9)


def test_syf37_absolute_value_http():
    """Explicit backend abs(-3) witness; original LaTeX source not covered."""
    assert ROWS["SY-F-37"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "abs(-3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(3.0, abs=1e-9)


@pytest.mark.parametrize("case_id", ["SY-F-38", "SY-F-39"])
def test_syf38_39_abs_translated_backend_http(case_id):
    """Explicit backend abs syntax only; MathLive LaTeX and typed bars unverified."""
    assert ROWS[case_id]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "abs(-3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(3.0, abs=1e-9)


@pytest.mark.parametrize("x,expected", [("-3", 1.0), ("0", 2.0), ("5", 3.0)])
def test_syf40_explicit_nested_absolute_backend(x, expected):
    """Only explicit abs(abs(x)-2) backend meaning; typed bars remain a UI gate."""
    assert ROWS["SY-F-40"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "abs(abs(x)-2)", "substitutions": {"x": x},
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(expected, abs=1e-9)


def test_syf41_floor_backend_http():
    """SY-F-41 floor(3.7)=3 via explicit backend notation; raw MathLive LaTeX is not covered."""
    assert ROWS["SY-F-41"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "floor(3.7)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(3.0, abs=1e-9)


def test_syf42_ceiling_backend_http():
    """SY-F-42: ceil(3.2)=4 via backend; original MathLive LaTeX not covered."""
    assert ROWS["SY-F-42"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "ceil(3.2)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(4.0, abs=1e-9)


def test_syf43_sign_of_negative_five_backend_http():
    """Explicit sign(-5) backend contract; does not cover original MathLive LaTeX."""
    assert ROWS["SY-F-43"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "sign(-5)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(-1.0, abs=1e-9)


def test_syf44_modulo_backend_http():
    """SY-F-44: explicit mod(10,3) backend witness; original LaTeX remains unverified."""
    assert ROWS["SY-F-44"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "mod(10,3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1.0, abs=1e-9)


def test_syf45_gcd_backend_http():
    """SY-F-45 gcd(12,18)=6 via explicit backend call; original LaTeX not covered."""
    assert ROWS["SY-F-45"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "gcd(12,18)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(6.0, abs=1e-9)


def test_syf46_lcm_backend_http():
    """SY-F-46: explicit backend lcm(4,6)=12; original MathLive source not covered."""
    assert ROWS["SY-F-46"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "lcm(4,6)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(12.0, abs=1e-9)


def test_syf47_maximum_backend_http():
    """SY-F-47 max(1,5,3)=5 in backend; not a raw MathLive LaTeX UI test."""
    assert ROWS["SY-F-47"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "max(1,5,3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(5.0, abs=1e-9)


def test_syf48_minimum_backend_http():
    """SY-F-48 min(1,5,3)=1 in backend; raw source MathLive UI unverified."""
    assert ROWS["SY-F-48"]["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "min(1,5,3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1.0, abs=1e-9)
