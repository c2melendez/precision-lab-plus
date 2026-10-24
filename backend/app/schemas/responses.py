"""
Contratos públicos de respuesta de la API — definidos UNA SOLA VEZ.

Fuente: spec_calculadora_cientifica_v9.md, sección 4.

Regla de proyecto (Mensaje 0, punto 3): estos contratos no se redefinen en
otro archivo. No se eliminan campos públicos existentes, no se renombran, no
se cambia su tipo o semántica sin autorización explícita. Ampliaciones
siempre retrocompatibles.
"""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class OperationType(str, Enum):
    EVALUATE = "evaluate"
    SIMPLIFY = "simplify"
    FACTOR = "factor"
    PARTIAL_FRACTIONS = "partial_fractions"
    EXPAND = "expand"
    SOLVE = "solve"
    DERIVATIVE = "derivative"
    INTEGRAL = "integral"
    MATRIX_OPERATION = "matrix_operation"
    MATRIX_DETERMINANT = "matrix_determinant"
    MATRIX_INVERSE = "matrix_inverse"
    MATRIX_ADJUGATE = "matrix_adjugate"
    MATRIX_COFACTOR = "matrix_cofactor"
    MATRIX_SOLVE_EQUATION = "matrix_solve_equation"
    GRAPH_2D = "graph_2d"
    SOLVE_SYSTEM = "solve_system"
    INEQUALITY = "inequality"
    LIMIT = "limit"
    SERIES = "series"
    MATRIX_EIGEN = "matrix_eigen"
    INTEGRAL_IMPROPER = "integral_improper"
    GRAPH_3D = "graph_3d"
    GRAPH_PARAMETRIC = "graph_parametric"
    DERIVATIVE_PARTIAL = "derivative_partial"
    DERIVATIVE_IMPLICIT = "derivative_implicit"
    MATRIX_TRANSPOSE = "matrix_transpose"
    MATRIX_POWER = "matrix_power"
    MATRIX_REF = "matrix_ref"
    MATRIX_RREF = "matrix_rref"
    MATRIX_LU = "matrix_lu"
    MATRIX_GRAM_SCHMIDT = "matrix_gram_schmidt"
    MATRIX_NORM = "matrix_norm"
    MATRIX_TRACE = "matrix_trace"
    MATRIX_RANK = "matrix_rank"
    MATRIX_NULLSPACE = "matrix_nullspace"
    MATRIX_COLUMNSPACE = "matrix_columnspace"
    STATISTICS_CORRELATION = "statistics_correlation"
    STATISTICS_DESCRIPTIVE = "statistics_descriptive"
    STATISTICS_COMBINATORICS = "statistics_combinatorics"
    STATISTICS_BINOMIAL = "statistics_binomial"
    STATISTICS_NORMAL = "statistics_normal"
    STATISTICS_POISSON = "statistics_poisson"
    STATISTICS_UNIFORM = "statistics_uniform"
    STATISTICS_EXPONENTIAL = "statistics_exponential"
    INEQUALITY_SYSTEM = "inequality_system"
    GRAPH_POLAR = "graph_polar"
    ODE = "ode"
    COMPLEX_RESIDUE = "complex_residue"
    COMPLEX_SINGULARITIES = "complex_singularities"


class MatrixOpKind(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    KRONECKER = "kronecker"
    DOT = "dot"
    CROSS = "cross"


class ResultType(str, Enum):
    SCALAR = "scalar"
    EQUATION_SOLUTIONS = "equation_solutions"
    MATRIX = "matrix"
    BOOLEAN = "boolean"
    GRAPH = "graph"
    IDENTITY = "identity"
    CONTRADICTION = "contradiction"
    INEQUALITY_REGION = "inequality_region"
    ODE_SOLUTION = "ode_solution"
    COMPLEX_RESIDUE = "complex_residue"
    COMPLEX_SINGULARITIES = "complex_singularities"


class ErrorCode(str, Enum):
    PARSE_ERROR = "PARSE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TIMEOUT = "TIMEOUT"
    COMPLEXITY_LIMIT = "COMPLEXITY_LIMIT"
    SINGULAR_MATRIX = "SINGULAR_MATRIX"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    DOMAIN_ERROR = "DOMAIN_ERROR"
    AMBIGUOUS_VARIABLE = "AMBIGUOUS_VARIABLE"
    INVALID_VARIABLE = "INVALID_VARIABLE"
    UNSUPPORTED_IN_PHASE_1 = "UNSUPPORTED_IN_PHASE_1"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    INTERNAL_ERROR = "INTERNAL_ERROR"


ERROR_CODE_HTTP_STATUS: Dict[ErrorCode, int] = {
    ErrorCode.PARSE_ERROR: 200,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.TIMEOUT: 200,
    ErrorCode.COMPLEXITY_LIMIT: 200,
    ErrorCode.SINGULAR_MATRIX: 200,
    ErrorCode.DIMENSION_MISMATCH: 200,
    ErrorCode.DOMAIN_ERROR: 200,
    ErrorCode.AMBIGUOUS_VARIABLE: 200,
    ErrorCode.INVALID_VARIABLE: 200,
    ErrorCode.UNSUPPORTED_IN_PHASE_1: 200,
    ErrorCode.UNSUPPORTED_OPERATION: 200,
    ErrorCode.INTERNAL_ERROR: 500,
}


class Step(BaseModel):
    index: int
    title: str
    description: str
    rule: Optional[str] = None
    latex_before: str
    latex_after: str


class EquationSolution(BaseModel):
    text: str
    latex: str
    is_complex: bool = False


class DomainCondition(BaseModel):
    text: str
    latex: str
    variable: Optional[str] = None
    kind: str = "domain"


class Trace(BaseModel):
    type: str
    name: str
    x: List[float]
    y: List[Optional[float]]
    z: Optional[List[List[float]]] = None
    hole_x: List[float] = []
    hole_y: List[float] = []


class GraphAnalysis(BaseModel):
    domain_text: Optional[str] = None
    domain_latex: Optional[str] = None
    range_text: Optional[str] = None
    range_latex: Optional[str] = None
    y_intercept: Optional[str] = None
    x_intercepts: List[str] = []
    local_maxima: List[str] = []
    local_minima: List[str] = []
    inflection_points: List[str] = []


class GraphData(BaseModel):
    traces: List[Trace]
    x_range: List[float]
    y_range: Optional[List[float]] = None
    points_truncated: bool = False
    analysis: Optional[List[GraphAnalysis]] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None


class MathResponse(BaseModel):
    success: bool
    operation: OperationType
    request_id: str
    result_type: Optional[ResultType] = None
    input_text: Optional[str] = None
    input_latex: Optional[str] = None
    result_latex: Optional[str] = None
    result_text: Optional[str] = None
    result_approx: Optional[float] = None
    result_data: Optional[Union[List[EquationSolution], List[List[str]]]] = None
    result_matrices: Optional[Dict[str, List[List[str]]]] = None
    steps: List[Step] = []
    has_detailed_steps: bool
    graph_data: Optional[GraphData] = None
    warnings: List[str] = []
    domain_conditions: List[DomainCondition] = []
    error_code: Optional[ErrorCode] = None
    error_message: Optional[str] = None
    duration_ms: float
