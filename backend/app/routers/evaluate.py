"""
app/routers/evaluate.py — `POST /evaluate` (spec, secciones 3, 4, 5, 6, 7, 9).
"""

import re
import time

import sympy
from fastapi import APIRouter, Request

from app.core.logging import log_request_event
from app.schemas.requests import EvaluateRequest
from app.schemas.responses import ErrorCode, MathResponse, OperationType, ResultType
from app.services import evaluate_service, parsing
from app.services.ast_validator import ComplexityLimitError

router = APIRouter(tags=["evaluate"])

_MAX_RESULT_LATEX_LENGTH = 10_000


def _duration_ms(request: Request) -> float:
    return (time.perf_counter() - request.state.start_time) * 1000


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


@router.post("/evaluate", response_model=MathResponse)
async def evaluate(payload: EvaluateRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "evaluate_request", input_text=payload.expression)

    try:
        result = evaluate_service.evaluate(
            payload.expression, payload.angle_unit, payload.substitutions
        )
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

    warnings = []

    # S18 r293/r294/r295 (portado desde Plus): el parser seguro construye el
    # AST con `evaluate=False` y la transformación `rationalize`, de modo que
    # un decimal literal como -1.3983707058413914 entra como Rational exacto
    # (-6991853529206957/5000000000000000). Para expresiones totalmente
    # numéricas que contienen exp(), `sympy.simplify()` sobre esa forma puede
    # agotar memoria/CPU sin límite (contraejemplo reproducido por el runner
    # S18 con seed 180018: `exp(-1.3983707058413914)+(-1)*sin(-1.3983707058413914)`).
    # El evaluador ya calculó una aproximación numérica acotada
    # (`result.approx_value`); para la presentación de ese caso se usa
    # directamente en vez de pedirle a `simplify()` una forma exacta no
    # acotada. El guard exige: sin símbolos libres, fuente con un decimal
    # independiente (no `1.5x`, no fracciones `1398/1000`), presencia real de
    # `exp` en el AST sin evaluar y aproximación disponible.
    def _decimal_exponential_source(source_expression: str) -> bool:
        return re.search(r"(?<![A-Za-z0-9_.])\d+\.\d+(?![A-Za-z0-9_])", source_expression) is not None

    display_expr = result.expr
    if (
        not display_expr.free_symbols
        and payload.expression is not None
        and _decimal_exponential_source(payload.expression)
        and display_expr.has(sympy.exp)
        and result.approx_value is not None
    ):
        display_expr = sympy.Float(result.approx_value)
    else:
        try:
            simplified = sympy.simplify(display_expr)
        except Exception:
            # Un simplify() controladamente fallido (p. ej. MemoryError bajo
            # presión) no debe tumbar la respuesta: se conserva la expresión
            # original para la presentación.
            simplified = None
        if simplified is not None:
            display_expr = simplified

    try:
        result_latex = sympy.latex(display_expr)
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
        except ValueError:
            result_text = "(resultado numérico demasiado grande para mostrarse)"

    try:
        input_latex = sympy.latex(result.input_expr)
    except ValueError:
        input_latex = None

    return MathResponse(
        success=True,
        operation=OperationType.EVALUATE,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        input_text=payload.expression,
        input_latex=input_latex,
        result_latex=result_latex,
        result_text=result_text,
        result_approx=result.approx_value,
        steps=[],
        has_detailed_steps=False,
        warnings=warnings,
        duration_ms=_duration_ms(request),
    )
