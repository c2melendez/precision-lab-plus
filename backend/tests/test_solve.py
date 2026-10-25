"""
Tests reales del Módulo 6 para `POST /api/v1/solve` (spec, secciones 8.5 y
15): variable ambigua, inferida, identity/contradiction, solución compleja,
angle_unit con/sin trig directa, y confirmación de que el servicio usa
`verify_equation_step_equivalence` (no la escalar) para los pasos.
"""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services import solve_service

client = TestClient(app)


def _solve(equation, variable=None, angle_unit="rad"):
    payload = {"equation": equation, "angle_unit": angle_unit}
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

# S19 targeted coverage r292
def test_absolute_value_steps_returns_both_real_branches():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Integer(2), evaluate=False)
    result = solve_service._absolute_value_steps(equation, x)
    assert result is not None
    steps, solutions = result
    assert set(solutions) == {sympy.Integer(-1), sympy.Integer(3)}
    assert steps[0].rule == "AbsoluteValueDomain"


def test_absolute_value_equidistance_returns_midpoint_for_distinct_centers():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Abs(x - 5), evaluate=False)
    result = solve_service._absolute_value_equidistance_steps(equation, x)
    assert result is not None
    steps, solutions = result
    assert solutions == [sympy.Integer(3)]
    assert steps[0].rule == "AbsoluteValueEquidistance"


def test_absolute_value_case_solver_keeps_only_roots_in_their_regions():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(x - 2), sympy.Integer(5), evaluate=False
    )
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert {sympy.sympify(solution.text) for solution in result.solutions} == {
        sympy.Rational(-3, 2), sympy.Rational(7, 2)
    }
    assert "pertenece al tramo" in result.steps[0].description


def test_absolute_value_case_solver_reports_empty_real_solution_set():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(x - 2), sympy.Integer(1), evaluate=False
    )
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.CONTRADICTION
    assert result.solutions == []


def test_real_radical_value_preserves_odd_real_roots_and_rejects_even_negative():
    assert solve_service._real_radical_value(sympy.Integer(-8), 3) == sympy.Integer(-2)
    assert solve_service._real_radical_value(sympy.Integer(-4), 2) is None


def test_radical_case_solver_rejects_candidate_that_fails_original_equation():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "sqrt(x)=x-2", allow_equation=True
    )
    result = solve_service._radical_cases_result(equation, x, [])
    assert result is not None
    assert {sympy.sympify(solution.text) for solution in result.solutions} == {
        sympy.Integer(4)
    }
    assert any("se descarta" in step.description for step in result.steps)


def test_rational_domain_identity_preserves_original_denominator_exclusion():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree("x/x=1", allow_equation=True)
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(0)], [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.IDENTITY
    assert result.steps[0].rule == "DomainRestriction"
    assert "x≠0" in result.steps[0].description


def test_rational_domain_solver_discards_root_excluded_by_original_denominator():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "((x-1)**2)/(x-1)=0", allow_equation=True
    )
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(1)], [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.CONTRADICTION
    assert result.solutions == []
    assert "no pertenece al dominio" in result.steps[0].description


# S19 targeted coverage r298 - scaled breakpoints, region text and step contracts
def test_absolute_value_case_solver_handles_non_unit_slope_breakpoint():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "abs(2*x-4)=2", allow_equation=True
    )
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert {sympy.sympify(solution.text) for solution in result.solutions} == {
        sympy.Integer(1),
        sympy.Integer(3),
    }


def test_absolute_value_case_solver_names_each_region_in_steps():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Integer(2), evaluate=False)
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    description = result.steps[0].description
    assert "x < 1" in description
    assert "x \u2265 1" in description


def test_absolute_value_steps_zero_radius_returns_the_center_once():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Integer(0), evaluate=False)
    result = solve_service._absolute_value_steps(equation, x)
    assert result is not None
    steps, solutions = result
    assert solutions == [sympy.Integer(1)]
    assert len(steps) == 1
    assert steps[0].index == 0
    assert steps[0].title == "Dominio del valor absoluto"


