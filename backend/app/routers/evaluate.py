"""
app/routers/evaluate.py — `POST /evaluate` (spec, secciones 3, 4, 5, 6, 7, 9).
"""

import time
import os
import re

import sympy
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.logging import log_request_event
from app.schemas.requests import EvaluateRequest
from app.schemas.responses import ErrorCode, MathResponse, OperationType, ResultType
from app.services import evaluate_service, parsing
from app.services.domain_analysis import extract_domain_conditions
from app.services.ast_validator import ComplexityLimitError
from app.services.interruptible import ComputationCancelled, ComputationFailed, ComputationTimedOut
from app.services.request_cancellation import IsolationCapacityExceeded, request_admission_lease, run_for_request

def _sg28_ci_slow_evaluate(expression, angle_unit, substitutions):
    """Picklable E2E fixture; selected only under explicit CI test flags."""
    time.sleep(4)
    return evaluate_service.evaluate(expression, angle_unit, substitutions)


def _render_evaluate_presentation(result, source_expression=None):
    """Render in an independent, killable SG28 worker if isolation is on."""
    warnings = []
    if getattr(result, "sum_bound", None) is not None:
        warnings.append(f"{result.sum_bound} debe ser un entero no negativo para esta suma simbólica.")
    if getattr(result, "binomial_variable", None) is not None:
        warnings.append(f"{result.binomial_variable} debe ser un entero no negativo para combinaciones.")
    if getattr(result, "permutation_alias", False):
        warnings.append("P(n,r) se interpreta como permutaciones (nPr); una definición local de P prevalece.")
    # H1 round-trip: el parser seguro construye el AST con evaluate=False
    # para no ejecutar/simplificar durante el parseo. Esa forma puede
    # conservar artefactos como 1*(1/3) o asin(1/2) sin reducir. La salida
    # pública, en cambio, debe ser canónica y reingresable sin acumular
    # factores ni cambiar de significado.
    try:
        # S18 r293 exposed an unbounded SymPy simplify() case: rationalized
        # decimal input exp(-1.398...)+(-1)*sin(-1.398...) can exhaust memory
        # while simplifying a fully numeric transcendental expression. For
        # numeric expressions with a decimal source and exp(), the evaluator
        # already computed a bounded numeric approximation; use it directly
        # for presentation instead of asking simplify() to prove an exact form.
        decimal_exponential = (
            not result.expr.free_symbols
            and source_expression is not None
            and re.search(r"(?<![A-Za-z0-9_.])\d+\.\d+(?![A-Za-z0-9_])", source_expression)
            and result.expr.has(sympy.exp)
            and result.approx_value is not None
        )
        display_expr = (
            sympy.Float(result.approx_value)
            if decimal_exponential
            else sympy.simplify(result.expr)
        )
    except Exception:
        display_expr = result.expr

    # EV-R-11/EV-R-12: SymPy keeps nested radicals such as sqrt(3+2*sqrt(2))
    # unevaluated, while the frozen matrix requires the denested exact form
    # (1+sqrt(2), sqrt(2)+sqrt(3)). Only a bare square root whose radicand
    # already contains a square root is denested; any other result is left
    # untouched, and a failed denest keeps the original expression.
    try:
        from sympy.simplify.sqrtdenest import sqrtdenest

        if (
            getattr(display_expr, "is_Pow", False)
            and display_expr.exp == sympy.Rational(1, 2)
            and any(
                atom.exp == sympy.Rational(1, 2)
                for atom in display_expr.base.atoms(sympy.Pow)
            )
        ):
            denested = sqrtdenest(display_expr)
            if denested is not None:
                display_expr = denested
    except Exception:
        pass

    try:
        # Keep the displayed LaTeX consistent with the canonical scalar text.
        # Unevaluated reciprocal trig ASTs can format as csc(pi/6) even though
        # the mathematical value is exactly 2. Trig simplification is bounded
        # to expressions containing reciprocal trigonometric functions.
        if display_expr.has(sympy.csc, sympy.sec, sympy.cot):
            display_expr = sympy.trigsimp(display_expr)
        result_latex = sympy.latex(display_expr)
        # H1 round-trip: SymPy representa el logaritmo natural con \\log,
        # pero Precision Lab reserva \\log para base 10 y usa \\ln para
        # el natural. Normalizar la salida evita cambiar el significado al
        # reingresar el propio resultado.
        result_latex = result_latex.replace(r"\log", r"\ln")
    except ValueError:
        # Un entero cuya magnitud excede el límite de conversión int->str de
        # Python (`sys.set_int_max_str_digits`) puede surgir incluso dentro
        # de los límites de la etapa 9 (que acotan el EXPONENTE de entrada,
        # no la magnitud final tras evaluar — ej. 99**10000 tiene ~19,903
        # dígitos aunque el exponente 10000 esté permitido). Hallazgo real
        # del testing del Módulo 2B, no anticipado por la spec. Se trata con
        # el mismo mecanismo que un LaTeX > 10,000 caracteres, en vez de
        # dejar que se propague como un 500 genérico.
        result_latex = None
        warnings.append(
            "Resultado LaTeX omitido: el valor numérico es demasiado grande " "para representarse."
        )
        result_text = "(resultado numérico demasiado grande para mostrarse)"
    else:
        if len(result_latex) > _MAX_RESULT_LATEX_LENGTH:
            result_latex = None
            warnings.append("Resultado LaTeX omitido: excede los 10,000 caracteres (sección 4).")
        try:
            result_text = str(display_expr)
            # SymPy prints natural logarithms as log(...), while our input
            # parser reserves log(...) for base 10. Preserve round-trip
            # semantics explicitly in the plain-text result as in LaTeX.
            if display_expr.has(sympy.log):
                result_text = result_text.replace("log(", "ln(")
        except ValueError:
            result_text = "(resultado numérico demasiado grande para mostrarse)"

    domain_conditions = []
    try:
        # Pickle may evaluate previously unevaluated SymPy AST nodes (2+3 -> 5).
        # Reparse inside the bounded presentation child to retain original input LaTeX.
        presentation_source = (evaluate_service.normalize_inline_substitution(source_expression)[0]
                               if source_expression is not None else None)
        input_expr = (parsing.parse_expression_tree(presentation_source)
                      if presentation_source is not None else result.input_expr)
        domain_conditions = extract_domain_conditions(input_expr)
        input_latex = sympy.latex(input_expr)
    except ValueError:
        input_latex = None

    return {"warnings": warnings, "input_latex": input_latex,
            "result_latex": result_latex, "result_text": result_text,
            "domain_conditions": domain_conditions}


