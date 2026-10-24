"""
app/services/matrix_service.py — `/matrix/operations` (spec, secciones 3,
5, 8.6, `MatrixOperationRequest`).

Parser de celda RESTRINGIDO (sección 3), deliberadamente separado del
parser general de `parsing.py`: reutiliza `parsing.parse_expression_tree`
para heredar todas las garantías de seguridad (inyección, límites de
complejidad, etc.) y le aplica encima las restricciones ADICIONALES
específicas de una celda de matriz — sin variables libres, sin funciones
trigonométricas, sin ninguna función que no sea `sqrt`/`abs`.

IMPORTANTE (Módulo 7A, igual que en `/solve`): los pasos se verifican con
`verify_matrix_step_equivalence`, NUNCA con la función escalar — se
comparan matrices completas, celda a celda.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import List, Optional, Tuple

import sympy

from app.core.config import get_settings
from app.schemas.responses import MatrixOpKind, Step
from app.services import parsing
from app.services.step_verification import verify_matrix_step_equivalence

MAX_STEP_MATRIX_SIZE = 4  # hasta 4x4: paso por celda. 5x5/6x6: resultado directo.
ROW_OP_STEP_BUDGET = 30
_TIME_BUDGET_FRACTION = 0.8  # fracción de MATH_TIMEOUT_SECONDS (sección 6)

# Todo lo permitido por ALLOWED_FUNCTIONS (parsing.py) EXCEPTO sqrt/abs está
# prohibido en una celda de matriz (sección 3: "sqrt/abs aplicadas
# únicamente a argumentos numéricos puros"; cualquier otra función,
# incluida cualquier trigonométrica, se rechaza).
_DISALLOWED_CELL_FUNCTION_NAMES = {
    name for name in parsing.ALLOWED_FUNCTIONS if name not in ("sqrt", "abs")
}
_DISALLOWED_CELL_FUNCTION_CLASSES = tuple(
    parsing.ALLOWED_FUNCTIONS[name]
    for name in _DISALLOWED_CELL_FUNCTION_NAMES
    if isinstance(parsing.ALLOWED_FUNCTIONS[name], type)
)

# `/matrix/determinant` es la única operación que admite entradas simbólicas
# (MV-B-16..20): variables libres y trigonométricas elementales. El resto de
# `/matrix/*` conserva el contrato numérico estricto de la sección 3. La
# lista es deliberadamente mínima: no se abre el catálogo completo del parser
# general dentro de una celda.
_SYMBOLIC_CELL_ALLOWED_FUNCTION_NAMES = {"sqrt", "abs", "sin", "cos", "tan"}
_SYMBOLIC_CELL_ALLOWED_FUNCTION_CLASSES = tuple(
    parsing.ALLOWED_FUNCTIONS[name]
    for name in _SYMBOLIC_CELL_ALLOWED_FUNCTION_NAMES
    if isinstance(parsing.ALLOWED_FUNCTIONS[name], type)
)


class DimensionMismatchError(ValueError):
    """Dimensiones incompatibles (sección 5) -> `ErrorCode.DIMENSION_MISMATCH`."""


class SingularMatrixError(ValueError):
    """Inversa de matriz singular -> `ErrorCode.SINGULAR_MATRIX`."""


class UnsupportedOperationError(ValueError):
    """Operación fuera de los límites acotados -> `ErrorCode.UNSUPPORTED_OPERATION`."""


SYMBOLIC_MATRIX_LIMIT = 4


@dataclass
class ScalarStepResult:
    value: sympy.Expr
    steps: List[Step]
    has_detailed_steps: bool
    warnings: List[str]


@dataclass
class MatrixStepResult:
    result_matrix: sympy.Matrix
    steps: List[Step]
    has_detailed_steps: bool
    warnings: List[str]


@dataclass
class MatrixOperationResult:
    result_matrix: sympy.Matrix
    steps: List[Step]
    has_detailed_steps: bool
    warnings: List[str]


@dataclass
class LUDecompositionResult:
    lower: sympy.Matrix
    upper: sympy.Matrix
    steps: List[Step]
    has_detailed_steps: bool
    warnings: List[str]


def _floats_to_rational(expr: sympy.Expr) -> sympy.Expr:
    """`sympy.Rational` siempre (sección 8.6) — cualquier `Float` que haya
    sobrevivido al parseo (ej. `0.75`, válido por la etapa 4 del parser
    general) se convierte a su Rational exacto."""
    float_atoms = expr.atoms(sympy.Float)
    if not float_atoms:
        return expr
    replacements = {f: sympy.nsimplify(f, rational=True) for f in float_atoms}
    return expr.xreplace(replacements)


def _parse_matrix_cell(text: str, *, allow_symbolic: bool = False) -> sympy.Expr:
    """Parser restringido de celda (sección 3). Reutiliza el parser general
    (mismas garantías de seguridad) y añade las restricciones propias de
    una celda. Con `allow_symbolic=True` (solo determinante) se admiten
    variables libres y trigonométricas elementales, necesarias para
    determinantes simbólicos; el resto de funciones sigue rechazado.
    """
    expr = parsing.parse_expression_tree(text, allow_equation=False)

    if not allow_symbolic and expr.free_symbols:
        free_names = sorted(s.name for s in expr.free_symbols)
        raise parsing.ParseSecurityError(
            f"Celda de matriz inválida: no se permiten variables libres ({free_names})."
        )

    for node in sympy.preorder_traversal(expr):
        if not isinstance(node, _DISALLOWED_CELL_FUNCTION_CLASSES):
            continue
        if allow_symbolic and isinstance(node, _SYMBOLIC_CELL_ALLOWED_FUNCTION_CLASSES):
            continue
        raise parsing.ParseSecurityError(
            f"Celda de matriz inválida: función no permitida '{type(node).__name__}' "
            "(solo se permiten sqrt/abs sobre argumentos numéricos puros)."
        )

    # El parser general usa evaluate=False deliberadamente (preserva la
    # estructura de la expresión para otros endpoints) — para una celda de
    # matriz sí queremos el valor totalmente colapsado (ej. "1/2" debe
    # quedar como el objeto Rational real, no como Mul(1, Pow(2,-1))
    # sin evaluar), así que se fuerza aquí con sympy.simplify().
    expr = sympy.simplify(expr)

    return _floats_to_rational(expr)


def parse_matrix(cells: List[List[str]], *, allow_symbolic: bool = False) -> sympy.Matrix:
    if not cells or all(not row for row in cells):
        raise parsing.ParseSecurityError("La matriz no puede estar vacía.")
    if not cells[0] or any(len(row) != len(cells[0]) for row in cells):
        raise parsing.ParseSecurityError("Todas las filas de la matriz deben tener la misma longitud y al menos una celda.")
    rows = [
        [_parse_matrix_cell(cell, allow_symbolic=allow_symbolic) for cell in row]
        for row in cells
    ]
    return sympy.Matrix(rows)


def _cell_steps_add_subtract(
    matrix_a: sympy.Matrix, matrix_b: sympy.Matrix, operation: MatrixOpKind
) -> List[Step]:
    sign = "+" if operation == MatrixOpKind.ADD else "-"
    steps = []
    for row in range(matrix_a.rows):
        for col in range(matrix_a.cols):
            a_val, b_val = matrix_a[row, col], matrix_b[row, col]
            result = a_val + b_val if operation == MatrixOpKind.ADD else a_val - b_val
            steps.append(
                Step(
                    index=0,
                    title=f"Celda ({row + 1},{col + 1})",
                    description=(
                        f"a[{row + 1},{col + 1}] {sign} b[{row + 1},{col + 1}] = "
                        f"{sympy.latex(a_val)} {sign} {sympy.latex(b_val)}."
                    ),
                    rule="MatrixAddSubtract",
                    latex_before=f"{sympy.latex(a_val)} {sign} {sympy.latex(b_val)}",
                    latex_after=sympy.latex(result),
                )
            )
    return steps


def _cell_steps_multiply(matrix_a: sympy.Matrix, matrix_b: sympy.Matrix) -> List[Step]:
    steps = []
    for row in range(matrix_a.rows):
        for col in range(matrix_b.cols):
            terms = [matrix_a[row, k] * matrix_b[k, col] for k in range(matrix_a.cols)]
            result = sum(terms)
            terms_latex = " + ".join(sympy.latex(term) for term in terms)
            steps.append(
                Step(
                    index=0,
                    title=f"Celda ({row + 1},{col + 1})",
                    description=(f"Producto punto: fila {row + 1} de A · columna {col + 1} de B."),
                    rule="MatrixMultiply",
                    latex_before=terms_latex,
                    latex_after=sympy.latex(result),
                )
            )
    return steps


def add_or_subtract(
    matrix_a: sympy.Matrix, matrix_b: sympy.Matrix, operation: MatrixOpKind
) -> MatrixOperationResult:
    if matrix_a.shape != matrix_b.shape:
        raise DimensionMismatchError(
            f"Suma/resta requiere las mismas dimensiones: A es {matrix_a.shape}, "
            f"B es {matrix_b.shape}."
        )

    result_matrix = matrix_a + matrix_b if operation == MatrixOpKind.ADD else matrix_a - matrix_b

    if max(matrix_a.rows, matrix_a.cols) > MAX_STEP_MATRIX_SIZE:
        return MatrixOperationResult(result_matrix, [], False, [])

    before_matrix = sympy.Matrix(
        matrix_a.rows,
        matrix_a.cols,
        lambda i, j: (
            matrix_a[i, j] + matrix_b[i, j]
            if operation == MatrixOpKind.ADD
            else matrix_a[i, j] - matrix_b[i, j]
        ),
    )
    verification = verify_matrix_step_equivalence(
        before_matrix, result_matrix, "suma/resta elemento a elemento"
    )
    if verification != "VERIFIED":
        return MatrixOperationResult(result_matrix, [], False, [])

    steps = _cell_steps_add_subtract(matrix_a, matrix_b, operation)
    for index, step in enumerate(steps):
        step.index = index
    return MatrixOperationResult(result_matrix, steps, True, [])


def multiply(matrix_a: sympy.Matrix, matrix_b: sympy.Matrix) -> MatrixOperationResult:
    if matrix_a.cols != matrix_b.rows:
        raise DimensionMismatchError(
            f"Multiplicación requiere columnas(A) == filas(B): A es {matrix_a.shape}, "
            f"B es {matrix_b.shape}."
        )

    result_matrix = matrix_a * matrix_b

    if max(matrix_a.rows, matrix_a.cols, matrix_b.rows, matrix_b.cols) > MAX_STEP_MATRIX_SIZE:
        return MatrixOperationResult(result_matrix, [], False, [])

    before_matrix = sympy.Matrix(
        matrix_a.rows,
        matrix_b.cols,
        lambda i, j: sum(matrix_a[i, k] * matrix_b[k, j] for k in range(matrix_a.cols)),
    )
    verification = verify_matrix_step_equivalence(
        before_matrix, result_matrix, "multiplicación fila×columna"
    )
    if verification != "VERIFIED":
        return MatrixOperationResult(result_matrix, [], False, [])

    steps = _cell_steps_multiply(matrix_a, matrix_b)
    for index, step in enumerate(steps):
        step.index = index
    return MatrixOperationResult(result_matrix, steps, True, [])


def matrix_to_result_data(matrix: sympy.Matrix) -> List[List[str]]:
    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def transpose(matrix: sympy.Matrix) -> MatrixOperationResult:
    """`/matrix/transpose` — passthrough trivial (`Matrix.T`), sin pasos
    detallados (no hay una secuencia de transformaciones intermedias que
    narrar: es una única reindexación de celdas), igual patrón que
    `/matrix/eigen` (Fase 2, sección 2)."""
    return MatrixOperationResult(matrix.T, [], False, [])


MAX_MATRIX_POWER_EXPONENT = 32


def power(matrix: sympy.Matrix, exponent: int) -> MatrixOperationResult:
    """`/matrix/power` — `Matrix ** exponent`. Requiere matriz cuadrada;
    exponente negativo requiere matriz invertible (usa `Matrix.inv()`
    internamente vía SymPy). Sin pasos detallados, mismo patrón que
    `eigen`/`transpose`."""
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"La potencia de una matriz requiere una matriz cuadrada; recibida {matrix.shape}."
        )
    if abs(exponent) > MAX_MATRIX_POWER_EXPONENT:
        raise DimensionMismatchError(
            f"Exponente fuera de rango permitido (máximo ±{MAX_MATRIX_POWER_EXPONENT})."
        )
    if exponent < 0 and matrix.det() == 0:
        raise SingularMatrixError(
            "La matriz es singular (determinante 0); no tiene inversa para potencia negativa."
        )
    if exponent == 0:
        result_matrix = sympy.eye(matrix.rows)
    else:
        result_matrix = matrix**exponent
    return MatrixOperationResult(result_matrix, [], False, [])


def eigen(matrix: sympy.Matrix) -> str:
    """`/matrix/eigen` (Fase 2, sección 2: "Sí — passthrough trivial —
    `Matrix.eigenvals()`/`eigenvects()`"). Resultado directo de SymPy, sin
    pasos (`has_detailed_steps: false`) — no hay un campo de contrato
    dedicado a eigenvalores/eigenvectores en `MathResponse.result_data`
    (que solo admite soluciones de ecuación o matrices), así que se
    presenta como texto/LaTeX (decisión DEDUCIBLE, documentada en el
    cierre del Módulo 9)."""
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"Los eigenvalores requieren una matriz cuadrada; recibida {matrix.shape}."
        )
    eigenvects = matrix.eigenvects()
    parts = []
    for eigenvalue, multiplicity, vectors in eigenvects:
        vectors_str = ", ".join(str(v.T) for v in vectors)
        parts.append(
            f"λ={eigenvalue} (multiplicidad {multiplicity}), autovectores: [{vectors_str}]"
        )
    return "; ".join(parts)


# ---------------------------------------------------------------------------
# Determinante e inversa (Módulo 7B) — eliminación por filas con pivoteo.
#
# IMPORTANTE (verificación, sección 8.6 y decisión DEDUCIBLE documentada en
# el cierre del Módulo 7B): a diferencia de suma/resta/multiplicación (donde
# "antes"/"después" son dos representaciones de la MISMA celda resultante),
# una operación elemental de fila transforma la matriz DELIBERADAMENTE en
# otra distinta — comparar "antes" vs "después" celda a celda con
# `verify_matrix_step_equivalence` no tiene el mismo sentido ahí (casi
# siempre darían REJECTED, ya que se espera que cambien). En su lugar, cada
# operación de fila se traza como narrativa (siempre matemáticamente
# correcta por construcción: son operaciones elementales estándar), y se
# hace UNA verificación holística al final con `verify_matrix_step_equivalence`
# — igual que en Módulos 4-7A — comparando el resultado ENSAMBLADO contra
# la verdad de referencia de SymPy:
#   - Determinante: se envuelve el escalar en una matriz 1x1 (cumple la
#     letra de "verify_matrix_step_equivalence, no la escalar" aunque el
#     resultado sea conceptualmente un número).
#   - Inversa: comparación directa matriz-contra-matriz (A⁻¹ propia vs.
#     `matrix.inv()` de SymPy) — aplicación natural, sin envolver nada.
# ---------------------------------------------------------------------------


def _time_budget_seconds() -> float:
    return get_settings().math_timeout_seconds * _TIME_BUDGET_FRACTION


def _determinant_row_reduction(
    matrix: sympy.Matrix,
) -> Optional[Tuple[List[Step], sympy.Expr]]:
    """Elimina por debajo de la diagonal con pivoteo parcial, registrando
    cada operación elemental como `Step`. Devuelve `None` si se excede el
    presupuesto de pasos/tiempo (el llamador colapsa a `Matrix.det()`)."""
    start_time = perf_counter()
    n = matrix.rows
    working = matrix.copy()
    sign = sympy.Integer(1)
    steps: List[Step] = []

    for col in range(n):
        if len(steps) > ROW_OP_STEP_BUDGET or (perf_counter() - start_time) > (
            _time_budget_seconds()
        ):
            return None

        pivot_row = next((r for r in range(col, n) if working[r, col] != 0), None)
        if pivot_row is None:
            steps.append(
                Step(
                    index=0,
                    title=f"Columna {col + 1} nula bajo la diagonal",
                    description="Toda la columna es cero bajo el pivote -> determinante 0.",
                    rule="ZeroColumn",
                    latex_before=sympy.latex(working),
                    latex_after="0",
                )
            )
            return steps, sympy.Integer(0)

        if pivot_row != col:
            working = working.copy()
            working.row_swap(col, pivot_row)
            sign *= -1
            steps.append(
                Step(
                    index=0,
                    title=f"Intercambiar filas {col + 1} y {pivot_row + 1}",
                    description="Pivoteo parcial: se coloca un pivote no nulo en la diagonal.",
                    rule="RowSwap",
                    latex_before=f"F_{{{col + 1}}} \\leftrightarrow F_{{{pivot_row + 1}}}",
                    latex_after=sympy.latex(working),
                )
            )

        pivot_val = working[col, col]
        for row in range(col + 1, n):
            if len(steps) > ROW_OP_STEP_BUDGET:
                return None
            factor = sympy.simplify(working[row, col] / pivot_val)
            if factor == 0:
                continue
            working = working.copy()
            working[row, :] = working[row, :] - factor * working[col, :]
            steps.append(
                Step(
                    index=0,
                    title=f"F{row + 1} ← F{row + 1} - ({sympy.latex(factor)})·F{col + 1}",
                    description="Eliminación por debajo del pivote.",
                    rule="RowElimination",
                    latex_before=f"F_{{{row + 1}}} - ({sympy.latex(factor)})F_{{{col + 1}}}",
                    latex_after=sympy.latex(working),
                )
            )

    determinant = sign
    for i in range(n):
        determinant *= working[i, i]
    determinant = sympy.simplify(determinant)
    return steps, determinant


def determinant(matrix: sympy.Matrix) -> ScalarStepResult:
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"El determinante requiere una matriz cuadrada; recibida {matrix.shape}."
        )

    reference = sympy.simplify(matrix.det())

    # MV-B-16..20: entradas simbólicas. La eliminación por filas con pivotes
    # simbólicos no es válida sin supuestos (un pivote podría anularse para
    # ciertos valores del parámetro), así que se devuelve la verdad directa
    # de SymPy sin narrativa de pasos — mismo patrón que las matrices >4×4.
    # `trigsimp` colapsa sin²+cos²; `factor` presenta la forma factorizada
    # cuando el resultado es polinómico (Vandermonde, autovalores).
    if any(expr.free_symbols for expr in matrix):
        value = sympy.simplify(sympy.trigsimp(reference))
        if value.is_polynomial():
            value = sympy.factor(value)
        return ScalarStepResult(value, [], False, [])

    if max(matrix.rows, matrix.cols) > MAX_STEP_MATRIX_SIZE:
        return ScalarStepResult(reference, [], False, [])

    reduction = _determinant_row_reduction(matrix)
    if reduction is None:
        return ScalarStepResult(
            reference,
            [],
            False,
            ["Procedimiento detallado omitido: tiempo de verificación excedido " "(sección 6)."],
        )

    steps, computed_value = reduction
    verification = verify_matrix_step_equivalence(
        sympy.Matrix([[computed_value]]),
        sympy.Matrix([[reference]]),
        "determinante por eliminación de filas",
    )
    if verification != "VERIFIED":
        return ScalarStepResult(reference, [], False, [])

    for index, step in enumerate(steps):
        step.index = index
    return ScalarStepResult(computed_value, steps, True, [])


def _inverse_row_reduction(
    matrix: sympy.Matrix,
) -> Optional[Tuple[List[Step], sympy.Matrix]]:
    """Gauss-Jordan explícito sobre `[A|I] -> [I|A⁻¹]`. Devuelve `None` si
    se excede el presupuesto de pasos/tiempo."""
    start_time = perf_counter()
    n = matrix.rows
    augmented = matrix.row_join(sympy.eye(n))
    steps: List[Step] = []

    for col in range(n):
        if len(steps) > ROW_OP_STEP_BUDGET or (perf_counter() - start_time) > (
            _time_budget_seconds()
        ):
            return None

        pivot_row = next((r for r in range(col, n) if augmented[r, col] != 0), None)
        if pivot_row is None:
            return None  # singular — no debería ocurrir (ya validado antes)

        if pivot_row != col:
            augmented = augmented.copy()
            augmented.row_swap(col, pivot_row)
            steps.append(
                Step(
                    index=0,
                    title=f"Intercambiar filas {col + 1} y {pivot_row + 1}",
                    description="Pivoteo parcial sobre la matriz aumentada [A|I].",
                    rule="RowSwap",
                    latex_before=f"F_{{{col + 1}}} \\leftrightarrow F_{{{pivot_row + 1}}}",
                    latex_after=sympy.latex(augmented),
                )
            )

        pivot_val = augmented[col, col]
        if pivot_val != 1:
            augmented = augmented.copy()
            augmented[col, :] = augmented[col, :] / pivot_val
            steps.append(
                Step(
                    index=0,
                    title=f"F{col + 1} ← F{col + 1} / ({sympy.latex(pivot_val)})",
                    description="Se normaliza el pivote a 1.",
                    rule="NormalizePivot",
                    latex_before=f"F_{{{col + 1}}} / ({sympy.latex(pivot_val)})",
                    latex_after=sympy.latex(augmented),
                )
            )

        for row in range(n):
            if row == col:
                continue
            if len(steps) > ROW_OP_STEP_BUDGET:
                return None
            factor = augmented[row, col]
            if factor == 0:
                continue
            augmented = augmented.copy()
            augmented[row, :] = augmented[row, :] - factor * augmented[col, :]
            steps.append(
                Step(
                    index=0,
                    title=f"F{row + 1} ← F{row + 1} - ({sympy.latex(factor)})·F{col + 1}",
                    description="Eliminación en la columna del pivote (Gauss-Jordan).",
                    rule="RowElimination",
                    latex_before=f"F_{{{row + 1}}} - ({sympy.latex(factor)})F_{{{col + 1}}}",
                    latex_after=sympy.latex(augmented),
                )
            )

    inverse_matrix = augmented[:, n:]
    return steps, inverse_matrix


def inverse(matrix: sympy.Matrix) -> MatrixStepResult:
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"La inversa requiere una matriz cuadrada; recibida {matrix.shape}."
        )

    determinant_value = sympy.simplify(matrix.det())
    if determinant_value == 0:
        raise SingularMatrixError("La matriz es singular (determinante 0); no tiene inversa.")

    symbolic = any(expr.free_symbols or expr.has(sympy.I) for expr in matrix)
    if symbolic and max(matrix.rows, matrix.cols) > SYMBOLIC_MATRIX_LIMIT:
        raise UnsupportedOperationError(
            "La inversa simbólica está limitada a 4×4."
        )

    reference = matrix.inv()

    # MV-C-08/10/11: celdas complejas o simb��licas. La eliminaci��n por
    # filas con pivotes simb��licos no es v��lida sin supuestos (un pivote
    # podr��a anularse para ciertos valores); se devuelve la verdad directa
    # de SymPy, simplificada con trigsimp. Sin pasos detallados, mismo
    # criterio que el determinante simb��lico.
    if symbolic:
        simplified = reference.applyfunc(lambda e: sympy.simplify(sympy.trigsimp(e)))
        return MatrixStepResult(simplified, [], False, [])

    if max(matrix.rows, matrix.cols) > MAX_STEP_MATRIX_SIZE:
        return MatrixStepResult(reference, [], False, [])

    reduction = _inverse_row_reduction(matrix)
    if reduction is None:
        return MatrixStepResult(
            reference,
            [],
            False,
            ["Procedimiento detallado omitido: tiempo de verificación excedido " "(sección 6)."],
        )

    steps, computed_inverse = reduction
    verification = verify_matrix_step_equivalence(
        computed_inverse, reference, "inversa por Gauss-Jordan"
    )
    if verification != "VERIFIED":
        return MatrixStepResult(reference, [], False, [])

    for index, step in enumerate(steps):
        step.index = index
    return MatrixStepResult(computed_inverse, steps, True, [])


def _symbolic_simplify_matrix(matrix: sympy.Matrix) -> sympy.Matrix:
    return matrix.applyfunc(lambda expr: sympy.simplify(sympy.trigsimp(expr)))


def adjugate(matrix: sympy.Matrix) -> MatrixStepResult:
    """MV-C-14/15: adjunta = transpuesta de la matriz de cofactores."""
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"La adjunta requiere una matriz cuadrada; recibida {matrix.shape}."
        )
    return MatrixStepResult(_symbolic_simplify_matrix(matrix.adjugate()), [], False, [])


def cofactor_matrix(matrix: sympy.Matrix) -> MatrixStepResult:
    """MV-C-16: matriz de cofactores (la adjunta es su transpuesta)."""
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"La matriz de cofactores requiere una matriz cuadrada; recibida {matrix.shape}."
        )
    return MatrixStepResult(_symbolic_simplify_matrix(matrix.adjugate().T), [], False, [])


def solve_matrix_equation(
    matrix_a: sympy.Matrix, matrix_b: sympy.Matrix, x_side: str
) -> MatrixOperationResult:
    """MV-C-18/19: resuelve X��A = B o A��X = B.

    ``x_side="left"`` significa que X aparece a la izquierda (X��A = B),
    por lo que X = B��A^{-1}. ``x_side="right"`` significa A��X = B, por lo
    que X = A^{-1}��B. El orden se conserva deliberadamente: la inversa no
    conmuta.
    """
    if matrix_a.rows != matrix_a.cols:
        raise DimensionMismatchError(
            f"La ecuaci��n matricial requiere una matriz A cuadrada; recibida {matrix_a.shape}."
        )
    if sympy.simplify(matrix_a.det()) == 0:
        raise SingularMatrixError(
            "La matriz A es singular (determinante 0); la ecuaci��n no tiene soluci��n ��nica."
        )

    if x_side == "left":
        if matrix_b.cols != matrix_a.rows:
            raise DimensionMismatchError(
                f"X��A = B requiere columnas(B) == filas(A): A es {matrix_a.shape}, "
                f"B es {matrix_b.shape}."
            )
        result = matrix_b * matrix_a.inv()
    elif x_side == "right":
        if matrix_b.rows != matrix_a.rows:
            raise DimensionMismatchError(
                f"A��X = B requiere filas(B) == filas(A): A es {matrix_a.shape}, "
                f"B es {matrix_b.shape}."
            )
        result = matrix_a.inv() * matrix_b
    else:
        raise DimensionMismatchError("x_side debe ser 'left' o 'right'.")

    return MatrixOperationResult(_symbolic_simplify_matrix(result), [], False, [])


# ---------------------------------------------------------------------------
# Fase C (spec UX estilo ClassCalc, sección 4) — agregadas sobre las
# operaciones de la spec v9 original. Mismo patrón que las demás: pasos
# explícitos verificados contra la referencia de SymPy, con fallback sin
# pasos si se excede el presupuesto o falla la verificación.
# ---------------------------------------------------------------------------


def _ref_row_reduction(matrix: sympy.Matrix) -> Optional[Tuple[List[Step], sympy.Matrix]]:
    """Eliminación hacia adelante únicamente (sin normalizar pivotes a 1 ni
    eliminar hacia arriba) — forma escalonada, no reducida."""
    start_time = perf_counter()
    rows, cols = matrix.rows, matrix.cols
    working = matrix.copy()
    steps: List[Step] = []
    pivot_row = 0

    for col in range(cols):
        if pivot_row >= rows:
            break
        if len(steps) > ROW_OP_STEP_BUDGET or (perf_counter() - start_time) > (
            _time_budget_seconds()
        ):
            return None

        sel = next((r for r in range(pivot_row, rows) if working[r, col] != 0), None)
        if sel is None:
            continue

        if sel != pivot_row:
            working = working.copy()
            working.row_swap(pivot_row, sel)
            steps.append(
                Step(
                    index=0,
                    title=f"Intercambiar filas {pivot_row + 1} y {sel + 1}",
                    description="Se coloca un pivote no nulo en la fila actual.",
                    rule="RowSwap",
                    latex_before=f"F_{{{pivot_row + 1}}} \\leftrightarrow F_{{{sel + 1}}}",
                    latex_after=sympy.latex(working),
                )
            )

        pivot_val = working[pivot_row, col]
        for row in range(pivot_row + 1, rows):
            if len(steps) > ROW_OP_STEP_BUDGET:
                return None
            factor = sympy.simplify(working[row, col] / pivot_val)
            if factor == 0:
                continue
            working = working.copy()
            working[row, :] = working[row, :] - factor * working[pivot_row, :]
            steps.append(
                Step(
                    index=0,
                    title=f"F{row + 1} ← F{row + 1} - ({sympy.latex(factor)})·F{pivot_row + 1}",
                    description=f"Eliminación en la columna {col + 1} bajo el pivote.",
                    rule="RowElimination",
                    latex_before=f"F_{{{row + 1}}} - ({sympy.latex(factor)})F_{{{pivot_row + 1}}}",
                    latex_after=sympy.latex(working),
                )
            )
        pivot_row += 1

    return steps, working


def ref(matrix: sympy.Matrix) -> MatrixStepResult:
    """Forma escalonada (ref) — `Matrix.echelon_form()` es la referencia."""
    reference = matrix.echelon_form()

    if max(matrix.rows, matrix.cols) > MAX_STEP_MATRIX_SIZE:
        return MatrixStepResult(reference, [], False, [])

    reduction = _ref_row_reduction(matrix)
    if reduction is None:
        return MatrixStepResult(
            reference, [], False, ["Procedimiento detallado omitido: tiempo de verificación excedido (sección 6)."]
        )

    steps, computed = reduction
    # echelon_form() de SymPy no siempre coincide fila a fila con una
    # eliminación "de libro de texto" (puede reordenar/escalar distinto,
    # ambas son ref válidas de la misma matriz) — se verifica igualdad de
    # RANGO y de posiciones de pivote, no igualdad exacta celda a celda
    # como si hace rref (que sí es única).
    if computed.rank() != reference.rank():
        return MatrixStepResult(reference, [], False, [])

    for index, step in enumerate(steps):
        step.index = index
    return MatrixStepResult(computed, steps, True, [])


def rref(matrix: sympy.Matrix) -> MatrixStepResult:
    """Forma escalonada reducida (rref) — única, se verifica celda a celda
    contra `Matrix.rref()` igual que el resto de las operaciones."""
    reference, _pivots = matrix.rref()

    if max(matrix.rows, matrix.cols) > MAX_STEP_MATRIX_SIZE:
        return MatrixStepResult(reference, [], False, [])

    ref_reduction = _ref_row_reduction(matrix)
    if ref_reduction is None:
        return MatrixStepResult(
            reference, [], False, ["Procedimiento detallado omitido: tiempo de verificación excedido (sección 6)."]
        )
    steps, working = ref_reduction

    start_time = perf_counter()
    rows, cols = working.rows, working.cols
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= rows:
            break
        if working[pivot_row, col] == 0:
            continue
        if len(steps) > ROW_OP_STEP_BUDGET or (perf_counter() - start_time) > (
            _time_budget_seconds()
        ):
            return MatrixStepResult(
                reference, [], False, ["Procedimiento detallado omitido: tiempo de verificación excedido (sección 6)."]
            )
        pivot_val = working[pivot_row, col]
        if pivot_val != 1:
            working = working.copy()
            working[pivot_row, :] = working[pivot_row, :] / pivot_val
            steps.append(
                Step(
                    index=0,
                    title=f"F{pivot_row + 1} ← F{pivot_row + 1} / ({sympy.latex(pivot_val)})",
                    description="Se normaliza el pivote a 1.",
                    rule="NormalizePivot",
                    latex_before=f"F_{{{pivot_row + 1}}} / ({sympy.latex(pivot_val)})",
                    latex_after=sympy.latex(working),
                )
            )
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = working[row, col]
            if factor == 0:
                continue
            working = working.copy()
            working[row, :] = working[row, :] - factor * working[pivot_row, :]
            steps.append(
                Step(
                    index=0,
                    title=f"F{row + 1} ← F{row + 1} - ({sympy.latex(factor)})·F{pivot_row + 1}",
                    description=f"Eliminación en la columna {col + 1} fuera del pivote.",
                    rule="RowElimination",
                    latex_before=f"F_{{{row + 1}}} - ({sympy.latex(factor)})F_{{{pivot_row + 1}}}",
                    latex_after=sympy.latex(working),
                )
            )
        pivot_row += 1

    verification = verify_matrix_step_equivalence(working, reference, "forma escalonada reducida (rref)")
    if verification != "VERIFIED":
        return MatrixStepResult(reference, [], False, [])

    for index, step in enumerate(steps):
        step.index = index
    return MatrixStepResult(working, steps, True, [])


def lu_decomposition(matrix: sympy.Matrix) -> LUDecompositionResult:
    """Descomposición A = L·U por eliminación de Doolittle SIN pivoteo.

    No se simula pivoteo: si aparece un pivote nulo se devuelve un error
    explícito. La factorización se verifica exactamente antes de publicarse.
    """
    rows, cols = matrix.rows, matrix.cols
    lower = sympy.eye(rows)
    upper = sympy.zeros(rows, cols)
    working = matrix.copy()
    limit = min(rows, cols)

    for pivot_index in range(limit):
        pivot = working[pivot_index, pivot_index]
        if pivot == 0:
            raise UnsupportedOperationError(
                "LU sin pivoteo no es posible: el pivote en la posición "
                f"({pivot_index + 1},{pivot_index + 1}) es 0. Se requiere "
                "intercambio de filas (pivoteo), que esta operación no realiza."
            )
        for col in range(pivot_index, cols):
            upper[pivot_index, col] = working[pivot_index, col]
        for row in range(pivot_index + 1, rows):
            factor = sympy.simplify(working[row, pivot_index] / pivot)
            lower[row, pivot_index] = factor
            if factor == 0:
                continue
            for col in range(pivot_index, cols):
                working[row, col] = sympy.simplify(
                    working[row, col] - factor * working[pivot_index, col]
                )

    if lower * upper != matrix:
        raise UnsupportedOperationError(
            "No se pudo verificar la descomposición LU de esta matriz."
        )

    return LUDecompositionResult(lower, upper, [], False, [])


def gram_schmidt(matrix: sympy.Matrix) -> MatrixOperationResult:
    """Gram-Schmidt SIN normalizar, tomando cada FILA como vector de entrada.

    Devuelve una matriz cuyas filas son los vectores ortogonales en el mismo
    orden. No se divide por la norma: solo se restan proyecciones.
    """
    vectors = [list(matrix.row(index)) for index in range(matrix.rows)]
    if not vectors or not vectors[0]:
        raise DimensionMismatchError("Se requiere al menos un vector no vacío.")

    orthogonal: List[List[sympy.Expr]] = []
    for original in vectors:
        current = [sympy.simplify(value) for value in original]
        for basis in orthogonal:
            denominator = sympy.simplify(sum(value * value for value in basis))
            if denominator == 0:
                continue
            numerator = sympy.simplify(
                sum(value * basis_value for value, basis_value in zip(original, basis))
            )
            factor = sympy.simplify(numerator / denominator)
            if factor == 0:
                continue
            current = [
                sympy.simplify(value - factor * basis_value)
                for value, basis_value in zip(current, basis)
            ]
        orthogonal.append(current)

    # Verificación exacta de ortogonalidad mutua.
    for index, first in enumerate(orthogonal):
        for second in orthogonal[index + 1 :]:
            if sympy.simplify(sum(a * b for a, b in zip(first, second))) != 0:
                raise UnsupportedOperationError(
                    "No se pudo verificar la ortogonalidad del resultado de Gram-Schmidt."
                )

    return MatrixOperationResult(sympy.Matrix(orthogonal), [], False, [])


def kronecker(matrix_a: sympy.Matrix, matrix_b: sympy.Matrix) -> MatrixOperationResult:
    """Producto de Kronecker A⊗B. Sin restricción de dimensiones (a
    diferencia de suma/multiplicación) — siempre definido."""
    from sympy.matrices.expressions.kronecker import KroneckerProduct

    result_matrix = KroneckerProduct(matrix_a, matrix_b).as_explicit()

    if max(matrix_a.rows, matrix_a.cols, matrix_b.rows, matrix_b.cols) > MAX_STEP_MATRIX_SIZE:
        return MatrixOperationResult(result_matrix, [], False, [])

    # Un solo paso descriptivo (no celda a celda como add/multiply, sería
    # ilegible con matrices de más de 2x2 dado el tamaño combinado) — la
    # propia construcción vía KroneckerProduct ya es la verificación (no
    # hay una eliminación manual con la que contrastar, a diferencia de
    # ref/rref/inverse/determinant).
    step = Step(
        index=0,
        title="Producto de Kronecker",
        description=(
            f"Cada bloque (i,j) de A se reemplaza por A[i,j]·B, dando una matriz "
            f"de {result_matrix.rows}×{result_matrix.cols}."
        ),
        rule="Kronecker",
        latex_before=f"{sympy.latex(matrix_a)} \\otimes {sympy.latex(matrix_b)}",
        latex_after=sympy.latex(result_matrix),
    )
    return MatrixOperationResult(result_matrix, [step], True, [])


# ---------------------------------------------------------------------------
# P5 (spec v2 §6): Vectores en Matrices — dot/cross/norm. Un vector es una
# matriz 1xn o nx1 (spec explícita: no se crea componente de entrada
# nuevo). A diferencia del equivalente en precision-lab-lite (que usa
# Fraction.js y por eso `norm` requiere una excepción documentada a su
# regla de aritmética exacta), aquí `sympy.sqrt(...)` representa la raíz
# de forma simbólica exacta sin ningún caso especial — mismo patrón que
# ya usa `determinant` para exponer el valor exacto (`result_text`/
# `result_latex`) junto con su aproximación decimal (`result_approx`).
# ---------------------------------------------------------------------------


def _as_vector(matrix: sympy.Matrix) -> List[sympy.Expr]:
    if matrix.rows == 1:
        return list(matrix.row(0))
    if matrix.cols == 1:
        return list(matrix.col(0))
    raise DimensionMismatchError(
        f"Se esperaba un vector (1 fila o 1 columna); recibida una matriz de {matrix.shape}."
    )


def dot(matrix_a: sympy.Matrix, matrix_b: sympy.Matrix) -> ScalarStepResult:
    va = _as_vector(matrix_a)
    vb = _as_vector(matrix_b)
    if len(va) != len(vb):
        raise DimensionMismatchError(
            f"Producto punto requiere vectores de la misma longitud: A tiene {len(va)}, "
            f"B tiene {len(vb)}."
        )
    value = sympy.simplify(sum(a * b for a, b in zip(va, vb)))
    step = Step(
        index=0,
        title="Producto punto",
        description="Suma de los productos componente a componente.",
        rule="DotProduct",
        latex_before=" + ".join(f"({sympy.latex(a)})({sympy.latex(b)})" for a, b in zip(va, vb)),
        latex_after=sympy.latex(value),
    )
    return ScalarStepResult(value, [step], True, [])


def cross(matrix_a: sympy.Matrix, matrix_b: sympy.Matrix) -> MatrixOperationResult:
    """Válido únicamente para vectores de 3 componentes (spec v2 §6) —
    dimensión inválida reutiliza `DimensionMismatchError`/
    `ErrorCode.DIMENSION_MISMATCH` ya existente, no se inventa un código
    de error nuevo."""
    va = _as_vector(matrix_a)
    vb = _as_vector(matrix_b)
    if len(va) != 3 or len(vb) != 3:
        raise DimensionMismatchError(
            f"Producto cruz requiere vectores de 3 componentes: A tiene {len(va)}, "
            f"B tiene {len(vb)}."
        )
    a1, a2, a3 = va
    b1, b2, b3 = vb
    result_matrix = sympy.Matrix([[a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1]])
    step = Step(
        index=0,
        title="Producto cruz",
        description="Producto cruz A×B (solo definido en 3 dimensiones).",
        rule="CrossProduct",
        latex_before=f"{sympy.latex(matrix_a)} \\times {sympy.latex(matrix_b)}",
        latex_after=sympy.latex(result_matrix),
    )
    return MatrixOperationResult(result_matrix, [step], True, [])


def norm(matrix: sympy.Matrix) -> ScalarStepResult:
    """Magnitud/norma euclidiana. No requiere matriz B (como transpose/
    determinant/inverse)."""
    v = _as_vector(matrix)
    sum_squares = sympy.simplify(sum(x**2 for x in v))
    value = sympy.sqrt(sum_squares)
    steps = [
        Step(
            index=0,
            title="Suma de cuadrados",
            description="Suma de los cuadrados de cada componente.",
            rule="VectorNormSumSquares",
            latex_before=" + ".join(f"({sympy.latex(x)})^2" for x in v),
            latex_after=sympy.latex(sum_squares),
        ),
        Step(
            index=1,
            title="Raíz cuadrada",
            description="Norma = raíz cuadrada de la suma de cuadrados.",
            rule="VectorNormSqrt",
            latex_before=f"\\sqrt{{{sympy.latex(sum_squares)}}}",
            latex_after=sympy.latex(value),
        ),
    ]
    return ScalarStepResult(value, steps, True, [])


def trace(matrix: sympy.Matrix) -> ScalarStepResult:
    """Módulo L0 (spec_graficacion_matrices_estadistica_unidades.md,
    sección 5): traza — suma de la diagonal principal. Cálculo trivial,
    sin dependencias nuevas; mismo patrón ScalarStepResult que
    determinant/norm/dot, no un tipo de resultado nuevo."""
    if matrix.rows != matrix.cols:
        raise DimensionMismatchError(
            f"La traza solo está definida para matrices cuadradas; recibida {matrix.shape}."
        )
    diagonal = [matrix[i, i] for i in range(matrix.rows)]
    value = sympy.simplify(sum(diagonal))
    step = Step(
        index=0,
        title="Traza",
        description="Suma de los elementos de la diagonal principal.",
        rule="Trace",
        latex_before=" + ".join(sympy.latex(d) for d in diagonal),
        latex_after=sympy.latex(value),
    )
    return ScalarStepResult(value, [step], True, [])


def rank(matrix: sympy.Matrix) -> ScalarStepResult:
    """Módulo L0 (spec_graficacion_matrices_estadistica_unidades.md,
    sección 5): rango, expuesto como operación con resultado visible —
    reutiliza `Matrix.rank()` de SymPy, el mismo cálculo que ya se usa
    internamente en `_verify_...`/clasificación de sistemas (Fase B de
    spec_motor_matematico_pendiente.md), sin duplicar esa lógica ni
    tocarla — este es un wrapper nuevo, no una modificación de la
    existente."""
    value = sympy.Integer(matrix.rank())
    step = Step(
        index=0,
        title="Rango",
        description="Número de filas (o columnas) linealmente independientes — calculado por eliminación gaussiana.",
        rule="Rank",
        latex_before=sympy.latex(matrix),
        latex_after=sympy.latex(value),
    )
    return ScalarStepResult(value, [step], True, [])
