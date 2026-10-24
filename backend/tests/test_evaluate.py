"""
Tests reales del Módulo 2B para `POST /api/v1/evaluate`, vía `TestClient`
(HTTP real sobre la app FastAPI) — casos de la sección 15.
"""

import math
import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services import evaluate_service

client = TestClient(app)


def _evaluate(**payload):
    return client.post("/api/v1/evaluate", json=payload)


# ---------------------------------------------------------------------------
# Inyecciones -> PARSE_ERROR
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "().__class__",
        "foo.bar",
        "eval(1)",
        "lambda x: x",
        "Integral(x,x)",
    ],
)
def test_injection_attempts_return_parse_error(expression):
    response = _evaluate(expression=expression)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert body["request_id"]


# ---------------------------------------------------------------------------
# Identificador largo
# ---------------------------------------------------------------------------


def test_identifier_too_long_returns_parse_error():
    response = _evaluate(expression="a" * 65 + "+1")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"


# ---------------------------------------------------------------------------
# Unicode: √4+1 -> sqrt(4)+1 -> 3
# ---------------------------------------------------------------------------


def test_unicode_sqrt_is_normalized_and_evaluated():
    response = _evaluate(expression="√4+1")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Punto decimal / notación científica
# ---------------------------------------------------------------------------


def test_valid_decimal_point():
    response = _evaluate(expression="3.14")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(3.14)


def test_decimal_exponential_trig_presentation_is_bounded():
    expression = "exp(-1.3983707058413914)+(-1)*sin(-1.3983707058413914)"
    x = -1.3983707058413914
    expected = math.exp(x) - math.sin(x)

    response = _evaluate(expression=expression)
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-9)
    assert float(body["result_text"]) == pytest.approx(expected, rel=1e-9, abs=1e-9)


@pytest.mark.parametrize("expression", ["1e5", "foo.bar", "5.__class__"])
def test_invalid_decimal_or_scientific_notation(expression):
    response = _evaluate(expression=expression)
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"


# ---------------------------------------------------------------------------
# Aridad de log/ln
# ---------------------------------------------------------------------------


def test_log_two_args_valid():
    response = _evaluate(expression="log(8,2)")  # log base 2 de 8 = 3
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(3.0)


def test_log_three_args_invalid():
    response = _evaluate(expression="log(x,2,3)")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"


def test_ln_requires_exactly_one_arg():
    response = _evaluate(expression="ln(8,2)")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"


# ---------------------------------------------------------------------------
# sin(x) función vs. y(x+1) multiplicación implícita
# ---------------------------------------------------------------------------


def test_sin_as_function_with_substitution():
    response = _evaluate(expression="sin(x)", substitutions={"x": "0"})
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(0.0, abs=1e-9)


def test_y_followed_by_parens_is_implicit_multiplication():
    response = _evaluate(expression="y(x+1)", substitutions={"x": "1", "y": "2"})
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Identificadores multi-letra: theta, 2theta, theta*x, xyz
# ---------------------------------------------------------------------------


def test_multiletter_theta_alone():
    response = _evaluate(expression="theta", substitutions={"theta": "2"})
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(2.0)


def test_multiletter_2theta_implicit_multiplication():
    response = _evaluate(expression="2theta", substitutions={"theta": "3"})
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(6.0)


def test_multiletter_theta_times_x_explicit():
    response = _evaluate(expression="theta*x", substitutions={"theta": "2", "x": "3"})
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(6.0)


def test_multiletter_xyz_single_identifier_not_x_times_y_times_z():
    response = _evaluate(expression="xyz", substitutions={"xyz": "5"})
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Modo grados con substitutions / inversas siempre en radianes
# ---------------------------------------------------------------------------


def test_degree_mode_with_substitution():
    response = _evaluate(expression="sin(x)", substitutions={"x": "90"}, angle_unit="deg")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(1.0, abs=1e-9)


def test_degree_mode_direct_literal():
    response = _evaluate(expression="sin(90)", angle_unit="deg")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(1.0, abs=1e-9)


