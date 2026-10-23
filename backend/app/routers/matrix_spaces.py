"""MV-E routes: /matrix/nullspace and /matrix/columnspace."""

import time

import sympy
from fastapi import APIRouter, Request

from app.core.logging import log_request_event
from app.schemas.requests import MatrixSingleRequest
from app.schemas.responses import ErrorCode, MathResponse, OperationType, ResultType
from app.services import matrix_service, matrix_spaces, parsing
from app.services.ast_validator import ComplexityLimitError

router = APIRouter(tags=["matrices"])


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


@router.post("/matrix/nullspace", response_model=MathResponse)
async def matrix_nullspace(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_nullspace_request")
    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_NULLSPACE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_NULLSPACE, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    result = matrix_spaces.nullspace(matrix)
    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_NULLSPACE,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        result_latex=sympy.latex(result.result_matrix.T) if result.result_matrix.rows else "\\{\\}",
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/columnspace", response_model=MathResponse)
async def matrix_columnspace(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_columnspace_request")
    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_COLUMNSPACE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_COLUMNSPACE, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    result = matrix_spaces.columnspace(matrix)
    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_COLUMNSPACE,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        result_latex=sympy.latex(result.result_matrix.T) if result.result_matrix.rows else "\\{\\}",
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )
