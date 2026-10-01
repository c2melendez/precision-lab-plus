"""
app/services/phase2_service.py — passthrough trivial REAL para `/limit` y
`/series` (spec, sección 2: "Sí — sympy.limit()" / "Sí — sympy.series()"),
más `/solve/system`, `/inequality`, `/integral/improper`,
`/derivative/partial` y `/derivative/implicit` (destrabados después de la
Fase 1 — ver cada función para su técnica de SymPy específica).

`/graph/3d` y `/graph/parametric` siguen sin implementar (requieren además
una visualización nueva en el frontend, alcance mayor que el resto de este
módulo) — responden `UNSUPPORTED_IN_PHASE_1` directamente desde el router
(`app/routers/phase2.py`), sin pasar por este servicio.
"""

from dataclasses import dataclass
from typing import List

import sympy

from app.schemas.responses import EquationSolution, GraphData, InequalityInterval, Trace
from app.services import graph_service, integral_service, parsing

_DIRECTION_MAP = {"both": "+-", "left": "-", "right": "+"}

MAX_SYSTEM_SOLUTIONS = 20  # tope defensivo (sección 7/9: mismo espíritu que otros límites)


@dataclass
class LimitResult:
    input_expr: sympy.Expr
    value: sympy.Expr
    # Fix (suite de regresión v1.1, caso L010: abs(x)/x en x=0 crasheaba
    # con INTERNAL_ERROR 500). sympy.limit() con dir="+-" (ambos lados)
    # LANZA una ValueError de Python cuando el límite lateral izquierdo y
    # derecho difieren — "no existe" es una respuesta matemática válida,
    # no un fallo del sistema, así que no debería tumbar el endpoint con
    # un 500. Este campo lo distingue para que el router lo formatee
    # como resultado (DNE), no como error.
    dne: bool = False
    left_value: sympy.Expr = None
    right_value: sympy.Expr = None
    dne_reason: str | None = None


@dataclass
class SeriesResult:
    input_expr: sympy.Expr
    value: sympy.Expr


class InconsistentVariablesError(ValueError):
    """`equations`/`variables` de tamaños incompatibles, o un nombre de
    variable inválido -> `ErrorCode.VALIDATION_ERROR`."""


@dataclass
class SolveSystemResult:
    solutions: List[EquationSolution]
    has_solutions: bool
    warnings: List[str]
    graph_expressions: List[str] | None = None
    graph_latex: List[str] | None = None
    graph_intersections: List[List[float]] | None = None
    graph_coincident: bool = False
    graph_data: GraphData | None = None
    graph_component_indices: List[int] | None = None


def _validate_variable(variable: str) -> sympy.Symbol:
    candidates = parsing.extract_candidate_identifiers(variable)
    if candidates != [variable]:
        raise parsing.ParseSecurityError(f"Nombre de variable inválido: '{variable}'.")
    return sympy.Symbol(variable)