def test_evaluate_without_substitutions_is_symbolic():
    response = _evaluate(expression="sin(x)")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] is None
    assert body["result_text"] == "sin(x)"


def test_inverse_trig_always_radians_regardless_of_angle_unit():
    response = _evaluate(expression="asin(1)", angle_unit="deg")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(math.pi / 2)


# ---------------------------------------------------------------------------
# Límite de complejidad
# ---------------------------------------------------------------------------


def test_complexity_limit_huge_exponent():
    response = _evaluate(expression="2**100000000")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "COMPLEXITY_LIMIT"


# ---------------------------------------------------------------------------
# substitutions no numéricas -> VALIDATION_ERROR
# ---------------------------------------------------------------------------


def test_substitution_with_free_variable_is_validation_error():
    response = _evaluate(expression="x", substitutions={"x": "y+1"})
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# Truncado de result_latex > 10,000 caracteres (sección 4)
# ---------------------------------------------------------------------------


def test_result_latex_truncated_when_too_long(monkeypatch):
    # Un símbolo de nombre largo produce más de 10.000 caracteres de LaTeX
    # sin construir ni ordenar una suma de 3.000 símbolos (operación
    # cuadrática/costosa en SymPy que bloqueaba el gate acumulativo).
    # El mock prueba exclusivamente el truncado de salida del router.
    huge_expr = sympy.Symbol("x" + "a" * 10_100)

    def _fake_evaluate(expression, angle_unit="rad", substitutions=None):
        return evaluate_service.EvaluateResult(
            expr=huge_expr, input_expr=huge_expr, is_numeric=False, approx_value=None
        )

    monkeypatch.setattr("app.routers.evaluate.evaluate_service.evaluate", _fake_evaluate)
    response = _evaluate(expression="1")
    body = response.json()
    assert body["success"] is True
    assert body["result_latex"] is None
    assert any("10,000" in w for w in body["warnings"])


# ---------------------------------------------------------------------------
# Fase 10 (auditoría Fase 0 v2, port de precision-lab-lite): funciones de
# estadística/combinatoria registradas en ALLOWED_FUNCTIONS — antes de esto,
# min/max estaban BLOQUEADOS como identificadores prohibidos y el resto del
# menú "Stat" del teclado (mean/median/mode/range/stdev/variance/mad/mod/
# gcd/lcm/nCr/nPr) ni siquiera existía como función reconocida.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("mean(1,2,3)", 2.0),
        ("median(1,2,3,4)", 2.5),
        ("mode(1,2,2,3)", 2.0),
        ("min(5,1,3)", 1.0),
        ("max(5,1,3)", 5.0),
        ("range(1,2,9)", 8.0),
        ("stdev(2,4,6)", 2.0),
        ("variance(2,4,6)", 4.0),
        ("var(2,4,6)", 4.0),  # alias real: la tecla del teclado inserta \mathrm{var}
        ("mad(1,2,3)", 2 / 3),
        ("mod(7,3)", 1.0),
        ("gcd(12,18)", 6.0),
        ("lcm(4,6)", 12.0),
        ("nCr(5,2)", 10.0),
        ("nPr(5,2)", 20.0),
    ],
)
def test_stat_and_combinatorics_functions(expression, expected):
    response = _evaluate(expression=expression)
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(expected)


def test_min_and_max_no_longer_blocked_identifiers():
    # Antes de Fase 10: BLOCKED_IDENTIFIERS incluía "min"/"max" (son
    # builtins de Python) por no estar todavía en ALLOWED_FUNCTIONS —
    # producían PARSE_ERROR, no solo "sin evaluar".
    for expression in ("min(1,2)", "max(1,2)"):
        response = _evaluate(expression=expression)
        body = response.json()
        assert body["success"] is True, f"{expression}: {body}"


def test_stat_functions_stay_symbolic_with_free_variables():
    response = _evaluate(expression="mean(x,1)")
    body = response.json()
    assert body["success"] is True
    assert body["result_approx"] is None  # simbólico, no numérico


