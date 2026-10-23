"""Bases del núcleo y del espacio columna (MV-E).

Separado de matrix_service para no tocar el archivo monolítico de operaciones.
Cada fila del resultado es un vector de la base (misma convención que Gram-Schmidt).
"""
from __future__ import annotations

from typing import List

import sympy

from app.schemas.responses import Step
from app.services.matrix_service import MatrixOperationResult


def nullspace(matrix: sympy.Matrix) -> MatrixOperationResult:
    basis = matrix.nullspace()
    if not basis:
        empty = sympy.Matrix.zeros(0, matrix.cols)
        return MatrixOperationResult(empty, [], False, [])
    rows: List[List[sympy.Expr]] = [list(vector) for vector in basis]
    result = sympy.Matrix(rows)
    steps = [
        Step(
            index=0,
            title="Núcleo",
            description=f"Base del núcleo con {len(rows)} vector(es).",
            rule="Nullspace",
            latex_before=sympy.latex(matrix),
            latex_after=sympy.latex(result.T),
        )
    ]
    return MatrixOperationResult(result, steps, True, [])


def columnspace(matrix: sympy.Matrix) -> MatrixOperationResult:
    basis = matrix.columnspace()
    if not basis:
        empty = sympy.Matrix.zeros(0, matrix.rows)
        return MatrixOperationResult(empty, [], False, [])
    rows: List[List[sympy.Expr]] = [list(vector) for vector in basis]
    result = sympy.Matrix(rows)
    steps = [
        Step(
            index=0,
            title="Espacio columna",
            description=f"Base del espacio columna con {len(rows)} vector(es) (columnas pivote).",
            rule="Columnspace",
            latex_before=sympy.latex(matrix),
            latex_after=sympy.latex(result.T),
        )
    ]
    return MatrixOperationResult(result, steps, True, [])