def test_absolute_value_steps_negative_radius_reports_empty_domain_step():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Integer(-2), evaluate=False)
    result = solve_service._absolute_value_steps(equation, x)
    assert result is not None
    steps, solutions = result
    assert solutions == []
    step = steps[0]
    assert step.index == 0
    assert step.title == "Dominio del valor absoluto"
    assert step.description == (
        "El valor absoluto siempre es no negativo; como b < 0, "
        "no existe solución real."
    )
    assert step.latex_after == r"\varnothing"


def test_absolute_value_steps_rejects_radius_that_contains_the_variable():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x), x, evaluate=False)
    assert solve_service._absolute_value_steps(equation, x) is None


def test_absolute_value_equidistance_rejects_one_sided_absolute_value():
    x = sympy.Symbol("x")
    equation = sympy.Eq(x, sympy.Abs(x - 1), evaluate=False)
    assert solve_service._absolute_value_equidistance_steps(equation, x) is None


def test_absolute_value_equidistance_rejects_constant_right_argument():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x), sympy.Abs(3), evaluate=False)
    assert solve_service._absolute_value_equidistance_steps(equation, x) is None


def test_absolute_value_equidistance_reports_identity_when_centers_match():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(1 - x), sympy.Abs(x - 1), evaluate=False)
    result = solve_service._absolute_value_equidistance_steps(equation, x)
    assert result is not None
    steps, solutions = result
    assert solutions == [sympy.Integer(1)]
    assert steps[0].description == (
        "Como a = b, ambos valores absolutos son idénticos; "
        "toda x real es solución."
    )


def test_radical_case_solver_accepts_a_fourth_root_candidate():
    x = sympy.Symbol("x")
    equation = sympy.Eq(x ** sympy.Rational(1, 4), sympy.Integer(2), evaluate=False)
    result = solve_service._radical_cases_result(equation, x, [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert {sympy.sympify(solution.text) for solution in result.solutions} == {
        sympy.Integer(16)
    }


def test_radical_case_solver_rejects_non_unit_numerator_exponent():
    x = sympy.Symbol("x")
    equation = sympy.Eq(x ** sympy.Rational(3, 2), sympy.Integer(8), evaluate=False)
    assert solve_service._radical_cases_result(equation, x, []) is None


def test_domain_step_keeps_index_title_and_every_exclusion():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "1/x+1/(x-1)=0", allow_equation=True
    )
    step = solve_service._domain_step(
        equation, x, [sympy.Integer(0), sympy.Integer(1)], "descripción de prueba"
    )
    assert step.index == 0
    assert step.title == "Dominio de la ecuación"
    assert step.description == (
        "Restricción de dominio original: x\u22600, x\u22601. descripción de prueba"
    )
    assert step.latex_before == sympy.latex(equation)
    assert step.latex_after == r"x \neq 0, x \neq 1"


def test_rational_domain_identity_preserves_equation_and_step_contract():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree("x/x=1", allow_equation=True)
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(0)], [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.IDENTITY
    assert result.input_eq == equation
    assert result.variable == x
    assert result.solutions == []
    assert result.has_detailed_steps is True
    assert result.warnings == []
    assert result.steps[0].description.startswith(
        "Restricción de dominio original: x\u22600. "
        "La ecuación se cumple para toda x del dominio"
    )


def test_rational_domain_contradiction_reports_constant_numerator():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree("1/x=0", allow_equation=True)
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(0)], [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.CONTRADICTION
    assert result.input_eq == equation
    assert result.variable == x
    assert result.solutions == []
    assert result.has_detailed_steps is True
    assert result.warnings == []
    assert "constante no nula 1" in result.steps[0].description


def test_rational_domain_keeps_valid_root_when_numerator_has_variable():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "((x-1)**2*(x-2))/(x-1)=0", allow_equation=True
    )
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(1)], [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert [solution.text for solution in result.solutions] == ["2"]


# S19 targeted coverage r299 - remaining branches of the certified real-domain helpers
def test_absolute_value_steps_symbolic_radius_reports_conditional_branches():
    x = sympy.Symbol("x")
    b = sympy.Symbol("b")
    equation = sympy.Eq(sympy.Abs(x - 1), b, evaluate=False)
    steps, solutions = solve_service._absolute_value_steps(equation, x)
    assert solutions == [b + 1, 1 - b]
    assert steps[0].description == (
        "Para |x-a| = b: si b < 0 no hay solución; si b = 0, x = a; "
        "si b > 0, x = a ± b. Las dos expresiones son condicionales a b > 0."
    )


def test_absolute_value_steps_accepts_absolute_value_on_the_right():
    x = sympy.Symbol("x")
    equation = sympy.Eq(3, sympy.Abs(x - 1), evaluate=False)
    steps, solutions = solve_service._absolute_value_steps(equation, x)
    assert set(solutions) == {sympy.Integer(-2), sympy.Integer(4)}
    assert steps[0].description == (
        "Si b > 0, las dos ramas x = a + b y x = a - b dan las dos raíces reales."
    )


def test_absolute_value_steps_rejects_non_unit_slope():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(2 * x - 1), 3, evaluate=False)
    assert solve_service._absolute_value_steps(equation, x) is None