def test_stdev_with_single_value_is_parse_error():
    # stdev/variance necesitan al menos 2 valores (decisión documentada en
    # stat_functions.py) — con uno solo, Mean.eval levanta ValueError,
    # que _parse_side envuelve como ParseSecurityError -> PARSE_ERROR.
    response = _evaluate(expression="stdev(5)")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"

# S19 targeted coverage r292
def test_render_evaluate_presentation_reports_bounded_symbolic_helper_warnings():
    from app.routers.evaluate import _render_evaluate_presentation

    x = sympy.Symbol("x")
    result = evaluate_service.EvaluateResult(
        expr=x,
        input_expr=x,
        is_numeric=False,
        sum_bound="n",
        binomial_variable="k",
        permutation_alias=True,
    )
    presentation = _render_evaluate_presentation(result, source_expression="x")
    assert "n debe ser un entero no negativo para esta suma simbólica." in presentation["warnings"]
    assert "k debe ser un entero no negativo para combinaciones." in presentation["warnings"]
    assert any("P(n,r) se interpreta como permutaciones" in w for w in presentation["warnings"])


def test_evaluate_endpoint_maps_domain_errors_to_public_response(monkeypatch):
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "0")

    def _raise_domain_error(*args, **kwargs):
        raise evaluate_service.DomainErrorResult("controlled domain-error fixture")

    monkeypatch.setattr(evaluate_service, "evaluate", _raise_domain_error)
    response = _evaluate(expression="1")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["operation"] == "evaluate"
    assert body["error_code"] == "DOMAIN_ERROR"
    assert body["request_id"]


def test_evaluate_endpoint_maps_controlled_timeout_without_claiming_sg28(monkeypatch):
    from app.services.interruptible import ComputationTimedOut

    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "0")

    def _raise_controlled_timeout(*args, **kwargs):
        raise ComputationTimedOut("controlled timeout-mapping fixture")

    monkeypatch.setattr(evaluate_service, "evaluate", _raise_controlled_timeout)
    response = _evaluate(expression="1")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["operation"] == "evaluate"
    assert body["error_code"] == "TIMEOUT"
    assert body["request_id"]


# ---------------------------------------------------------------------------
# S19 targeted coverage r299 - _evaluate_impl error mapping and isolation wiring
# ---------------------------------------------------------------------------

import asyncio
import json
import time
import types

from app.routers import evaluate as evaluate_router
from app.schemas.requests import EvaluateRequest
from app.services import parsing as _parsing
from app.services.ast_validator import ComplexityLimitError as _ComplexityLimitError
from app.services.interruptible import (
    ComputationCancelled as _ComputationCancelled,
    ComputationFailed as _ComputationFailed,
    ComputationTimedOut as _ComputationTimedOut,
)
from app.services.request_cancellation import (
    IsolationCapacityExceeded as _IsolationCapacityExceeded,
)


def _impl_request():
    return types.SimpleNamespace(
        state=types.SimpleNamespace(
            request_id="s19-evaluate-impl",
            start_time=time.perf_counter(),
        )
    )


def _run_impl(payload, **kwargs):
    return asyncio.run(
        evaluate_router._evaluate_impl(payload, _impl_request(), **kwargs)
    )


def _raise(exc):
    def _raiser(*args, **kwargs):
        raise exc

    return _raiser


def _fixture_result():
    expr = sympy.Integer(2)
    return evaluate_service.EvaluateResult(
        expr=expr,
        input_expr=expr,
        is_numeric=True,
        approx_value=2.0,
    )


_FIXTURE_PRESENTATION = {
    "warnings": [],
    "input_latex": "2",
    "result_latex": "2",
    "result_text": "2",
    "domain_conditions": [],
}