def compute_limit(expression: str, variable: str, point: str, direction: str) -> LimitResult:
    """Passthrough trivial: `sympy.limit(expr, var, point, dir=...)` directo.

    Fix (suite de regresión v1.1, caso L010: abs(x)/x en x=0 crasheaba
    con INTERNAL_ERROR 500). Si dir="+-" y los límites laterales
    difieren, sympy.limit() lanza ValueError en vez de devolver algo —
    "el límite no existe" es una respuesta matemática válida, no un
    fallo del sistema. Se atrapa específicamente ESE mensaje (no
    cualquier ValueError, para no ocultar otros fallos genuinos) y se
    recalculan los dos límites laterales por separado para reportarlos.
    """
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    var_symbol = _validate_variable(variable)
    point_expr = parsing.parse_expression_tree(point, allow_equation=False)

    # Fast exact identities that otherwise enter expensive heuristic
    # limit branches in SymPy.
    if point_expr == 0 and input_expr == var_symbol * sympy.cot(var_symbol):
        return LimitResult(input_expr, sympy.Integer(1))

    # Fast, exact handling for canonical oscillatory limits that otherwise
    # keep SymPy busy until the client's 15-second timeout.
    if direction == "both":
        if point_expr in (sympy.oo, -sympy.oo) and input_expr in (
            sympy.sin(var_symbol),
            sympy.cos(var_symbol),
        ):
            return LimitResult(
                input_expr,
                sympy.nan,
                dne=True,
                left_value=None,
                right_value=None,
                dne_reason="El límite no existe por oscilación.",
            )
        reciprocal = sympy.Pow(var_symbol, -1)
        if point_expr == 0 and input_expr in (
            sympy.sin(reciprocal),
            sympy.cos(reciprocal),
        ):
            return LimitResult(
                input_expr,
                sympy.nan,
                dne=True,
                left_value=sympy.S.NaN,
                right_value=sympy.S.NaN,
            )

    # Inverse hyperbolic functions have exact logarithmic forms. Rewriting
    # them before limit() avoids several expensive heuristic branches while
    # preserving the same real limit.
    limit_expr = input_expr
    if input_expr.has(sympy.asinh, sympy.acosh, sympy.atanh, sympy.acoth, sympy.asech, sympy.acsch):
        limit_expr = input_expr.rewrite(sympy.log)

    try:
        value = sympy.limit(limit_expr, var_symbol, point_expr, dir=_DIRECTION_MAP[direction])
        if direction == "both" and isinstance(
            value, sympy.calculus.accumulationbounds.AccumBounds
        ):
            return LimitResult(
                input_expr,
                sympy.nan,
                dne=True,
                left_value=None,
                right_value=None,
                dne_reason="El límite no existe por oscilación.",
            )
        if direction == "both" and value.has(sympy.zoo):
            left = sympy.limit(input_expr, var_symbol, point_expr, dir="-")
            right = sympy.limit(input_expr, var_symbol, point_expr, dir="+")
            if left != right:
                return LimitResult(input_expr, sympy.nan, dne=True, left_value=left, right_value=right)
        return LimitResult(input_expr, value)
    except ValueError as exc:
        if "does not exist" not in str(exc) or direction != "both":
            raise
        left = sympy.limit(input_expr, var_symbol, point_expr, dir="-")
        right = sympy.limit(input_expr, var_symbol, point_expr, dir="+")
        return LimitResult(input_expr, sympy.nan, dne=True, left_value=left, right_value=right)


def compute_series(expression: str, variable: str, point: str, order: int) -> SeriesResult:
    """Passthrough trivial: `sympy.series(expr, var, point, n=order+1)` directo,
    sin remover el término `O(...)` — resultado de SymPy tal cual."""
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    var_symbol = _validate_variable(variable)
    point_expr = parsing.parse_expression_tree(point, allow_equation=False)

    value = sympy.series(input_expr, var_symbol, point_expr, n=order + 1)
    return SeriesResult(input_expr, value)


def _format_solution_tuple(
    var_symbols: List[sympy.Symbol], values: tuple
) -> EquationSolution:
    assignments_text = ", ".join(f"{v}={val}" for v, val in zip(var_symbols, values))
    assignments_latex = r",\ ".join(
        f"{sympy.latex(v)} = {sympy.latex(val)}" for v, val in zip(var_symbols, values)
    )
    is_complex = any(val.has(sympy.I) for val in values)
    return EquationSolution(text=assignments_text, latex=assignments_latex, is_complex=is_complex)