def test_absolute_value_steps_rejects_argument_without_variable():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - x + 3), 3, evaluate=False)
    assert solve_service._absolute_value_steps(equation, x) is None


def test_absolute_value_steps_negative_radius_preserves_step_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), -2, evaluate=False)
    steps, solutions = solve_service._absolute_value_steps(equation, x)
    assert solutions == []
    assert steps[0].rule == "AbsoluteValueDomain"
    assert steps[0].latex_before == sympy.latex(equation)


def test_absolute_value_equidistance_reports_distinct_centers_description():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Abs(x - 5), evaluate=False)
    steps, solutions = solve_service._absolute_value_equidistance_steps(equation, x)
    assert solutions == [sympy.Integer(3)]
    assert steps[0].description == (
        "Como a ≠ b, la única solución real es el punto medio x = (a+b)/2."
    )
    assert steps[0].latex_after == sympy.latex(sympy.Eq(x, sympy.Integer(3)))


def test_absolute_value_equidistance_reports_symbolic_conditional_description():
    x = sympy.Symbol("x")
    a = sympy.Symbol("a")
    b = sympy.Symbol("b")
    equation = sympy.Eq(sympy.Abs(x - a), sympy.Abs(x - b), evaluate=False)
    steps, solutions = solve_service._absolute_value_equidistance_steps(equation, x)
    assert solutions == [(a + b) / 2]
    assert steps[0].description == (
        "Si a ≠ b, la única solución real es x = (a+b)/2; "
        "si a = b, toda x real es solución. La raíz mostrada es condicional a a ≠ b."
    )


def test_absolute_value_equidistance_supports_negative_unit_slope():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(1 - x), sympy.Abs(x - 3), evaluate=False)
    steps, solutions = solve_service._absolute_value_equidistance_steps(equation, x)
    assert solutions == [sympy.Integer(2)]
    assert steps[0].title == "Equidistancia en la recta real"


def test_absolute_value_equidistance_rejects_non_unit_slopes():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(2 * x), sympy.Abs(x - 1), evaluate=False)
    assert solve_service._absolute_value_equidistance_steps(equation, x) is None


def test_absolute_value_equidistance_rejects_non_linear_argument():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x ** 2), sympy.Abs(x - 1), evaluate=False)
    assert solve_service._absolute_value_equidistance_steps(equation, x) is None


def test_absolute_value_case_solver_assigns_roots_across_three_breakpoints():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(x - 2) + sympy.Abs(x - 4), 6, evaluate=False
    )
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert [solution.text for solution in result.solutions] == ["0", "4"]
    description = result.steps[0].description
    assert "En 0 ≤ x < 2: x = 0, pertenece al tramo y se acepta." in description
    assert "En 2 ≤ x < 4: x = 4 no pertenece al tramo" in description
    assert "En x ≥ 4: x = 4, pertenece al tramo y se acepta." in description
    assert result.steps[0].title == "Análisis por casos del valor absoluto"
    assert result.steps[0].rule == "AbsoluteValueCases"
    assert result.has_detailed_steps is True


def test_absolute_value_case_solver_contradiction_preserves_step_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(x - 2), 1, evaluate=False
    )
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    assert result.steps[0].latex_after == r"\varnothing"
    assert result.steps[0].rule == "AbsoluteValueCases"
    assert "se descarta (raíz extraña)" in result.steps[0].description
    assert result.has_detailed_steps is True
    assert result.warnings == []


