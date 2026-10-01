"""
app/routers/algebra.py — `POST /simplify`, `/factor`, `/expand`
(spec, secciones 4, 5, 8.2, 9).
"""

import time
from typing import Optional

import sympy
from fastapi import APIRouter, Request

from app.core.logging import log_request_event
from app.schemas.requests import ExpressionRequest, SolveRequest
from app.schemas.responses import ErrorCode, MathResponse, OperationType, ResultType
from app.services import algebra_service, parsing, solve_service
from app.services.ast_validator import ComplexityLimitError

router = APIRouter(tags=["algebra"])

_MAX_RESULT_LATEX_LENGTH = 10_000


def _duration_ms(request: Request) -> float:
    return (time.perf_counter() - request.state.start_time) * 1000


def _error(
    request: Request, operation: OperationType, error_code: ErrorCode, message: str
) -> MathResponse:
    return MathResponse(
        success=False,
        operation=operation,
        request_id=request.state.request_id,
        has_detailed_steps=False,
        error_code=error_code,
        error_message=message,
        duration_ms=_duration_ms(request),
    )


def _safe_latex(expr: sympy.Expr) -> Optional[str]:
    try:
        return sympy.latex(expr)
    except ValueError:
        # Ver app/routers/evaluate.py: mismo hallazgo del Módulo 2B (enteros
        # que exceden el límite de conversión int->str de Python).
        return None


def _safe_text(expr: sympy.Expr) -> str:
    try:
        return str(expr)
    except ValueError:
        return "(resultado numérico demasiado grande para mostrarse)"


def _build_response(
    request: Request,
    operation: OperationType,
    payload: ExpressionRequest,
    result,
) -> MathResponse:
    warnings = []
    result_latex = _safe_latex(result.result_expr)
    if result_latex is None:
        warnings.append(
            "Resultado LaTeX omitido: el valor numérico es demasiado grande " "para representarse."
        )
    elif len(result_latex) > _MAX_RESULT_LATEX_LENGTH:
        result_latex = None
        warnings.append("Resultado LaTeX omitido: excede los 10,000 caracteres (sección 4).")

    input_latex = _safe_latex(result.input_expr)
    symbols = result.input_expr.free_symbols | result.result_expr.free_symbols
    graph_polynomial_comparison = (
        len(symbols) == 1
        and result.input_expr.is_polynomial(*symbols) is True
        and result.result_expr.is_polynomial(*symbols) is True
    )

    return MathResponse(
        success=True,
        operation=operation,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        input_text=payload.expression,
        input_latex=input_latex,
        result_latex=result_latex,
        result_text=_safe_text(result.result_expr),
        graph_polynomial_comparison=graph_polynomial_comparison,
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/simplify", response_model=MathResponse)
async def simplify(payload: ExpressionRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "simplify_request", input_text=payload.expression)
    try:
        result = algebra_service.simplify_expression(payload.expression)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.SIMPLIFY, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.SIMPLIFY, ErrorCode.COMPLEXITY_LIMIT, str(exc))
    return _build_response(request, OperationType.SIMPLIFY, payload, result)


@router.post("/expand", response_model=MathResponse)
async def expand(payload: ExpressionRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "expand_request", input_text=payload.expression)
    try:
        result = algebra_service.expand_expression(payload.expression)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.EXPAND, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.EXPAND, ErrorCode.COMPLEXITY_LIMIT, str(exc))
    return _build_response(request, OperationType.EXPAND, payload, result)


@router.post("/factor", response_model=MathResponse)
async def factor(payload: ExpressionRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "factor_request", input_text=payload.expression)
    try:
        result = algebra_service.factor_expression(payload.expression)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.FACTOR, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.FACTOR, ErrorCode.COMPLEXITY_LIMIT, str(exc))
    return _build_response(request, OperationType.FACTOR, payload, result)


@router.post("/solve", response_model=MathResponse)
async def solve(payload: SolveRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "solve_request", input_text=payload.equation)
    try:
        result = solve_service.solve_equation(
            payload.equation,
            payload.variable,
            payload.angle_unit,
            payload.domain,
            payload.domain_lower,
            payload.domain_upper,
            payload.domain_lower_inclusive,
            payload.domain_upper_inclusive,
        )
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.SOLVE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.SOLVE, ErrorCode.COMPLEXITY_LIMIT, str(exc))
    except solve_service.AmbiguousVariableError as exc:
        return _error(request, OperationType.SOLVE, ErrorCode.AMBIGUOUS_VARIABLE, str(exc))
    except NotImplementedError as exc:
        return _error(
            request,
            OperationType.SOLVE,
            ErrorCode.UNSUPPORTED_OPERATION,
            str(exc),
        )

    warnings = list(result.warnings)
    result_data = result.solutions if result.result_type == ResultType.EQUATION_SOLUTIONS else None

    return MathResponse(
        success=True,
        operation=OperationType.SOLVE,
        request_id=request.state.request_id,
        result_type=result.result_type,
        input_text=payload.equation,
        input_latex=_safe_latex(result.input_eq),
        result_data=result_data,
        complex_graph_points=result.graph_points,
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=warnings,
        duration_ms=_duration_ms(request),
    )