def _vertical_system_graph(equations, variables, solution_set) -> tuple[GraphData | None, bool, List[List[float]]]:
    """Exact affine coefficients produce actual vertical traces, never fake functions."""
    x, y = variables
    polynomials = [sympy.Poly(eq.lhs - eq.rhs, x, y) for eq in equations]
    coefficients = [(poly.coeff_monomial(x), poly.coeff_monomial(y), poly.coeff_monomial(1))
                    for poly in polynomials]
    if not any(b == 0 for _, b, _ in coefficients) or any(
        a == b == 0 or any(value.is_real is not True for value in (a, b, c))
        for a, b, c in coefficients
    ):
        return None, False, []
    # A vertical line may be paired with another vertical or an oblique line.
    coincident = all(sympy.simplify(coefficients[0][i] * coefficients[1][j]
                                    - coefficients[1][i] * coefficients[0][j]) == 0
                     for i, j in ((0, 1), (0, 2), (1, 2)))
    intersections = []
    if not coincident and solution_set:
        for point in solution_set:
            if all(value.is_real is True and not value.free_symbols for value in point):
                intersections.append([float(sympy.N(value)) for value in point])
    center_x = intersections[0][0] if intersections else float(-coefficients[0][2] / coefficients[0][0]) if coefficients[0][1] == 0 else 0.0
    center_y = intersections[0][1] if intersections else 0.0
    if not all(sympy.Float(value).is_finite and abs(value) <= 1e6 for value in (center_x, center_y)):
        return None, False, []
    x_min, x_max = center_x - 10, center_x + 10
    y_min, y_max = center_y - 10, center_y + 10
    traces = []
    for index, (a, b, c) in enumerate(coefficients[:1] if coincident else coefficients):
        if b == 0:
            fixed_x = float(-c / a)
            traces.append(Trace(type="line", name=str(equations[index]),
                                x=[fixed_x, fixed_x], y=[y_min, y_max]))
        else:
            traces.append(Trace(type="line", name=str(equations[index]),
                                x=[x_min, x_max], y=[float((-a * xx - c) / b) for xx in (x_min, x_max)]))
    if intersections:
        traces.append(Trace(type="point", name="Intersección común",
                            x=[point[0] for point in intersections],
                            y=[point[1] for point in intersections]))
    all_y = [value for trace in traces for value in trace.y] + [y_min, y_max]
    if not all(sympy.Float(value).is_finite and abs(value) <= 1e9 for value in all_y):
        return None, False, []
    return GraphData(traces=traces, x_range=[x_min, x_max],
                     y_range=[min(all_y), max(all_y)]), coincident, intersections


def _explicit_nonlinear_system_graph(equations, variables, raw_solutions):
    """Graph every real polynomial branch y=f(x), or decline the whole system."""
    if len(variables) != 2 or len(equations) != 2:
        return None
    x, y = variables
    polynomials = [(eq.lhs - eq.rhs).as_poly(x, y) for eq in equations]
    if any(poly is None or poly.total_degree() > 4 or poly.degree(y) > 2
           or poly.degree(y) < 1 or any(coefficient.is_real is not True for coefficient in poly.coeffs())
           for poly in polynomials):
        return None
    coincident = sympy.cancel(polynomials[0].as_expr() / polynomials[1].as_expr())
    coincident = coincident.is_number and coincident.is_finite is True and coincident != 0
    expressions, latex, groups = [], [], []
    for index, equation in enumerate(equations[:1] if coincident else equations):
        branches = sympy.solve(equation, y)
        if not 1 <= len(branches) <= 2:
            return None
        for branch in branches:
            if branch.free_symbols - {x} or branch.has(sympy.I):
                return None
            expressions.append(str(branch))
            latex.append(sympy.latex(branch))
            groups.append(index)
    if len(expressions) > 5:
        return None
    intersections = []
    if not coincident:
        for solution in raw_solutions:
            values = [solution.get(symbol, symbol) for symbol in variables]
            if any(value.free_symbols or value.is_real is not True for value in values):
                continue
            point = [float(sympy.N(value)) for value in values]
            if (all(abs(value) <= 1e6 and sympy.Float(value).is_finite for value in point)
                    and point not in intersections):
                intersections.append(point)
    return expressions, latex, groups, intersections, bool(coincident)