def test_absolute_value_case_solver_rejects_constant_absolute_node():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(sympy.Integer(2), evaluate=False), 3, evaluate=False
    )
    assert solve_service._absolute_value_cases_result(equation, x, []) is None


def test_absolute_value_case_solver_rejects_non_polynomial_argument():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(1 / x, evaluate=False), 2, evaluate=False
    )
    assert solve_service._absolute_value_cases_result(equation, x, []) is None


def test_absolute_value_case_solver_rejects_missing_or_foreign_symbols():
    x = sympy.Symbol("x")
    y = sympy.Symbol("y")
    assert solve_service._absolute_value_cases_result(
        sympy.Eq(x, 1, evaluate=False), x, []
    ) is None
    assert solve_service._absolute_value_cases_result(
        sympy.Eq(sympy.Abs(x) + y, 1, evaluate=False), x, []
    ) is None


def test_radical_case_solver_reports_no_real_candidates():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.sqrt(x ** 2 + 1), 0, evaluate=False)
    result = solve_service._radical_cases_result(equation, x, [])
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert result.solutions == []
    assert result.steps[0].latex_after == r"\varnothing"
    assert result.steps[0].description == (
        "Al eliminar los radicales no aparece ningún candidato real."
    )


def test_radical_case_solver_rejects_abs_piecewise_and_foreign_symbols():
    x = sympy.Symbol("x")
    y = sympy.Symbol("y")
    assert solve_service._radical_cases_result(
        sympy.Eq(sympy.Abs(x), sympy.sqrt(x), evaluate=False), x, []
    ) is None
    assert solve_service._radical_cases_result(
        sympy.Eq(sympy.sqrt(x) + y, 1, evaluate=False), x, []
    ) is None


def test_radical_case_solver_rejects_non_polynomial_radicand():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.sqrt(1 / x), 2, evaluate=False)
    assert solve_service._radical_cases_result(equation, x, []) is None


def test_radical_case_solver_rejects_more_than_three_radicals():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.sqrt(x)
        + sympy.sqrt(x - 1)
        + sympy.sqrt(x - 2)
        + sympy.sqrt(x - 3),
        1,
        evaluate=False,
    )
    assert solve_service._radical_cases_result(equation, x, []) is None


def test_radical_case_solver_rejects_index_above_four():
    x = sympy.Symbol("x")
    equation = sympy.Eq(x ** sympy.Rational(1, 5), 2, evaluate=False)
    assert solve_service._radical_cases_result(equation, x, []) is None


def test_radical_case_solver_extraneous_step_names_the_reason():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "sqrt(x)=x-2", allow_equation=True
    )
    result = solve_service._radical_cases_result(equation, x, [])
    assert result is not None
    assert result.steps[0].rule == "RadicalCandidates"
    assert result.steps[0].title == "Eliminación de radicales y verificación"
    assert "verifica la ecuación original" in result.steps[0].description
    assert "no satisface la ecuación original; se descarta (raíz extraña)" in (
        result.steps[0].description
    )


def test_rational_domain_rejects_numerator_above_degree_four():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "x**6/x=0", allow_equation=True
    )
    assert solve_service._rational_domain_result(
        equation, x, [sympy.Integer(0)], []
    ) is None


def test_rational_domain_rejects_non_polynomial_numerator():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "(x+sqrt(x))/x=0", allow_equation=True
    )
    assert solve_service._rational_domain_result(
        equation, x, [sympy.Integer(0)], []
    ) is None


def test_rational_domain_requires_original_exclusions():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree("1/x=0", allow_equation=True)
    assert solve_service._rational_domain_result(equation, x, [], []) is None


@pytest.mark.parametrize(
    "text", ["P(1234,1)", "P(1,1234)", "P(-1,0)", "P(171,1)", "P(2,3)"]
)
def test_permutation_alias_reports_exact_range_message(text):
    with pytest.raises(solve_service.parsing.ParseSecurityError) as excinfo:
        solve_service.parsing.permutation_alias_args(text)
    assert str(excinfo.value) == (
        "Permutaciones: se requiere 0 <= r <= n <= 170, con enteros."
    )


def test_permutation_alias_accepts_explicit_positive_signs():
    assert solve_service.parsing.permutation_alias_args("P(+5,+2)") == (5, 2)