@pytest.mark.parametrize(
    "exc,expected_code,expected_message",
    [
        (_parsing.ParseSecurityError("parse boom"), "PARSE_ERROR", "parse boom"),
        (
            _ComplexityLimitError("complexity boom"),
            "COMPLEXITY_LIMIT",
            "complexity boom",
        ),
        (
            evaluate_service.SubstitutionValidationError("substitution boom"),
            "VALIDATION_ERROR",
            "substitution boom",
        ),
        (
            evaluate_service.DomainErrorResult("domain boom"),
            "DOMAIN_ERROR",
            "domain boom",
        ),
        (
            _ComputationTimedOut("timeout fixture"),
            "TIMEOUT",
            "El cálculo excedió el tiempo permitido.",
        ),
        (
            _ComputationCancelled("cancelled fixture"),
            "TIMEOUT",
            "El cálculo fue interrumpido.",
        ),
        (AttributeError("attribute boom"), "DOMAIN_ERROR", "El resultado no está definido en este dominio."),
        (ZeroDivisionError("zero boom"), "DOMAIN_ERROR", "El resultado no está definido en este dominio."),
        (ValueError("value boom"), "DOMAIN_ERROR", "El resultado no está definido en este dominio."),
        (OverflowError("overflow boom"), "DOMAIN_ERROR", "El resultado no está definido en este dominio."),
    ],
)
def test_evaluate_impl_maps_non_isolated_errors(monkeypatch, exc, expected_code, expected_message):
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "0")
    monkeypatch.setattr(evaluate_service, "evaluate", _raise(exc))

    response = _run_impl(EvaluateRequest(expression="1"))

    assert response.success is False
    assert response.error_code == expected_code
    assert response.error_message == expected_message
    assert response.request_id == "s19-evaluate-impl"


@pytest.mark.parametrize(
    "error_type,expected_code",
    [
        ("ParseSecurityError", "PARSE_ERROR"),
        ("ComplexityLimitError", "COMPLEXITY_LIMIT"),
        ("MemoryError", "COMPLEXITY_LIMIT"),
        ("SubstitutionValidationError", "VALIDATION_ERROR"),
        ("DomainErrorResult", "DOMAIN_ERROR"),
        ("AttributeError", "DOMAIN_ERROR"),
        ("ZeroDivisionError", "DOMAIN_ERROR"),
        ("ValueError", "DOMAIN_ERROR"),
        ("OverflowError", "DOMAIN_ERROR"),
        ("SomethingElse", "INTERNAL_ERROR"),
        (None, "INTERNAL_ERROR"),
    ],
)
def test_evaluate_impl_maps_isolated_child_failure_types(monkeypatch, error_type, expected_code):
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    prefix = f"{error_type}: " if error_type else ""
    failure = _ComputationFailed(f"{prefix}child boom", error_type)

    async def _fake_run_for_request(request, operation, *args, **kwargs):
        raise failure

    monkeypatch.setattr(evaluate_router, "run_for_request", _fake_run_for_request)

    response = _run_impl(EvaluateRequest(expression="1"))

    assert response.success is False
    assert response.error_code == expected_code
    assert response.error_message == "child boom"


def test_evaluate_impl_returns_503_when_isolation_capacity_is_exhausted(monkeypatch):
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")

    async def _fake_run_for_request(request, operation, *args, **kwargs):
        raise _IsolationCapacityExceeded("capacity")

    monkeypatch.setattr(evaluate_router, "run_for_request", _fake_run_for_request)

    response = _run_impl(EvaluateRequest(expression="1"))

    assert response.status_code == 503
    body = json.loads(response.body)
    assert body["error_code"] == "INTERNAL_ERROR"
    assert body["error_message"] == "Capacidad de cálculo temporalmente agotada."


