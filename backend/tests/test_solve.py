"""
Tests reales del Módulo 6 para `POST /api/v1/solve` (spec, secciones 8.5 y
15): variable ambigua, inferida, identity/contradiction, solución compleja,
angle_unit con/sin trig directa, y confirmación de que el servicio usa
`verify_equation_step_equivalence` (no la escalar) para los pasos.
"""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services import solve_service

client = TestClient(app)


def _solve(equation, variable=None, angle_unit="rad", **extra):
    payload = {"equation": equation, "angle_unit": angle_unit, **extra}
    if variable is not None:
        payload["variable"] = variable
    return client.post("/api/v1/solve", json=payload)


def test_ambiguous_variable_without_hint():
    response = _solve("x+y=0")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "AMBIGUOUS_VARIABLE"


def test_variable_inferred_with_warning():
    response = _solve("2*x+4=0")
    body = response.json()
    assert body["success"] is True
    assert body["has_detailed_steps"] is True
    assert any("inferida" in w for w in body["warnings"])
    assert body["result_data"][0]["text"] == "-2"


def test_identity_2_equals_2():
    response = _solve("2=2")
    body = response.json()
    assert body["success"] is True
    assert body["result_type"] == "identity"
    assert body["has_detailed_steps"] is False


def test_contradiction_2_equals_3():
    response = _solve("2=3")
    body = response.json()
    assert body["success"] is True
    assert body["result_type"] == "contradiction"
    assert body["has_detailed_steps"] is False


def test_complex_solution():
    # x**2 + 1 = 0 -> x = i, -i (discriminante negativo)
    response = _solve("x**2+1=0", variable="x")
    body = response.json()
    assert body["success"] is True
    assert body["has_detailed_steps"] is True
    assert len(body["result_data"]) == 2
    assert all(sol["is_complex"] for sol in body["result_data"])


def test_angle_unit_with_direct_trig():
    # sin(x) = 1/2, angle_unit=deg -> se espera una solución de 30 grados
    response = _solve("sin(x)-1/2=0", variable="x", angle_unit="deg")
    body = response.json()
    assert body["success"] is True
    solutions_text = [sol["text"] for sol in body["result_data"]]
    assert any("30" in text for text in solutions_text)


def test_angle_unit_without_direct_trig_not_converted():
    # 2*x-6=0, angle_unit=deg no debería afectar (no hay trig directa de x)
    response_rad = _solve("2*x-6=0", variable="x", angle_unit="rad")
    response_deg = _solve("2*x-6=0", variable="x", angle_unit="deg")
    assert response_rad.json()["result_data"] == response_deg.json()["result_data"]


def test_solve_uses_equation_verification_not_scalar(monkeypatch):
    calls = []

    original = solve_service.verify_equation_step_equivalence

    def _spy(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(solve_service, "verify_equation_step_equivalence", _spy)

    result = solve_service.solve_equation("2*x+4=0", "x")

    assert result.has_detailed_steps is True
    assert len(calls) >= 1
    # Cada llamada capturada debe ser con objetos sympy.Eq (ecuaciones), no
    # con la diferencia escalar de dos expresiones.
    for call_args in calls:
        eq_before, eq_after = call_args[0], call_args[1]
        assert isinstance(eq_before, sympy.Eq)
        assert isinstance(eq_after, sympy.Eq)


def test_solve_parse_error_propagates():
    response = _solve("eval(1)=0")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert body["operation"] == "solve"


# ---------------------------------------------------------------------------
# Matriz trigonométrica — dominio real e intervalo explícito
# ---------------------------------------------------------------------------

def test_real_domain_filters_complex_solutions():
    response = _solve("sin(x)=2", variable="x", domain="real")
    body = response.json()
    assert body["success"] is True
    assert body["result_data"] == []


def test_complex_domain_keeps_historical_complex_solutions():
    response = _solve("x**2+1=0", variable="x", domain="complex")
    body = response.json()
    assert body["success"] is True
    assert len(body["result_data"]) == 2
    assert all(item["is_complex"] for item in body["result_data"])


def test_bounded_real_trig_equation_returns_all_periodic_solutions_in_interval():
    response = _solve(
        "sin(x)=1/2",
        variable="x",
        domain="real",
        domain_lower="0",
        domain_upper="2*pi",
        domain_lower_inclusive=True,
        domain_upper_inclusive=False,
    )
    body = response.json()
    assert body["success"] is True
    solutions = {item["text"] for item in body["result_data"]}
    assert solutions == {"pi/6", "5*pi/6"}


def test_real_arccot_equation_uses_calculator_branch():
    response = _solve("acot(x)=2*pi/3", variable="x", domain="real")
    body = response.json()
    assert body["success"] is True
    solutions = [sympy.sympify(item["text"]) for item in body["result_data"]]
    assert len(solutions) == 1
    assert sympy.simplify(solutions[0] + sympy.sqrt(3) / 3) == 0


def test_real_asin_equals_acos_reduces_before_generic_solver():
    response = _solve("asin(x)=acos(x)", variable="x", domain="real")
    body = response.json()
    assert body["success"] is True
    solutions = [sympy.sympify(item["text"]) for item in body["result_data"]]
    assert len(solutions) == 1
    assert sympy.simplify(solutions[0] - sympy.sqrt(2) / 2) == 0

def test_bounded_quadratic_in_sine_keeps_all_algebraic_and_periodic_branches():
    body = _solve(
        "2*sin(x)^2-sin(x)-1=0", domain="real",
        domain_lower="0", domain_upper="2*pi", domain_upper_inclusive=False,
    ).json()
    assert body["success"] is True
    values = {sympy.sympify(item["text"]) for item in body["result_data"]}
    assert values == {sympy.pi/2, 7*sympy.pi/6, 11*sympy.pi/6}
    x = sympy.Symbol("x")
    residual = 2*sympy.sin(x)**2-sympy.sin(x)-1
    assert all(sympy.simplify(residual.subs(x, value)) == 0 for value in values)


def test_bounded_trig_polynomial_preserves_open_endpoints_and_degrees():
    for angle_unit, expected in (("rad", {"pi/2", "pi"}), ("deg", {"90", "180"})):
        body = _solve(
            "sin(x)^2-sin(x)=0", domain="real", angle_unit=angle_unit,
            domain_lower="0", domain_upper="2*pi",
            domain_lower_inclusive=False, domain_upper_inclusive=False,
        ).json()
        assert body["success"] is True
        assert {item["text"] for item in body["result_data"]} == expected