def test_inequality_tree_resolves_euler_constant_on_each_side():
    assert solve_service.parsing.parse_inequality_tree("e<x").lhs == sympy.E
    assert solve_service.parsing.parse_inequality_tree("x<e").rhs == sympy.E


# S19 targeted coverage r300 - exact step contract of real-domain helpers
def test_absolute_value_steps_zero_radius_is_a_single_root_step():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), 0, evaluate=False)
    steps, solutions = solve_service._absolute_value_steps(equation, x)
    assert solutions == [sympy.Integer(1)]
    assert steps[0].index == 0
    assert steps[0].latex_before == sympy.latex(equation)
    assert steps[0].latex_after == sympy.latex(sympy.Eq(x, sympy.Integer(1)))
    assert steps[0].description == "Si b = 0, |x-a| solo vale cero en x = a."


def test_absolute_value_steps_positive_radius_orders_and_formats_both_roots():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), 2, evaluate=False)
    steps, solutions = solve_service._absolute_value_steps(equation, x)
    assert solutions == [sympy.Integer(3), sympy.Integer(-1)]
    assert steps[0].index == 0
    assert steps[0].latex_before == sympy.latex(equation)
    assert steps[0].latex_after == r"x = 3,\quad x = -1"


def test_absolute_value_steps_negative_radius_reports_the_exact_reason():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), -2, evaluate=False)
    steps, solutions = solve_service._absolute_value_steps(equation, x)
    assert solutions == []
    assert steps[0].description == (
        "El valor absoluto siempre es no negativo; como b < 0, "
        "no existe solución real."
    )


def test_absolute_value_equidistance_distinct_centers_preserve_step_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x - 1), sympy.Abs(x - 5), evaluate=False)
    steps, solutions = solve_service._absolute_value_equidistance_steps(equation, x)
    assert solutions == [sympy.Integer(3)]
    assert steps[0].index == 0
    assert steps[0].latex_before == sympy.latex(equation)
    assert steps[0].latex_after == sympy.latex(sympy.Eq(x, sympy.Integer(3)))


def test_absolute_value_case_solver_preserves_full_three_region_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(
        sympy.Abs(x) + sympy.Abs(x - 2) + sympy.Abs(x - 4), 6, evaluate=False
    )
    result = solve_service._absolute_value_cases_result(equation, x, ["w"])
    assert result is not None
    assert [solution.text for solution in result.solutions] == ["0", "4"]
    assert result.input_eq == equation
    assert result.variable == x
    assert result.has_detailed_steps is True
    assert result.warnings == ["w"]
    assert result.steps[0].index == 0
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].latex_after == r"x = 0,\quad x = 4"
    assert result.steps[0].description == (
        "En x < 0: x = 0 no pertenece al tramo; se descarta (raíz extraña). "
        "En 0 ≤ x < 2: x = 0, pertenece al tramo y se acepta. "
        "En 2 ≤ x < 4: x = 4 no pertenece al tramo; se descarta (raíz extraña). "
        "En x ≥ 4: x = 4, pertenece al tramo y se acepta."
    )


def test_absolute_value_case_solver_contradiction_preserves_full_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.Abs(x) + sympy.Abs(x - 2), 1, evaluate=False)
    result = solve_service._absolute_value_cases_result(equation, x, [])
    assert result is not None
    assert result.input_eq == equation
    assert result.variable == x
    assert result.has_detailed_steps is True
    assert result.steps[0].index == 0
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].description == (
        "En x < 0: x = 1/2 no pertenece al tramo; se descarta (raíz extraña). "
        "En 0 ≤ x < 2 la ecuación queda 1 = 0: sin solución. "
        "En x ≥ 2: x = 3/2 no pertenece al tramo; se descarta (raíz extraña)."
    )


def test_rational_domain_identity_preserves_full_step_contract():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree("x/x=1", allow_equation=True)
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(0)], [])
    assert result is not None
    assert result.steps[0].index == 0
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].latex_after == r"x \neq 0"
    assert result.steps[0].description == (
        "Restricción de dominio original: x≠0. La ecuación se cumple para toda x "
        "del dominio; el punto excluido no pertenece al conjunto solución."
    )


