"""
app/routers/evaluate.py — `POST /evaluate` (spec, secciones 3, 4, 5, 6, 7, 9).
"""

import time
import os

import sympy
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.logging import log_request_event
from app.schemas.requests import EvaluateRequest
from app.schemas.responses import ErrorCode, MathResponse, OperationType, ResultType
from app.services import evaluate_service, parsing
from app.services.ast_validator import ComplexityLimitError
from app.services.interruptible import ComputationCancelled, ComputationFailed, ComputationTimedOut
from app.services.request_cancellation import IsolationCapacityExceeded, run_for_request

def _sg28_ci_slow_evaluate(expression, angle_unit, substitutions):
    """Picklable E2E fixture; selected only under explicit CI test flags."""
    time.sleep(4)
    return evaluate_service.evaluate(expression, angle_unit, substitutions)


def _render_evaluate_presentation(result, source_expression=None):
    """Render in an independent, killable SG28 worker if isolation is on."""
    warnings = []
    # H1 round-trip: el parser seguro construye el AST con evaluate=False
    # para no ejecutar/simplificar durante el parseo. Esa forma puede
    # conservar artefactos como 1*(1/3) o asin(1/2) sin reducir. La salida
    # pública, en cambio, debe ser canónica y reingresable sin acumular
    # factores ni cambiar de significado.
    try:
        display_expr = sympy.simplify(result.expr)
    except Exception:
        display_expr = result.expr

    try:
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
        except ValueError:
            result_text = "(resultado numérico demasiado grande para mostrarse)"

    try:
        # Pickle may evaluate previously unevaluated SymPy AST nodes (2+3 -> 5).
        # Reparse inside the bounded presentation child to retain original input LaTeX.
        input_expr = (parsing.parse_expression_tree(source_expression)
                      if source_expression is not None else result.input_expr)
        input_latex = sympy.latex(input_expr)
    except ValueError:
        input_latex = None

    return {"warnings": warnings, "input_latex": input_latex,
            "result_latex": result_latex, "result_text": result_text}


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
        if os.getenv("SG28_EVALUATE_ISOLATION", "0") == "1":
            # Opt-in experimental path; default production behavior remains unchanged.
            result = await run_for_request(
                request,
                (_sg28_ci_slow_evaluate if os.getenv('SG28_CI_SLOW', '0') == '1' and os.getenv('SG28_CI_OBSERVE', '0') == '1' and payload.expression == '7+11' else evaluate_service.evaluate),
                payload.expression, payload.angle_unit, payload.substitutions,
                timeout_seconds=6,
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
        return _error(request, code, str(exc))
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
        presentation = (await run_for_request(request, _render_evaluate_presentation, result, payload.expression, timeout_seconds=4)
                        if os.getenv("SG28_EVALUATE_ISOLATION", "0") == "1"
                        else _render_evaluate_presentation(result))
    except IsolationCapacityExceeded:
        error = _error(request, ErrorCode.INTERNAL_ERROR, "Capacidad de cálculo temporalmente agotada.")
        return JSONResponse(status_code=503, content=error.model_dump(mode="json"))
    except ComputationTimedOut:
        return _error(request, ErrorCode.TIMEOUT, "La presentación excedió el tiempo permitido.")
    except ComputationCancelled:
        return _error(request, ErrorCode.TIMEOUT, "La presentación fue interrumpida.")
    except ComputationFailed as exc:
        return _error(request, ErrorCode.COMPLEXITY_LIMIT if exc.error_type == "MemoryError" else ErrorCode.INTERNAL_ERROR, str(exc))

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