def _mixed_vertical_nonlinear_graph(equations, variables, raw_solutions):
    """Finite real branches of one polynomial plus an actual vertical line."""
    if len(equations) != 2 or len(variables) != 2:
        return None
    x, y = variables
    polynomials = [(eq.lhs - eq.rhs).as_poly(x, y) for eq in equations]
    if any(poly is None for poly in polynomials):
        return None
    vertical_indices = [i for i, poly in enumerate(polynomials)
                        if poly.total_degree() == 1 and poly.degree(y) == 0
                        and all(coefficient.is_real is True for coefficient in poly.coeffs())]
    if len(vertical_indices) != 1:
        return None
    vertical_index = vertical_indices[0]
    curve_index = 1 - vertical_index
    curve_poly = polynomials[curve_index]
    if (curve_poly.total_degree() > 4 or not 1 <= curve_poly.degree(y) <= 2
            or any(coefficient.is_real is not True for coefficient in curve_poly.coeffs())):
        return None
    branches = sympy.solve(equations[curve_index], y)
    if not 1 <= len(branches) <= 2 or any(branch.free_symbols - {x} or branch.has(sympy.I)
                                               for branch in branches):
        return None
    vertical_poly = polynomials[vertical_index]
    fixed = sympy.cancel(-vertical_poly.coeff_monomial(1) / vertical_poly.coeff_monomial(x))
    if fixed.is_real is not True or fixed.free_symbols:
        return None
    fixed_x = float(sympy.N(fixed))
    if not sympy.Float(fixed_x).is_finite or abs(fixed_x) > 1e6:
        return None
    intersections = []
    for solution in raw_solutions:
        values = [solution.get(symbol, symbol) for symbol in variables]
        if any(value.free_symbols or value.is_real is not True for value in values):
            continue
        point = [float(sympy.N(value)) for value in values]
        if all(sympy.Float(value).is_finite and abs(value) <= 1e6 for value in point) and point not in intersections:
            intersections.append(point)
    span = max(2.0, *(abs(point[1]) * 1.5 for point in intersections)) if intersections else 10.0
    span = min(span, 1e4)
    x_min, x_max = fixed_x - span, fixed_x + span
    x_values = [x_min + i * (x_max - x_min) / 200 for i in range(201)]
    curve_traces = [Trace(type="line", name=str(equations[curve_index]) + f" · rama {i+1}",
                          x=x_values, y=[graph_service._evaluate_at(branch, x, xx) for xx in x_values])
                    for i, branch in enumerate(branches)]
    visible_y = [value for trace in curve_traces for value in trace.y if value is not None]
    visible_y.extend(point[1] for point in intersections)
    if not visible_y:
        visible_y = [-span, span]
    y_span = max(1.0, max(visible_y) - min(visible_y))
    y_min, y_max = min(visible_y) - y_span * 0.15, max(visible_y) + y_span * 0.15
    if not all(sympy.Float(value).is_finite and abs(value) <= 1e6 for value in (y_min, y_max)):
        return None
    vertical_trace = Trace(type="line", name=str(equations[vertical_index]),
                           x=[fixed_x, fixed_x], y=[y_min, y_max])
    traces = curve_traces + [vertical_trace]
    if intersections:
        traces.append(Trace(type="point", name="Intersección común",
                            x=[point[0] for point in intersections],
                            y=[point[1] for point in intersections]))
    return GraphData(traces=traces, x_range=[x_min, x_max], y_range=[y_min, y_max]), intersections, [curve_index] * len(branches) + [vertical_index]


@dataclass
class InequalityResult:
    solution_set: sympy.Set
    warnings: List[str]


def inequality_number_line_intervals(solution_set: sympy.Set) -> List[InequalityInterval] | None:
    """A finite union of real intervals/points, preserving endpoint inclusion."""
    if solution_set == sympy.S.EmptySet:
        return []
    parts = solution_set.args if isinstance(solution_set, sympy.Union) else (solution_set,)
    if len(parts) > 12:
        return None
    intervals = []
    for part in parts:
        if isinstance(part, sympy.Interval):
            lower, upper = part.start, part.end
            if lower != -sympy.oo and (lower.is_real is not True or lower.free_symbols):
                return None
            if upper != sympy.oo and (upper.is_real is not True or upper.free_symbols):
                return None
            values = [float(sympy.N(bound)) for bound in (lower, upper) if bound.is_finite]
            if any(not sympy.Float(value).is_finite or abs(value) > 1e6 for value in values):
                return None
            intervals.append(InequalityInterval(
                lower=None if lower == -sympy.oo else float(sympy.N(lower)),
                upper=None if upper == sympy.oo else float(sympy.N(upper)),
                lower_text=None if lower == -sympy.oo else str(lower),
                upper_text=None if upper == sympy.oo else str(upper),
                lower_included=not part.left_open, upper_included=not part.right_open))
        elif isinstance(part, sympy.FiniteSet):
            for point in part:
                if point.is_real is not True or point.free_symbols:
                    return None
                numeric = float(sympy.N(point))
                if not sympy.Float(numeric).is_finite or abs(numeric) > 1e6:
                    return None
                intervals.append(InequalityInterval(lower=numeric, upper=numeric,
                    lower_text=str(point), upper_text=str(point),
                    lower_included=True, upper_included=True))
        else:
            return None
    return intervals