def test_rational_domain_constant_numerator_preserves_full_step_contract():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree("1/x=0", allow_equation=True)
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(0)], [])
    assert result is not None
    assert result.steps[0].index == 0
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].latex_after == r"x \neq 0"
    assert result.steps[0].description == (
        "Restricción de dominio original: x≠0. Al llevar todo a un denominador común "
        "el numerador es la constante no nula 1; no existe solución."
    )


def test_rational_domain_discarded_root_reports_exact_step():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "((x-1)**2*(x-2))/(x-1)=0", allow_equation=True
    )
    result = solve_service._rational_domain_result(equation, x, [sympy.Integer(1)], [])
    assert result is not None
    assert result.steps[0].description == (
        "Restricción de dominio original: x≠1. x = 1 anula el numerador pero "
        "no pertenece al dominio; se descarta."
    )
    assert result.steps[0].latex_after == r"x \neq 1"


def test_rational_domain_all_roots_excluded_is_a_contradiction_step():
    x = sympy.Symbol("x")
    equation = sympy.Eq(x ** 2 - 1, sympy.Integer(0), evaluate=False)
    result = solve_service._rational_domain_result(
        equation, x, [sympy.Integer(1), sympy.Integer(-1)], []
    )
    assert result is not None
    assert result.result_type == solve_service.ResultType.CONTRADICTION
    assert result.solutions == []
    assert result.input_eq == equation
    assert result.variable == x
    assert result.has_detailed_steps is True
    assert result.warnings == []
    assert result.steps[0].description == (
        "Restricción de dominio original: x≠1, x≠-1. x = -1 anula el numerador "
        "pero no pertenece al dominio; se descarta. x = 1 anula el numerador "
        "pero no pertenece al dominio; se descarta."
    )
    assert result.steps[0].latex_after == r"x \neq 1, x \neq -1"


def test_rational_domain_uncancelled_degree_four_keeps_valid_root():
    x = sympy.Symbol("x")
    equation = solve_service.parsing.parse_expression_tree(
        "(x**4-1)/(x-1)=1", allow_equation=True
    )
    result = solve_service._rational_domain_result(
        equation, x, [sympy.Integer(1)], ["w"]
    )
    assert result is not None
    assert result.result_type == solve_service.ResultType.EQUATION_SOLUTIONS
    assert [solution.text for solution in result.solutions] == ["0"]
    assert result.input_eq == equation
    assert result.variable == x
    assert result.has_detailed_steps is True
    assert result.warnings == ["w"]
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].description == (
        "Restricción de dominio original: x≠1. x = 1 anula el numerador pero "
        "no pertenece al dominio; se descarta."
    )


def test_radical_case_solver_no_candidate_preserves_full_step_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.sqrt(x ** 2 + 1), 0, evaluate=False)
    result = solve_service._radical_cases_result(equation, x, [])
    assert result is not None
    assert result.steps[0].index == 0
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].latex_after == r"\varnothing"


def test_radical_case_solver_extraneous_root_preserves_full_step_contract():
    x = sympy.Symbol("x")
    equation = sympy.Eq(sympy.sqrt(x), x - 2, evaluate=False)
    result = solve_service._radical_cases_result(equation, x, [])
    assert result is not None
    assert [solution.text for solution in result.solutions] == ["4"]
    assert result.steps[0].index == 0
    assert result.steps[0].latex_before == sympy.latex(equation)
    assert result.steps[0].latex_after == r"x = 4"
    assert result.steps[0].description == (
        "Candidato x = 1: no satisface la ecuación original; se descarta "
        "(raíz extraña). Candidato x = 4: verifica la ecuación original."
    )


@pytest.mark.parametrize(
    "text,expected",
    [
        ("P(0,0)", (0, 0)),
        ("P(1,1)", (1, 1)),
        ("P(170,170)", (170, 170)),
        ("P(170,0)", (170, 0)),
    ],
)
def test_permutation_alias_accepts_inclusive_boundaries(text, expected):
    assert solve_service.parsing.permutation_alias_args(text) == expected


@pytest.mark.parametrize(
    "text", ["P(1,2)", "P(0,1)", "P(171,171)", "P(171,0)", "P(-1,0)"]
)
def test_permutation_alias_rejects_out_of_range_boundaries(text):
    with pytest.raises(solve_service.parsing.ParseSecurityError):
        solve_service.parsing.permutation_alias_args(text)