def test_evaluate_impl_isolated_success_serializes_public_fields(monkeypatch):
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    calls = []
    result = _fixture_result()

    async def _fake_run_for_request(request, operation, *args, **kwargs):
        calls.append((operation, args, kwargs))
        if operation is evaluate_router._render_evaluate_presentation:
            return dict(_FIXTURE_PRESENTATION)
        return result

    monkeypatch.setattr(evaluate_router, "run_for_request", _fake_run_for_request)

    response = _run_impl(
        EvaluateRequest(expression="7+11", angle_unit="deg", substitutions={"x": "1"}),
        admission_reserved=True,
    )

    assert response.success is True
    assert response.result_type == "scalar"
    assert response.input_text == "7+11"
    assert response.result_approx == 2.0
    assert response.steps == []
    assert response.has_detailed_steps is False
    assert response.result_text == "2"
    assert response.request_id == "s19-evaluate-impl"
    assert [call[0] for call in calls] == [
        evaluate_service.evaluate,
        evaluate_router._render_evaluate_presentation,
    ]
    assert calls[0][1] == ("7+11", "deg", {"x": "1"})
    assert calls[0][2] == {"timeout_seconds": 6, "admission_reserved": True}
    assert calls[1][1] == (result, "7+11")
    assert calls[1][2] == {"timeout_seconds": 4, "admission_reserved": True}


@pytest.mark.parametrize(
    "exc,expected_code,expected_message",
    [
        (
            _IsolationCapacityExceeded("capacity"),
            "INTERNAL_ERROR",
            "Capacidad de cálculo temporalmente agotada.",
        ),
        (
            _ComputationTimedOut("presentation timeout"),
            "TIMEOUT",
            "La presentación excedió el tiempo permitido.",
        ),
        (
            _ComputationCancelled("presentation cancelled"),
            "TIMEOUT",
            "La presentación fue interrumpida.",
        ),
        (
            _ComputationFailed("MemoryError: presentation boom", "MemoryError"),
            "COMPLEXITY_LIMIT",
            "presentation boom",
        ),
        (
            _ComputationFailed("ValueError: presentation boom", "ValueError"),
            "INTERNAL_ERROR",
            "presentation boom",
        ),
        (
            _ComputationFailed("plain presentation boom", None),
            "INTERNAL_ERROR",
            "plain presentation boom",
        ),
    ],
)
def test_evaluate_impl_maps_presentation_phase_failures(
    monkeypatch, exc, expected_code, expected_message
):
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    calls = []

    async def _fake_run_for_request(request, operation, *args, **kwargs):
        calls.append(operation)
        if len(calls) == 1:
            return _fixture_result()
        raise exc

    monkeypatch.setattr(evaluate_router, "run_for_request", _fake_run_for_request)

    response = _run_impl(EvaluateRequest(expression="1"))

    if isinstance(exc, _IsolationCapacityExceeded):
        assert response.status_code == 503
        body = json.loads(response.body)
        assert body["error_code"] == expected_code
        assert body["error_message"] == expected_message
    else:
        assert response.success is False
        assert response.error_code == expected_code
        assert response.error_message == expected_message


def test_computation_failure_message_strips_only_matching_type_prefix():
    assert evaluate_router._computation_failure_message(
        _ComputationFailed("ValueError: boom", "ValueError")
    ) == "boom"
    assert evaluate_router._computation_failure_message(
        _ComputationFailed("ValueError: boom", None)
    ) == "ValueError: boom"
    assert evaluate_router._computation_failure_message(
        _ComputationFailed("boom", "ValueError")
    ) == "boom"


# S19 targeted coverage r299 - _render_evaluate_presentation branches
def _render_fixture(expr, *, input_expr=None, source=None, approx=None, is_numeric=False):
    result = evaluate_service.EvaluateResult(
        expr=expr,
        input_expr=input_expr if input_expr is not None else expr,
        is_numeric=is_numeric,
        approx_value=approx,
    )
    return evaluate_router._render_evaluate_presentation(result, source_expression=source)


@pytest.mark.parametrize(
    "expr,expected_text,expected_latex",
    [
        (sympy.sqrt(3 + 2 * sympy.sqrt(2)), "1 + sqrt(2)", "1 + \\sqrt{2}"),
        (
            sympy.sqrt(5 + 2 * sympy.sqrt(6)),
            "sqrt(2) + sqrt(3)",
            "\\sqrt{2} + \\sqrt{3}",
        ),
        (sympy.sqrt(5), "sqrt(5)", "\\sqrt{5}"),
        (
            sympy.Integer(2) ** sympy.Rational(1, 3),
            "2**(1/3)",
            "\\sqrt[3]{2}",
        ),
    ],
)
def test_render_denests_only_nested_square_roots(expr, expected_text, expected_latex):
    presentation = _render_fixture(expr)
    assert presentation["result_text"] == expected_text
    assert presentation["result_latex"] == expected_latex
    assert presentation["warnings"] == []