def _bounded_continuous_trig_inequality(inequality, var, domain_set):
    """Classify every component between exact zeros and original trig poles."""
    from app.services.solve_service import _bounded_trig_polynomial_solutions

    expr = inequality.lhs - inequality.rhs
    trig_functions = (sympy.sin, sympy.cos, sympy.tan, sympy.sec, sympy.csc, sympy.cot)
    if not expr.has(*trig_functions):
        return None
    if any(node.func not in (*trig_functions, sympy.Abs)
           for node in expr.atoms(sympy.Function)):
        return None
    if domain_set.start.is_finite is not True or domain_set.end.is_finite is not True:
        return None
    # Fractional powers can introduce real-domain boundaries beyond zeros/poles.
    if any(node.base.has(var) and node.exp.is_integer is not True
           for node in expr.atoms(sympy.Pow)):
        return None

    # Keep singularities from the original expression before together() can
    # cancel a denominator or a reciprocal trig function.
    pole_expressions = []
    for node in sympy.preorder_traversal(inequality):
        if node.func in (sympy.tan, sympy.sec):
            pole_expressions.append(sympy.cos(node.args[0]))
        elif node.func in (sympy.cot, sympy.csc):
            pole_expressions.append(sympy.sin(node.args[0]))
        elif isinstance(node, sympy.Pow) and node.exp.is_negative is True and node.base.has(var):
            pole_expressions.append(node.base)

    def finite_roots(expression):
        if expression == 0:
            return []
        roots = _bounded_trig_polynomial_solutions(expression, var, domain_set)
        if roots is not None:
            return roots
        zeros = sympy.solveset(expression, var, domain=domain_set)
        if zeros is sympy.EmptySet:
            return []
        if isinstance(zeros, sympy.FiniteSet):
            return list(zeros)
        return None

    poles = set()
    for expression in pole_expressions:
        found = finite_roots(expression)
        if found is None:
            return None
        poles.update(found)

    zero_expr = expr
    if expr.has(sympy.Abs):
        if inequality.lhs.func == sympy.Abs and not inequality.rhs.has(var):
            threshold = inequality.rhs
            if threshold.is_nonnegative is not True:
                return None
            zero_expr = inequality.lhs.args[0]**2 - threshold**2
        else:
            return None
    zero_expr = zero_expr.replace(
        lambda node: node.func in (sympy.tan, sympy.sec, sympy.csc, sympy.cot),
        lambda node: {
            sympy.tan: lambda x: sympy.sin(x)/sympy.cos(x),
            sympy.sec: lambda x: 1/sympy.cos(x),
            sympy.csc: lambda x: 1/sympy.sin(x),
            sympy.cot: lambda x: sympy.cos(x)/sympy.sin(x),
        }[node.func](node.args[0]),
    )
    numerator, denominator = sympy.fraction(sympy.together(zero_expr))
    if denominator.has(var):
        found = finite_roots(denominator)
        if found is None:
            return None
        poles.update(found)
    roots = finite_roots(numerator)
    if roots is None:
        return None
    points = sorted(set([domain_set.start, *roots, *poles, domain_set.end]),
                    key=lambda point: float(sympy.N(point, 30)))

    def satisfies(point):
        if point in poles:
            return False
        value = sympy.simplify(expr.subs(var, point))
        if value.is_real is not True or value.is_finite is not True:
            return None
        truth = inequality.func(value, 0)
        if truth is sympy.true:
            return True
        if truth is sympy.false:
            return False
        return None

    solution = sympy.EmptySet
    for left, right in zip(points, points[1:]):
        truth = satisfies((left + right)/2)
        if truth is None:
            return None
        if truth:
            solution = solution.union(sympy.Interval.open(left, right))
    for point in points:
        if domain_set.contains(point) is not sympy.true or point in poles:
            continue
        truth = satisfies(point)
        if truth is None:
            return None
        if truth:
            solution = solution.union(sympy.FiniteSet(point))
    return solution