router = APIRouter(tags=["evaluate"])

_MAX_RESULT_LATEX_LENGTH = 10_000


def _duration_ms(request: Request) -> float:
    return (time.perf_counter() - request.state.start_time) * 1000


def _computation_failure_message(exc: ComputationFailed) -> str:
    """Return child error text without type prefix to preserve public API parity."""
    message = str(exc)
    prefix = f"{exc.error_type}: " if exc.error_type else ""
    return message[len(prefix):] if prefix and message.startswith(prefix) else message


def _error(request: Request, error_code: ErrorCode, message: str) -> MathResponse:
    return MathResponse(
        success=False,
        operation=OperationType.EVALUATE,
        request_id=request.state.request_id,
        has_detailed_steps=False,
        error_code=error_code,
        error_message=message,
        duration_ms=_duration_ms(request),
    )


async def _evaluate_impl(payload: EvaluateRequest, request: Request, *, admission_reserved: bool = False) -> MathResponse:
    log_request_event(request.state.request_id, "evaluate_request", input_text=payload.expression)

    try:
        if os.getenv("SG28_EVALUATE_ISOLATION", "0") == "1":
            # Opt-in experimental path; default production behavior remains unchanged.
            result = await run_for_request(
                request,
                (_sg28_ci_slow_evaluate if os.getenv('SG28_CI_SLOW', '0') == '1' and os.getenv('SG28_CI_OBSERVE', '0') == '1' and payload.expression == '7+11' else evaluate_service.evaluate),
                payload.expression, payload.angle_unit, payload.substitutions,
                timeout_seconds=6, admission_reserved=admission_reserved,
            )
        else:
            result = evaluate_service.evaluate(
                payload.expression, payload.angle_unit, payload.substitutions
            )
    except IsolationCapacityExceeded:
        error = _error(request, ErrorCode.INTERNAL_ERROR, "Capacidad de cálculo temporalmente agotada.")
        return JSONResponse(status_code=503, content=error.model_dump(mode="json"))
    except ComputationFailed as exc:
        child_error_codes = {
            "ParseSecurityError": ErrorCode.PARSE_ERROR,
            "ComplexityLimitError": ErrorCode.COMPLEXITY_LIMIT,
            "MemoryError": ErrorCode.COMPLEXITY_LIMIT,
            "SubstitutionValidationError": ErrorCode.VALIDATION_ERROR,
            "DomainErrorResult": ErrorCode.DOMAIN_ERROR,
            "AttributeError": ErrorCode.DOMAIN_ERROR,
            "ZeroDivisionError": ErrorCode.DOMAIN_ERROR,
            "ValueError": ErrorCode.DOMAIN_ERROR,
            "OverflowError": ErrorCode.DOMAIN_ERROR,
        }
        code = child_error_codes.get(exc.error_type, ErrorCode.INTERNAL_ERROR)
        return _error(request, code, _computation_failure_message(exc))
    except ComputationTimedOut:
        return _error(request, ErrorCode.TIMEOUT, "El cálculo excedió el tiempo permitido.")
    except ComputationCancelled:
        return _error(request, ErrorCode.TIMEOUT, "El cálculo fue interrumpido.")
    except parsing.ParseSecurityError as exc:
        return _error(request, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, ErrorCode.COMPLEXITY_LIMIT, str(exc))
    except evaluate_service.SubstitutionValidationError as exc:
        return _error(request, ErrorCode.VALIDATION_ERROR, str(exc))
    except evaluate_service.DomainErrorResult as exc:
        return _error(request, ErrorCode.DOMAIN_ERROR, str(exc))
    except (AttributeError, ZeroDivisionError, ValueError, OverflowError):
        # Safety net for numeric-domain failures raised internally by SymPy.
        # These inputs are mathematically undefined/unsupported, not server
        # faults, and must never escape as HTTP 500 (e.g. sec(pi/2)).
        return _error(
            request,
            ErrorCode.DOMAIN_ERROR,
            "El resultado no está definido en este dominio.",
        )

    try:
        presentation = (await run_for_request(request, _render_evaluate_presentation, result, payload.expression, timeout_seconds=4, admission_reserved=admission_reserved)
                        if os.getenv("SG28_EVALUATE_ISOLATION", "0") == "1"
                        else _render_evaluate_presentation(result, payload.expression))
    except IsolationCapacityExceeded:
        error = _error(request, ErrorCode.INTERNAL_ERROR, "Capacidad de cálculo temporalmente agotada.")
        return JSONResponse(status_code=503, content=error.model_dump(mode="json"))
    except ComputationTimedOut:
        return _error(request, ErrorCode.TIMEOUT, "La presentación excedió el tiempo permitido.")
    except ComputationCancelled:
        return _error(request, ErrorCode.TIMEOUT, "La presentación fue interrumpida.")
    except ComputationFailed as exc:
        return _error(request, ErrorCode.COMPLEXITY_LIMIT if exc.error_type == "MemoryError" else ErrorCode.INTERNAL_ERROR, _computation_failure_message(exc))

    return MathResponse(
        success=True,
        operation=OperationType.EVALUATE,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        input_text=payload.expression,
        result_approx=result.approx_value,
        steps=[],
        has_detailed_steps=False,
        **presentation,
        duration_ms=_duration_ms(request),
    )


@router.post("/evaluate", response_model=MathResponse)
async def evaluate(payload: EvaluateRequest, request: Request) -> MathResponse:
    """Hold local quota across both phases when SG28 isolation is opted in."""
    if os.getenv("SG28_EVALUATE_ISOLATION", "0") != "1":
        return await _evaluate_impl(payload, request)
    try:
        with request_admission_lease():
            return await _evaluate_impl(payload, request, admission_reserved=True)
    except IsolationCapacityExceeded:
        error = _error(request, ErrorCode.INTERNAL_ERROR, "Capacidad de cálculo temporalmente agotada.")
        return JSONResponse(status_code=503, content=error.model_dump(mode="json"))