def test_render_simplifies_reciprocal_trigonometry():
    presentation = _render_fixture(sympy.csc(sympy.pi / 6))
    assert presentation["result_text"] == "2"
    assert presentation["result_latex"] == "2"


def test_render_rewrites_natural_log_in_text_and_latex():
    x = sympy.Symbol("x")
    presentation = _render_fixture(sympy.log(x))
    assert presentation["result_text"] == "ln(x)"
    assert presentation["result_latex"] == r"\ln{\left(x \right)}"


def test_render_uses_bounded_numeric_approximation_for_decimal_exponentials():
    raw = sympy.exp(sympy.Float("-1.398"), evaluate=False)
    presentation = _render_fixture(
        raw, source="exp(-1.398)", approx=123.456, is_numeric=True
    )
    assert presentation["result_text"] == "123.456000000000"
    assert presentation["result_latex"] == "123.456"


@pytest.mark.parametrize(
    "source,approx",
    [
        ("exp(-1398/1000)", 123.456),
        ("exp(-1.398)", None),
    ],
)
def test_render_decimal_exponential_requires_decimal_source_and_approximation(
    source, approx
):
    raw = sympy.exp(sympy.Float("-1.398"), evaluate=False)
    presentation = _render_fixture(raw, source=source, approx=approx, is_numeric=True)
    assert presentation["result_text"] == "0.247090651392378"


def test_render_decimal_exponential_requires_no_free_symbols():
    x = sympy.Symbol("x")
    presentation = _render_fixture(sympy.exp(x), source="exp(1.5)", approx=1.0)
    assert presentation["result_text"] == "exp(x)"


def test_render_falls_back_to_original_expression_when_simplify_fails(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("controlled simplify failure")

    monkeypatch.setattr(sympy, "simplify", _boom)
    presentation = _render_fixture(sympy.Integer(7))
    assert presentation["result_text"] == "7"
    assert presentation["result_latex"] == "7"


def test_render_handles_integers_too_large_to_stringify(monkeypatch):
    presentation = _render_fixture(sympy.Integer(10) ** 10000)
    assert presentation["result_latex"] is None
    assert presentation["result_text"] == "(resultado numérico demasiado grande para mostrarse)"
    assert presentation["warnings"] == [
        "Resultado LaTeX omitido: el valor numérico es demasiado grande para representarse."
    ]


def test_render_drops_latex_above_the_ten_thousand_character_limit():
    presentation = _render_fixture(sympy.Symbol("a" * 10001))
    assert presentation["result_latex"] is None
    assert presentation["warnings"] == [
        "Resultado LaTeX omitido: excede los 10,000 caracteres (sección 4)."
    ]


def test_render_reports_exact_symbolic_helper_warnings():
    x = sympy.Symbol("x")
    result = evaluate_service.EvaluateResult(
        expr=x,
        input_expr=x,
        is_numeric=False,
        sum_bound="n",
        binomial_variable="k",
        permutation_alias=True,
    )
    presentation = evaluate_router._render_evaluate_presentation(result, source_expression="x")
    assert presentation["warnings"] == [
        "n debe ser un entero no negativo para esta suma simbólica.",
        "k debe ser un entero no negativo para combinaciones.",
        "P(n,r) se interpreta como permutaciones (nPr); una definición local de P prevalece.",
    ]


def test_render_reports_missing_input_latex_when_source_cannot_be_reparsed():
    presentation = _render_fixture(sympy.Integer(5), source=".__bad__")
    assert presentation["input_latex"] is None
    assert presentation["result_text"] == "5"
