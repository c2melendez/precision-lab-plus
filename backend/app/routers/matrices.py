"""
app/routers/matrices.py — `POST /matrix/operations` (spec, secciones 4, 5,
8.6, 9).
"""

import time

import sympy
from fastapi import APIRouter, Request

from app.core.logging import log_request_event
from app.schemas.requests import (
    MatrixEigenRequest,
    MatrixEquationRequest,
    MatrixOperationRequest,
    MatrixPowerRequest,
    MatrixSingleRequest,
)
from app.schemas.responses import ErrorCode, MathResponse, MatrixOpKind, OperationType, ResultType
from app.services import matrix_service, parsing
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


@router.post("/matrix/operations", response_model=MathResponse)
async def matrix_operations(payload: MatrixOperationRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_operations_request")

    try:
        matrix_a = matrix_service.parse_matrix(payload.matrix_a)
        matrix_b = matrix_service.parse_matrix(payload.matrix_b)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_OPERATION, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_OPERATION, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        if payload.operation in (MatrixOpKind.ADD, MatrixOpKind.SUBTRACT):
            result = matrix_service.add_or_subtract(matrix_a, matrix_b, payload.operation)
        elif payload.operation == MatrixOpKind.KRONECKER:
            result = matrix_service.kronecker(matrix_a, matrix_b)
        elif payload.operation == MatrixOpKind.CROSS:
            result = matrix_service.cross(matrix_a, matrix_b)
        elif payload.operation == MatrixOpKind.DOT:
            # P5 (spec v2 §6): dot devuelve un escalar (ScalarStepResult),
            # no una matriz — se arma la respuesta aparte, no puede pasar
            # por el "return MathResponse(...)" genérico de abajo (que
            # asume result.result_matrix).
            dot_result = matrix_service.dot(matrix_a, matrix_b)
            return MathResponse(
                success=True,
                operation=OperationType.MATRIX_OPERATION,
                request_id=request.state.request_id,
                result_type=ResultType.SCALAR,
                result_text=str(dot_result.value),
                result_latex=sympy.latex(dot_result.value),
                result_approx=float(dot_result.value) if dot_result.value.is_real else None,
                steps=dot_result.steps,
                has_detailed_steps=dot_result.has_detailed_steps,
                warnings=dot_result.warnings,
                duration_ms=_duration_ms(request),
            )
        else:
            result = matrix_service.multiply(matrix_a, matrix_b)
    except matrix_service.DimensionMismatchError as exc:
        return _error(
            request, OperationType.MATRIX_OPERATION, ErrorCode.DIMENSION_MISMATCH, str(exc)
        )

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_OPERATION,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/ref", response_model=MathResponse)
async def matrix_ref(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """Fase C (spec UX estilo ClassCalc, sección 4)."""
    log_request_event(request.state.request_id, "matrix_ref_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_REF, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_REF, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    result = matrix_service.ref(matrix)

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_REF,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/rref", response_model=MathResponse)
async def matrix_rref(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """Fase C (spec UX estilo ClassCalc, sección 4)."""
    log_request_event(request.state.request_id, "matrix_rref_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_RREF, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_RREF, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    result = matrix_service.rref(matrix)

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_RREF,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/lu", response_model=MathResponse)
async def matrix_lu(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """MV-D-16: factorización LU de Doolittle sin pivoteo."""
    log_request_event(request.state.request_id, "matrix_lu_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_LU, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_LU, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.lu_decomposition(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_LU, ErrorCode.DIMENSION_MISMATCH, str(exc))
    except matrix_service.UnsupportedOperationError as exc:
        return _error(request, OperationType.MATRIX_LU, ErrorCode.UNSUPPORTED_OPERATION, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_LU,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_latex=(
            f"L = {sympy.latex(result.lower)},\\quad U = {sympy.latex(result.upper)}"
        ),
        result_matrices={
            "L": matrix_service.matrix_to_result_data(result.lower),
            "U": matrix_service.matrix_to_result_data(result.upper),
        },
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/gram-schmidt", response_model=MathResponse)
async def matrix_gram_schmidt(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """MV-D-17: Gram-Schmidt sin normalizar; cada fila es un vector."""
    log_request_event(request.state.request_id, "matrix_gram_schmidt_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_GRAM_SCHMIDT, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(
            request,
            OperationType.MATRIX_GRAM_SCHMIDT,
            ErrorCode.COMPLEXITY_LIMIT,
            str(exc),
        )

    try:
        result = matrix_service.gram_schmidt(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(
            request, OperationType.MATRIX_GRAM_SCHMIDT, ErrorCode.DIMENSION_MISMATCH, str(exc)
        )
    except matrix_service.UnsupportedOperationError as exc:
        return _error(
            request,
            OperationType.MATRIX_GRAM_SCHMIDT,
            ErrorCode.UNSUPPORTED_OPERATION,
            str(exc),
        )

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_GRAM_SCHMIDT,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        result_latex=sympy.latex(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/determinant", response_model=MathResponse)
async def matrix_determinant(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_determinant_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix, allow_symbolic=True)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_DETERMINANT, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(
            request, OperationType.MATRIX_DETERMINANT, ErrorCode.COMPLEXITY_LIMIT, str(exc)
        )

    try:
        result = matrix_service.determinant(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(
            request, OperationType.MATRIX_DETERMINANT, ErrorCode.DIMENSION_MISMATCH, str(exc)
        )

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_DETERMINANT,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        result_text=str(result.value),
        result_latex=sympy.latex(result.value),
        result_approx=float(result.value) if result.value.is_real else None,
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/inverse", response_model=MathResponse)
async def matrix_inverse(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_inverse_request")

    try:
        # MV-C-10/11: la inversa sí admite variables y trigonométricas
        # elementales. Es la segunda operación simbólica acotada, junto con
        # el determinante; el resto de /matrix/* sigue siendo numérico.
        matrix = matrix_service.parse_matrix(payload.matrix, allow_symbolic=True)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_INVERSE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_INVERSE, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.inverse(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_INVERSE, ErrorCode.DIMENSION_MISMATCH, str(exc))
    except matrix_service.SingularMatrixError as exc:
        return _error(request, OperationType.MATRIX_INVERSE, ErrorCode.SINGULAR_MATRIX, str(exc))
    except matrix_service.UnsupportedOperationError as exc:
        return _error(
            request, OperationType.MATRIX_INVERSE, ErrorCode.UNSUPPORTED_OPERATION, str(exc)
        )

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_INVERSE,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/adjugate", response_model=MathResponse)
async def matrix_adjugate(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """MV-C-14/15: adjunta de una matriz cuadrada."""
    log_request_event(request.state.request_id, "matrix_adjugate_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_ADJUGATE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_ADJUGATE, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.adjugate(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_ADJUGATE, ErrorCode.DIMENSION_MISMATCH, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_ADJUGATE,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/cofactor", response_model=MathResponse)
async def matrix_cofactor(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """MV-C-16: matriz de cofactores."""
    log_request_event(request.state.request_id, "matrix_cofactor_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_COFACTOR, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_COFACTOR, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.cofactor_matrix(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_COFACTOR, ErrorCode.DIMENSION_MISMATCH, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_COFACTOR,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/solve-equation", response_model=MathResponse)
async def matrix_solve_equation(payload: MatrixEquationRequest, request: Request) -> MathResponse:
    """MV-C-18/19: X·A = B (x_side="left") o A·X = B (x_side="right")."""
    log_request_event(request.state.request_id, "matrix_solve_equation_request")

    try:
        matrix_a = matrix_service.parse_matrix(payload.matrix_a)
        matrix_b = matrix_service.parse_matrix(payload.matrix_b)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_SOLVE_EQUATION, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_SOLVE_EQUATION, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.solve_matrix_equation(matrix_a, matrix_b, payload.x_side)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_SOLVE_EQUATION, ErrorCode.DIMENSION_MISMATCH, str(exc))
    except matrix_service.SingularMatrixError as exc:
        return _error(request, OperationType.MATRIX_SOLVE_EQUATION, ErrorCode.SINGULAR_MATRIX, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_SOLVE_EQUATION,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/transpose", response_model=MathResponse)
async def matrix_transpose(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_transpose_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_TRANSPOSE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(
            request, OperationType.MATRIX_TRANSPOSE, ErrorCode.COMPLEXITY_LIMIT, str(exc)
        )

    result = matrix_service.transpose(matrix)

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_TRANSPOSE,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/power", response_model=MathResponse)
async def matrix_power(payload: MatrixPowerRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_power_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_POWER, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_POWER, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.power(matrix, payload.exponent)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_POWER, ErrorCode.DIMENSION_MISMATCH, str(exc))
    except matrix_service.SingularMatrixError as exc:
        return _error(request, OperationType.MATRIX_POWER, ErrorCode.SINGULAR_MATRIX, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_POWER,
        request_id=request.state.request_id,
        result_type=ResultType.MATRIX,
        result_data=matrix_service.matrix_to_result_data(result.result_matrix),
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/norm", response_model=MathResponse)
async def matrix_norm(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_norm_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_NORM, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_NORM, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.norm(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_NORM, ErrorCode.DIMENSION_MISMATCH, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_NORM,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        result_text=str(result.value),
        result_latex=sympy.latex(result.value),
        result_approx=float(result.value) if result.value.is_real else None,
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/trace", response_model=MathResponse)
async def matrix_trace(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    log_request_event(request.state.request_id, "matrix_trace_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_TRACE, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_TRACE, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        result = matrix_service.trace(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_TRACE, ErrorCode.DIMENSION_MISMATCH, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_TRACE,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        result_text=str(result.value),
        result_latex=sympy.latex(result.value),
        result_approx=float(result.value) if result.value.is_real else None,
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/rank", response_model=MathResponse)
async def matrix_rank(payload: MatrixSingleRequest, request: Request) -> MathResponse:
    """Módulo L0 — rango expuesto como operación con resultado visible;
    reutiliza Matrix.rank() de SymPy (el mismo cálculo interno de la
    clasificación de sistemas de Fase B, sin tocar esa lógica ni
    duplicarla). allow_symbolic=True para MV-E-08 (rango genérico en a)."""
    log_request_event(request.state.request_id, "matrix_rank_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix, allow_symbolic=True)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_RANK, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_RANK, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    result = matrix_service.rank(matrix)

    # Rank is always an integer (generic rank when symbols present).
    approx = float(result.value) if result.value.is_number else None
    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_RANK,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        result_text=str(result.value),
        result_latex=sympy.latex(result.value),
        result_approx=approx,
        steps=result.steps,
        has_detailed_steps=result.has_detailed_steps,
        warnings=result.warnings,
        duration_ms=_duration_ms(request),
    )


@router.post("/matrix/eigen", response_model=MathResponse)
async def matrix_eigen(payload: MatrixEigenRequest, request: Request) -> MathResponse:
    """Fase 2 — passthrough trivial real (sección 2)."""
    log_request_event(request.state.request_id, "matrix_eigen_request")

    try:
        matrix = matrix_service.parse_matrix(payload.matrix)
    except parsing.ParseSecurityError as exc:
        return _error(request, OperationType.MATRIX_EIGEN, ErrorCode.PARSE_ERROR, str(exc))
    except ComplexityLimitError as exc:
        return _error(request, OperationType.MATRIX_EIGEN, ErrorCode.COMPLEXITY_LIMIT, str(exc))

    try:
        text = matrix_service.eigen(matrix)
    except matrix_service.DimensionMismatchError as exc:
        return _error(request, OperationType.MATRIX_EIGEN, ErrorCode.DIMENSION_MISMATCH, str(exc))

    return MathResponse(
        success=True,
        operation=OperationType.MATRIX_EIGEN,
        request_id=request.state.request_id,
        result_type=ResultType.SCALAR,
        result_text=text,
        result_latex=text,
        steps=[],
        has_detailed_steps=False,
        warnings=[],
        duration_ms=_duration_ms(request),
    )