def compute_inequality(
    inequality: sympy.core.relational.Relational,
    variable: str,
    domain_lower: str | None = None,
    domain_upper: str | None = None,
    domain_lower_inclusive: bool = True,
    domain_upper_inclusive: bool = True,
) -> InequalityResult:
    """`/inequality` (spec, `InequalityRequest`). Usa
    `sympy.solve_univariate_inequality` (una sola variable, el caso común
    de "resuelve esta desigualdad") con `reduce_inequalities` como
    respaldo para casos que `solve_univariate_inequality` no cubre
    (p. ej. cuando el símbolo detectado en el request no coincide con el
    único símbolo libre de la expresión)."""
    var_symbol = _validate_variable(variable)
    warnings: List[str] = []

    # Calculator convention for real arccot uses range (0, pi):
    # arccot(x) = pi/2 - atan(x). SymPy's principal acot branch differs
    # on negative reals and can therefore add spurious intervals for
    # inequalities such as arccot(x) < pi/4. Rewrite only for inequality
    # solving so the rest of the symbolic engine keeps its native forms.
    inequality = inequality.replace(
        lambda node: getattr(node, "func", None) == sympy.acot,
        lambda node: sympy.pi / 2 - sympy.atan(node.args[0]),
    )


    if domain_lower is not None and domain_upper is not None:
        lower_expr = parsing.parse_expression_tree(domain_lower, allow_equation=False)
        upper_expr = parsing.parse_expression_tree(domain_upper, allow_equation=False)
        if lower_expr.free_symbols or upper_expr.free_symbols:
            raise parsing.ParseSecurityError("Los límites del dominio deben ser valores concretos.")
        domain_set = sympy.Interval(
            lower_expr, upper_expr,
            left_open=not domain_lower_inclusive, right_open=not domain_upper_inclusive,
        )
        if isinstance(domain_set, sympy.Interval):
            bounded = _bounded_continuous_trig_inequality(inequality, var_symbol, domain_set)
            if bounded is not None:
                return InequalityResult(bounded, warnings)


    try:
        solution_set = sympy.solve_univariate_inequality(inequality, var_symbol, relational=False)
    except (NotImplementedError, TypeError):
        result = sympy.reduce_inequalities([inequality], [var_symbol])
        if isinstance(result, sympy.logic.boolalg.BooleanFalse):
            solution_set = sympy.S.EmptySet
        elif isinstance(result, sympy.logic.boolalg.BooleanTrue):
            solution_set = sympy.S.Reals
        else:
            warnings.append(
                "No se pudo reducir a un único intervalo; el resultado puede requerir "
                "interpretación manual."
            )
            solution_set = result
    if domain_lower is not None and domain_upper is not None:
        lower_expr = parsing.parse_expression_tree(domain_lower, allow_equation=False)
        upper_expr = parsing.parse_expression_tree(domain_upper, allow_equation=False)
        if lower_expr.free_symbols or upper_expr.free_symbols:
            raise parsing.ParseSecurityError("Los límites del dominio deben ser valores concretos.")
        domain_set = sympy.Interval(
            lower_expr,
            upper_expr,
            left_open=not domain_lower_inclusive,
            right_open=not domain_upper_inclusive,
        )
        solution_set = sympy.Intersection(solution_set, domain_set)

    return InequalityResult(solution_set, warnings)


@dataclass
class PartialDerivativeResult:
    value: sympy.Expr


def compute_partial_derivative(expression: str, variable: str, order: int) -> PartialDerivativeResult:
    """`/derivative/partial` (spec, `PartialDerivativeRequest`). SymPy ya
    trata cualquier símbolo distinto al de derivación como constante por
    defecto (`sympy.diff(expr, var, order)`) — es exactamente la misma
    operación que la derivada "normal" de una sola variable, la única
    diferencia real es semántica (la expresión SUELE tener más de una
    variable libre, p. ej. `x**2*y` respecto a `x`). Sin pasos detallados
    (mismo patrón que `eigen`/`transpose`/`limit`)."""
    expr = parsing.parse_expression_tree(expression, allow_equation=False)
    var_symbol = _validate_variable(variable)
    value = sympy.diff(expr, var_symbol, order)
    return PartialDerivativeResult(value)


@dataclass
class ImplicitDerivativeResult:
    value: sympy.Expr


