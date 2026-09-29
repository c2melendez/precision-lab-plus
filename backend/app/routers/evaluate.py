"""
app/routers/evaluate.py — `POST /evaluate` (spec, secciones 3, 4, 5, 6, 7, 9).
"""

import time

import sympy
from fastapi import APIRouter, Request

from app.core.logging import log_request_event
from app.schemas.requests import EvaluateRequest
from app.schemas.responses import ComplexGraphComponents, ComplexGraphPoint, ErrorCode, MathResponse, OperationType, ResultType
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
    try:
        result_latex = sympy.latex(result.expr)
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
            result_text = str(result.expr)
        except ValueError:
            result_text = "(resultado numérico demasiado grande para mostrarse)"

    try:
        input_latex = sympy.latex(result.input_expr)
    except ValueError:
        input_latex = None

    complex_points = None
    complex_components = None
    if not result.expr.free_symbols and result.expr.is_number and result.expr.has(sympy.I):
        try:
            re_value = float(sympy.N(sympy.re(result.expr)))
            im_value = float(sympy.N(sympy.im(result.expr)))
            if all(sympy.Float(v).is_finite and abs(v) <= 1e6 for v in (re_value, im_value)):
                complex_points = [ComplexGraphPoint(re=re_value, im=im_value, label=result_text)]
        except (AttributeError, TypeError, ValueError, OverflowError):
            pass
    symbols = result.expr.free_symbols
    if len(symbols) == 1 and result.expr.has(sympy.I) and sympy.count_ops(result.expr) <= 30:
        source_symbol = next(iter(symbols))
        if source_symbol.name in ("x", "t"):
            real_symbol = sympy.Symbol(source_symbol.name, real=True)
            try:
                real_expr = result.expr.subs(source_symbol, real_symbol)
                re_part = sympy.expand_complex(sympy.re(real_expr))
                im_part = sympy.expand_complex(sympy.im(real_expr))
                if (re_part.is_real is True and im_part.is_real is True
                        and not re_part.has(sympy.re, sympy.im, sympy.I)
                        and not im_part.has(sympy.re, sympy.im, sympy.I)
                        and sympy.count_ops(re_part) + sympy.count_ops(im_part) <= 80):
                    complex_components = ComplexGraphComponents(
                        variable=source_symbol.name,
                        re_expression=str(re_part), im_expression=str(im_part),
                        re_latex=sympy.latex(re_part), im_latex=sympy.latex(im_part),
                    )
            except (AttributeError, TypeError, ValueError, OverflowError, NotImplementedError):
                pass

    return MathResponse(
        success=True,
        operation=OperationType.EVALUATE,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        input_text=payload.expression,
        input_latex=input_latex,
        result_latex=result_latex,
        result_text=result_text,
        complex_graph_points=complex_points,
        complex_graph_components=complex_components,
        result_approx=result.approx_value,
        steps=[],
        has_detailed_steps=False,
        warnings=warnings,
        duration_ms=_duration_ms(request),
    )