def compute_implicit_derivative(
    equation: str, dependent_variable: str, independent_variable: str
) -> ImplicitDerivativeResult:
    """`/derivative/implicit` (spec, `ImplicitDerivativeRequest`):
    diferenciación implícita clásica — se sustituye la variable
    dependiente (p. ej. `y`) por `Function('y')(x)`, se deriva ambos
    lados de la ecuación respecto a `x` (aplicando la regla de la
    cadena automáticamente vía SymPy), y se despeja `dy/dx`."""
    eq = parsing.parse_expression_tree(equation, allow_equation=True)
    x_symbol = _validate_variable(independent_variable)
    y_symbol = _validate_variable(dependent_variable)

    if x_symbol not in eq.free_symbols and y_symbol not in eq.free_symbols:
        raise InconsistentVariablesError(
            f"La ecuación no usa ninguna de las variables indicadas "
            f"('{independent_variable}', '{dependent_variable}')."
        )

    y_func = sympy.Function(str(y_symbol))(x_symbol)
    lhs_sub = eq.lhs.subs(y_symbol, y_func)
    rhs_sub = eq.rhs.subs(y_symbol, y_func)

    lhs_diff = sympy.diff(lhs_sub, x_symbol)
    rhs_diff = sympy.diff(rhs_sub, x_symbol)

    y_prime = sympy.diff(y_func, x_symbol)
    diff_equation = sympy.Eq(lhs_diff, rhs_diff)

    solutions = sympy.solve(diff_equation, y_prime)
    if not solutions:
        raise ImplicitDerivativeUnsolvableError(
            "No se pudo despejar dy/dx de forma cerrada para esta ecuación."
        )
    # Se sustituye y(x) de vuelta por el símbolo original ('y') para que el
    # resultado se muestre en términos de las variables que el usuario
    # escribió, no de la notación funcional interna de SymPy.
    value = solutions[0].subs(y_func, y_symbol)
    return ImplicitDerivativeResult(value)


class ImplicitDerivativeUnsolvableError(ValueError):
    """`sympy.solve` no encontró una forma cerrada para dy/dx ->
    `ErrorCode.PARSE_ERROR` (no es un error de validación del payload,
    sino de que la técnica simbólica no aplica a esta ecuación)."""


@dataclass
class ImproperIntegralResult:
    value: sympy.Expr
    warnings: List[str]


def compute_improper_integral(
    expression: str, variable: str, lower_bound: str, upper_bound: str
) -> ImproperIntegralResult:
    """`/integral/improper` (spec, `ImproperIntegralRequest`). A
    diferencia de `/integral` (que RECHAZA límites infinitos —
    `integral_service.UnsupportedInfiniteBoundsError` — porque su
    `manualintegrate` con pasos detallados no está pensado para eso),
    aquí se llama a `sympy.integrate()` directo con los límites que sea
    (incluye `oo`/`-oo`), sin desglose paso a paso: SymPy internamente ya
    resuelve el límite del área bajo la curva cuando la integral converge,
    y devuelve `zoo`/no converge cuando no."""
    expr = parsing.parse_expression_tree(expression, allow_equation=False)
    var_symbol = _validate_variable(variable)
    lower_expr = parsing.parse_expression_tree(lower_bound, allow_equation=False)
    upper_expr = parsing.parse_expression_tree(upper_bound, allow_equation=False)

    fast_antiderivative = integral_service._fast_antiderivative(expr, var_symbol)
    if fast_antiderivative is not None:
        lower_value = sympy.limit(fast_antiderivative, var_symbol, lower_expr, dir="+") \
            if lower_expr in (sympy.oo, -sympy.oo) else fast_antiderivative.subs(var_symbol, lower_expr)
        upper_value = sympy.limit(fast_antiderivative, var_symbol, upper_expr, dir="-") \
            if upper_expr in (sympy.oo, -sympy.oo) else fast_antiderivative.subs(var_symbol, upper_expr)
        value = sympy.simplify(upper_value - lower_value)
    else:
        value = sympy.integrate(expr, (var_symbol, lower_expr, upper_expr))

    warnings: List[str] = []
    if value.has(sympy.Integral):
        warnings.append(
            "SymPy no pudo resolver esta integral impropia de forma cerrada; el "
            "resultado puede quedar parcialmente sin evaluar."
        )
    elif value in (sympy.oo, -sympy.oo, sympy.zoo, sympy.nan):
        warnings.append("La integral diverge (no converge a un valor finito).")

    return ImproperIntegralResult(value, warnings)


def compute_solve_system(equations: List[str], variables: List[str]) -> SolveSystemResult:
    """`/solve/system` (spec, `SolveSystemRequest`). Sistemas LINEALES ->
    `sympy.linsolve` (maneja de forma robusta sin solución / solución única /
    infinitas soluciones paramétricas). Cualquier ecuación no lineal en las
    variables pedidas -> `sympy.solve` (puede devolver 0, 1 o varias
    tuplas solución)."""
    if len(equations) != len(variables):
        raise InconsistentVariablesError(
            "El sistema necesita el mismo número de ecuaciones que de variables a resolver."
        )

    var_symbols = [_validate_variable(v) for v in variables]
    parsed_equations = [
        parsing.parse_expression_tree(eq, allow_equation=True) for eq in equations
    ]

    def _is_linear(eq: sympy.Eq) -> bool:
        try:
            poly = (eq.lhs - eq.rhs).as_poly(*var_symbols)
        except sympy.PolynomialError:
            return False
        return poly is not None and poly.total_degree() <= 1

    is_linear = all(_is_linear(eq) for eq in parsed_equations)

    if is_linear:
        solution_set = sympy.linsolve(parsed_equations, var_symbols)
        graph_expressions = None
        graph_latex = None
        graph_intersections = None
        graph_coincident = False
        graph_data = None
        if len(var_symbols) == 2 and len(parsed_equations) == 2:
            x, y = var_symbols
            # Only explicit, nonvertical affine lines belong in /graph/2d.
            curves = []
            for eq in parsed_equations:
                polynomial = sympy.Poly(eq.lhs - eq.rhs, x, y)
                y_coefficient = polynomial.coeff_monomial(y)
                if y_coefficient == 0 or any(coefficient.is_real is not True
                                             for coefficient in polynomial.coeffs()):
                    break
                curve = sympy.cancel(-polynomial.coeff_monomial(x) * x / y_coefficient
                                     - polynomial.coeff_monomial(1) / y_coefficient)
                if curve.free_symbols - {x}:
                    break
                curves.append(curve)
            if len(curves) == 2:
                graph_coincident = sympy.simplify(curves[0] - curves[1]) == 0
                visible = curves[:1] if graph_coincident else curves
                graph_expressions = [str(curve) for curve in visible]
                graph_latex = [sympy.latex(curve) for curve in visible]
                graph_intersections = []
                if not graph_coincident and solution_set:
                    for point in solution_set:
                        if all(value.is_real is True and not value.free_symbols for value in point):
                            graph_intersections.append([float(sympy.N(value)) for value in point])
            else:
                graph_data, graph_coincident, graph_intersections = _vertical_system_graph(
                    parsed_equations, var_symbols, solution_set)
        if not solution_set:
            return SolveSystemResult([], False, ["El sistema no tiene solución (inconsistente)."],
                                     graph_expressions, graph_latex, graph_intersections, graph_coincident, graph_data)
        solutions = [
            _format_solution_tuple(var_symbols, tuple(values))
            for values in list(solution_set)[:MAX_SYSTEM_SOLUTIONS]
        ]
        # linsolve deja cualquier parámetro libre (tau_i) visible directamente
        # en el texto/latex de la solución cuando el sistema es indeterminado.
        return SolveSystemResult(solutions, True, [], graph_expressions, graph_latex,
                                 graph_intersections, graph_coincident, graph_data)

    raw_solutions = sympy.solve(parsed_equations, var_symbols, dict=True)
    graph = _explicit_nonlinear_system_graph(parsed_equations, var_symbols, raw_solutions)
    graph_fields = (graph[0], graph[1], graph[3], graph[4], None, graph[2]) if graph else (
        None, None, None, False, None, None)
    if not graph:
        mixed = _mixed_vertical_nonlinear_graph(parsed_equations, var_symbols, raw_solutions)
        if mixed:
            graph_fields = (None, None, mixed[1], False, mixed[0], mixed[2])
    if not raw_solutions:
        return SolveSystemResult(
            [], False, ["No se encontraron soluciones para este sistema no lineal."], *graph_fields
        )
    solutions = [
        _format_solution_tuple(var_symbols, tuple(sol.get(v, v) for v in var_symbols))
        for sol in raw_solutions[:MAX_SYSTEM_SOLUTIONS]
    ]
    return SolveSystemResult(solutions, True, [], *graph_fields)
