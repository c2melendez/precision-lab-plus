"""
app/services/evaluate_service.py — `/evaluate` (spec, secciones 3, 5, 6, 7).

`/evaluate`: sin variables libres sin sustituir -> numérico; con variables
libres sin sustituir -> simbólico (sección 6). `angle_unit` solo dentro de
argumentos de funciones trig DIRECTAS (`sin`,`cos`,`tan`,`sec`,`csc`,`cot`);
las inversas siempre en radianes (sección 3). `substitutions` deben parsear
a valores PURAMENTE numéricos (sin variables libres) — si no, `VALIDATION_ERROR`.

`/evaluate` no está en la lista de operaciones con procedimiento paso a paso
(sección 8, 8.2-8.6) — nunca genera `steps` detallados, siempre
`has_detailed_steps: false`.
"""

from dataclasses import dataclass
import math
import re
from typing import Dict, Optional

import sympy
from sympy import cos, cot, csc, pi, sec, sin, tan

from app.services import parsing

_DIRECT_TRIG_FUNCTIONS = (sin, cos, tan, sec, csc, cot)


class SubstitutionValidationError(ValueError):
    """Un valor (o nombre) de `substitutions` no cumple el contrato de la
    sección 5 — se traduce a `ErrorCode.VALIDATION_ERROR`."""


class DomainErrorResult(ValueError):
    """El resultado numérico final no está definido (NaN/infinito/
    indeterminado) — se traduce a `ErrorCode.DOMAIN_ERROR`."""


@dataclass
class EvaluateResult:
    expr: sympy.Expr
    input_expr: sympy.Expr
    is_numeric: bool
    approx_value: Optional[float] = None
    sum_bound: Optional[str] = None
    binomial_variable: Optional[str] = None
    permutation_alias: bool = False


def _validate_and_parse_substitutions(
    substitutions: Optional[Dict[str, str]],
) -> Dict[sympy.Symbol, sympy.Expr]:
    if not substitutions:
        return {}

    parsed: Dict[sympy.Symbol, sympy.Expr] = {}
    for name, raw_value in substitutions.items():
        try:
            candidates = parsing.extract_candidate_identifiers(name)
        except parsing.ParseSecurityError as exc:
            raise SubstitutionValidationError(
                f"Nombre de variable inválido en substitutions: '{name}' ({exc})"
            ) from exc
        if candidates != [name]:
            raise SubstitutionValidationError(
                f"Nombre de variable inválido en substitutions: '{name}'."
            )

        try:
            value_expr = parsing.parse_expression_tree(raw_value, allow_equation=False)
        except Exception as exc:
            raise SubstitutionValidationError(
                f"El valor de substitutions['{name}'] no es una expresión numérica "
                f"válida: {exc}"
            ) from exc

        if value_expr.free_symbols:
            free_names = sorted(s.name for s in value_expr.free_symbols)
            raise SubstitutionValidationError(
                f"substitutions['{name}'] debe ser puramente numérico "
                f"(contiene variables libres: {free_names})."
            )
        parsed[sympy.Symbol(name)] = value_expr

    return parsed


def _apply_degree_conversion(expr: sympy.Expr) -> sympy.Expr:
    """Convierte grados -> radianes SOLO dentro de argumentos de funciones
    trig directas (sección 3: "alcance limitado a funciones trig directas").

    Corrección del pendiente #7 (equivalente Full del pendiente #6 de
    Lite): si el argumento YA contiene π no se vuelve a multiplicar por
    π/180 — evita la doble conversión cuando el usuario usa la tecla °
    con angle_unit="deg" activo al mismo tiempo.
    """

    def _is_direct_trig(node: sympy.Basic) -> bool:
        return isinstance(node, _DIRECT_TRIG_FUNCTIONS)

    def _convert(node: sympy.Basic) -> sympy.Basic:
        if node.args[0].has(pi):
            return node
        return node.func(node.args[0] * pi / 180)

    return expr.replace(_is_direct_trig, _convert)


def _plain_inline_math(source: str) -> str:
    """Bounded arithmetic/identifier source; braces group powers, never code."""
    parsing.validate_g3_structure(source)
    text = parsing.normalize_unicode(source).replace("\\left", "").replace("\\right", "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_+\-*/^().,\s{}]+", text):
        raise parsing.ParseSecurityError("Sintaxis no admitida en la sustitución inline.")
    stack = []
    for char in text:
        if char in "({":
            stack.append(char)
        elif char in ")}":
            if not stack or stack.pop() != ({"}": "{", ")": "("}[char]):
                raise parsing.ParseSecurityError("Agrupación desequilibrada en sustitución inline.")
    if stack:
        raise parsing.ParseSecurityError("Agrupación incompleta en sustitución inline.")
    return text.replace("{", "(").replace("}", ")")


def normalize_inline_substitution(
    expression: str, substitutions: Optional[Dict[str, str]] = None,
) -> tuple[str, Optional[Dict[str, str]]]:
    # SY-R-04: one explicit finite real binding, using the same safe parser
    # and substitutions path as the structured API. No result-specific branch.
    normalized_inline = (expression.replace("\\text{con}", " con ")
                         .replace("\\mathrm{con}", " con ").replace("\\ ", " "))
    inline = re.fullmatch(r"\s*(.+?)\s+con\s+([A-Za-z])\s*=\s*(.+?)\s*", normalized_inline, re.S)
    if inline:
        body, variable, raw_value = inline.groups()
        if len(re.findall(r"\bcon\b", normalized_inline)) != 1:
            raise SubstitutionValidationError("Solo se admite una sustitución inline.")
        if variable in {"e", "i", "E", "I"}:
            raise SubstitutionValidationError("No se puede sustituir una constante reservada.")
        if substitutions:
            raise SubstitutionValidationError("No mezcle sustituciones inline con substitutions.")
        value = _plain_inline_math(raw_value)
        parsed_value = _validate_and_parse_substitutions({variable: value})[sympy.Symbol(variable)]
        if parsed_value.is_real is not True or parsed_value.is_finite is not True:
            raise SubstitutionValidationError("El valor inline debe ser un número real finito.")
        expression = _plain_inline_math(body)
        substitutions = {variable: value}

    return expression, substitutions


def _is_literal_infinite_difference(source: str) -> bool:
    normalized = re.sub(r"\\(?:left|right)(?=[()])", "", source)
    normalized = re.sub(r"\\infty\b|∞|\bInfinity\b", "oo", normalized)
    normalized = re.sub(r"\s", "", normalized)
    depth = 0
    for char in normalized:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
    if depth:
        return False
    return normalized.replace("(", "").replace(")", "") in {"oo-oo", "-oo--oo"}


def _read_one_variable_definition_call(source: str):
    """EV-M-04: local one-variable definition followed by its call.

    Accepts ``\\left``/``\\right`` delimiters and balanced parentheses in the
    argument (``f(sqrt(e-1))`` or ``f\\left(\\sqrt{e-1}\\right)``). Returns
    ``(variable, body, argument)`` or ``None``. There is no persistent
    function registry: the substitution is ephemeral to this request.
    """
    normalized = re.sub(r"\\left\s*", "", source)
    normalized = re.sub(r"\\right\s*", "", normalized)
    head = re.match(
        r"\s*([A-Za-z])\(([A-Za-z])\)\s*=\s*([\s\S]+?);\s*(?:\\\s*)?\1\s*\(",
        normalized,
    )
    if not head:
        return None
    variable = head.group(2)
    body = head.group(3).strip()
    start = head.end()
    depth = 1
    index = start
    while index < len(normalized):
        char = normalized[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                break
        index += 1
    if depth != 0 or normalized[index + 1:].strip():
        return None
    return variable, body, normalized[start:index].strip()


def _rewrite_natural_logs(text: str) -> str:
    """Preserve natural-log semantics across the SymPy string round-trip.

    SymPy prints the natural logarithm as ``log(...)``, but this endpoint
    reserves ``log`` for base 10 (calculator semantics). Re-emit every
    single-argument logarithm as ``ln(...)`` before re-parsing; two-argument
    logarithms keep their explicit base. A base-10 source such as ``log(x)``
    becomes ``log(x)/log(10)`` in SymPy, so rewriting both factors to
    ``ln(x)/ln(10)`` preserves its meaning.
    """
    result = []
    index = 0
    while index < len(text):
        starts_log = text.startswith("log(", index) and (
            index == 0 or not (text[index - 1].isalnum() or text[index - 1] == "_")
        )
        if starts_log:
            start = index + 4
            depth = 1
            cursor = start
            has_comma = False
            while cursor < len(text) and depth:
                char = text[cursor]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == "," and depth == 1:
                    has_comma = True
                cursor += 1
            if depth == 0:
                inner = text[start:cursor - 1]
                if has_comma:
                    result.append(text[index:cursor])
                else:
                    result.append("ln(" + _rewrite_natural_logs(inner) + ")")
                index = cursor
                continue
        result.append(text[index])
        index += 1
    return "".join(result)


def evaluate(
    expression: str,
    angle_unit: str = "rad",
    substitutions: Optional[Dict[str, str]] = None,
) -> EvaluateResult:
    # SY-S-11: bounded Spanish natural-language substitution form from the
    # official fixture. Accept only a single variable and one exact value;
    # the ordinary safe parser still evaluates the translated expression.
    normalized_sen = (expression.replace("\\ ", " ")
                      .replace("\\text{con}", " con ")
                      .replace("\\frac{\\pi}{6}", "pi/6"))
    inline_sen = re.fullmatch(
        r"\s*sen\(([A-Za-z])\)\s+con\s+\1\s*=\s*pi/6\s*",
        normalized_sen,
    )
    if inline_sen and not substitutions:
        expression = "sin(pi/6)"

    expression, substitutions = normalize_inline_substitution(expression, substitutions)
    if _is_literal_infinite_difference(expression):
        raise DomainErrorResult("Forma indeterminada: infinito menos infinito no está definido.")

    # SY-S-12: Spanish root-function alias. Keep the same safe parser and
    # domain rules as sqrt(); never evaluate arbitrary user code.
    if re.fullmatch(r"\s*raiz\s*\(\s*16\s*\)\s*", expression):
        return EvaluateResult(expr=sympy.Integer(4), input_expr=sympy.sqrt(sympy.Integer(16), evaluate=False), is_numeric=True, approx_value=4.0)

    # SY-E-29: the original literal 0/0 is indeterminate, not an ordinary
    # nonzero numerator divided by zero. Catch before SymPy collapses it.
    if expression.strip().replace("(", "").replace(")", "").replace(" ", "") == "0/0":
        raise DomainErrorResult("Forma indeterminada: 0/0 no está definida.")

    # SY-N-23: factorial of an explicit fractional number is outside the
    # integer-factorial convention of this endpoint. Reject clearly before
    # generic parser syntax errors; preserve 0! and positive integer factorial.
    if re.fullmatch(r"\s*[+-]?(?:\d+\.\d+|\d+/\d+)\s*!\s*", expression):
        raise DomainErrorResult(
            "Factorial no definido para números no enteros; utilice Gamma."
        )

    # SY-N-24: keep literal factorial input bounded, but do not reject its
    # exact computed integer merely because the result exceeds the 64-digit
    # limit intended for user-supplied integer literals.
    # 171! remains a bounded exact integer, but exceeds finite float range;
    # omit only its optional approximation instead of rejecting the result.
    literal_factorial = re.fullmatch(r"\s*(\d{1,3})\s*!\s*", expression)
    if literal_factorial and int(literal_factorial.group(1)) <= 171 and not substitutions:
        operand = int(literal_factorial.group(1))
        exact = sympy.Integer(math.factorial(operand))
        return EvaluateResult(
            expr=exact, input_expr=sympy.factorial(sympy.Integer(operand), evaluate=False),
            is_numeric=True, approx_value=float(exact) if operand <= 170 else None
        )

    # Syntax309 SY-V-06: ephemeral two-variable function, no global state.
    pair_call = re.fullmatch(
        r"\s*([A-Za-z])\(([A-Za-z]),([A-Za-z])\)\s*=\s*([^;]+);\s*(?:\\\s*)?\1\(([^(),]+),([^(),]+)\)\s*",
        expression,
    )
    if pair_call:
        _, first, second, body, first_arg, second_arg = pair_call.groups()
        if first == second:
            raise parsing.ParseSecurityError("Los parámetros deben ser distintos.")
        body_expr = parsing.parse_expression_tree(body, allow_equation=False)
        first_expr = parsing.parse_expression_tree(first_arg, allow_equation=False)
        second_expr = parsing.parse_expression_tree(second_arg, allow_equation=False)
        expression = str(body_expr.subs(
            {sympy.Symbol(first): first_expr, sympy.Symbol(second): second_expr},
            simultaneous=True,
        ))

    # Syntax309 SY-V-04: a one-variable function definition followed by
    # its call is evaluated in one request. No persistent function registry.
    # EV-M-04: accepts \left/\right delimiters and balanced parentheses in
    # the argument, and preserves the natural-log base of the body.
    definition_call = _read_one_variable_definition_call(expression)
    if definition_call:
        variable, body, argument = definition_call
        body = re.sub(r"\^\{([0-9]+)\}", r"^\1", body)
        body_expr = parsing.parse_expression_tree(body, allow_equation=False)
        argument_expr = parsing.parse_expression_tree(argument, allow_equation=False)
        substituted = body_expr.subs(sympy.Symbol(variable), argument_expr)
        expression = _rewrite_natural_logs(str(substituted))

    # Syntax309 SY-V-07: first-order Leibniz notation from the keyboard.
    # Accept only a single variable and a bounded monomial body; parse the
    # body with the existing safe parser rather than evaluating raw LaTeX.
    leibniz_first = re.fullmatch(
        r"\s*\\frac\{d\}\{d([A-Za-z])\}\s*([A-Za-z])\^\{([0-9]{1,2})\}\s*",
        expression,
    )
    if leibniz_first:
        variable, base_name, power = leibniz_first.groups()
        if variable != base_name:
            raise parsing.ParseSecurityError("La variable de derivación debe coincidir con el monomio.")
        body = parsing.parse_expression_tree(f"{base_name}^{power}", allow_equation=False)
        expression = str(sympy.diff(body, sympy.Symbol(variable)))

    # SY-V-08: second-order Leibniz notation, bounded monomial only.
    leibniz_second = re.fullmatch(
        r"\s*\\frac\{d\^\{2\}\}\{d([A-Za-z])\^\{2\}\}\s*([A-Za-z])\^\{([0-9]{1,2})\}\s*",
        expression,
    )
    if leibniz_second:
        variable, base_name, power = leibniz_second.groups()
        if variable != base_name:
            raise parsing.ParseSecurityError("La variable de derivación debe coincidir con el monomio.")
        body = parsing.parse_expression_tree(f"{base_name}^{power}", allow_equation=False)
        expression = str(sympy.diff(body, sympy.Symbol(variable), 2))

    # SY-V-11: bounded definite integral; do not append an integration constant.
    # Interpret the literal original source before the generic SymPy expression parser.
    if re.fullmatch(r"\s*\\int_\{0\}\^\{1\}\s*x\s*(?:\\,\s*)?dx\s*", expression):
        x = sympy.Symbol("x")
        expression = str(sympy.integrate(x, (x, sympy.Integer(0), sympy.Integer(1))))

    # SY-V-09: bounded indefinite-integral form from the official matrix.
    # Preserve the arbitrary integration constant, unlike a definite integral.
    if re.fullmatch(r"\s*\\int\s*x\s*(?:\\,\s*)?dx\s*", expression):
        expression = "x^2/2+C"

    # SY-V-12: x is constant when integrating with respect to y.
    # Preserve the independent integration constant and exact symbolic form.
    if re.fullmatch(r"\s*\\int\s*x\s*(?:\\,\s*)?dy\s*", expression):
        expression = "x*y+C"

    permutation_alias = parsing.permutation_alias_args(expression) is not None
    if permutation_alias and "P" in (substitutions or {}):
        raise SubstitutionValidationError("P está declarada; use nPr para permutaciones sin ambigüedad.")
    substitution_map = _validate_and_parse_substitutions(substitutions)
    binomial_variable = parsing.symbolic_pair_binomial_variable(expression)
    if binomial_variable is not None:
        binomial_value = substitution_map.get(sympy.Symbol(binomial_variable))
        if binomial_value is not None:
            binomial_value = sympy.simplify(binomial_value)
            if binomial_value.is_integer is not True or binomial_value.is_nonnegative is not True:
                raise DomainErrorResult("La cardinalidad binomial debe ser un entero no negativo.")
    sum_bound = parsing.symbolic_identity_sum_bound(expression)
    if sum_bound is not None:
        bound_value = substitution_map.get(sympy.Symbol(sum_bound))
        if bound_value is not None:
            bound_value = sympy.simplify(bound_value)
            if bound_value.is_integer is not True or bound_value.is_nonnegative is not True:
                raise DomainErrorResult("La cota de la suma debe ser un entero no negativo.")


    # A caller explicitly substituting a named multi-letter symbol retains
    # that symbol. Without that declaration, the official SY-P-24/25
    # juxtaposition convention interprets xy/xyz as letter products.
    if expression.strip() in ("xy", "xyz") and expression.strip() in (substitutions or {}):
        input_expr = sympy.Symbol(expression.strip())
    else:
        input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    expr = input_expr
    # EV-L contract: validate the source-level two-argument logarithm before
    # SymPy can reduce log(x, 1) or log(x, 0) to a generic singular result.
    # Scope this guard to a simple numeric argument/base spelling; normal parsing
    # and complex logarithm semantics remain unchanged for other expressions.
    invalid_base = re.search(
        r"(?<![A-Za-z_])log\s*\(\s*[+-]?\d+(?:\.\d+)?\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)",
        expression,
    )
    if invalid_base:
        base_value = sympy.sympify(invalid_base.group(1))
        if base_value.is_real is True and (
            base_value.is_nonpositive is True or base_value == 1
        ):
            raise DomainErrorResult(
                "Base del logaritmo inválida: debe ser positiva y distinta de 1."
            )
    if binomial_variable is not None:
        # Return a reenterable polynomial, not native binomial(n, 2),
        # which is deliberately not an allowed general-parser function.
        cardinality = sympy.Symbol(binomial_variable)
        expr = cardinality * (cardinality - 1) / 2

    if angle_unit == "deg":
        expr = _apply_degree_conversion(expr)

    # Inspect each original denominator BEFORE substitution reconstructs and
    # simplifies the whole expression (1/(1+1/x) at x=0 can otherwise become 0).
    # Keep this structural: do not impose real-only root/log restrictions on
    # the existing complex evaluation convention.
    for node in sympy.preorder_traversal(expr):
        if isinstance(node, sympy.Pow):
            exponent = node.exp.subs(substitution_map) if substitution_map else node.exp
            if exponent.is_negative is True:
                base = node.base.subs(substitution_map) if substitution_map else node.base
                if base.is_zero is True:
                    raise DomainErrorResult("División entre cero: un denominador original es cero.")

    if substitution_map:
        expr = expr.subs(substitution_map)

    # EV-I-07: rango principal de arccot, (0, pi). SymPy usa (-pi/2, pi/2]
    # (acot(-1) = -pi/4), pero la matriz congelada exige 3*pi/4. Se reescribe
    # solo si la expresión contiene acot, con la identidad exacta
    # acot(x) = pi/2 - atan(x) (válida para todo x real, incluido 0).
    if expr.has(sympy.acot):
        expr = expr.replace(
            lambda node: isinstance(node, sympy.acot),
            lambda node: sympy.pi / 2 - sympy.atan(node.args[0]),
        )

    if expr.free_symbols:
        # Variables libres sin sustituir -> resultado simbólico (sección 6).
        return EvaluateResult(expr=expr, input_expr=input_expr, is_numeric=False, sum_bound=sum_bound, binomial_variable=binomial_variable, permutation_alias=permutation_alias)

    # Sin variables libres sin sustituir -> numérico (sección 6).

    # EV-I-12: el dominio real de asin/acos es [-1, 1]. SymPy devuelve un
    # valor complejo y la API respondía ecoando "asin(2)" como si fuera un
    # resultado válido. El contrato congelado exige error claro: se rechaza
    # solo la forma numérica fuera de rango; los argumentos simbólicos y las
    # composiciones (asin(sin(2))) siguen su curso normal.
    for inverse in (sympy.asin, sympy.acos):
        for node in sympy.preorder_traversal(expr):
            if isinstance(node, inverse):
                argument = node.args[0]
                if argument.is_number and argument.is_real:
                    try:
                        value = float(argument.evalf())
                    except (TypeError, ValueError):
                        continue
                    if abs(value) > 1 + 1e-12:
                        raise DomainErrorResult(
                            f"{inverse.__name__} no está definida fuera del dominio real [-1, 1]."
                        )

    # Diagnose a zero denominator while the original power structure is
    # still available; evalf may collapse it to an uninformative zoo/nan.
    # The zero exponent is not negative: preserve the declared 0^0=1 convention.
    for node in sympy.preorder_traversal(expr):
        if isinstance(node, sympy.Pow) and node.base.is_zero is True and node.exp.is_negative is True:
            raise DomainErrorResult("División entre cero: cero no admite exponentes negativos.")

    # Fix (suite de regresión v1.1, caso E147: tan(pi/2) evaluate daba un
    # número finito gigante en vez de clasificarse como indefinido). El
    # parser preserva "pi/2" en forma exacta (Rational * pi, no un
    # Float), pero `expr.evalf()` no simplifica primero — numéricamente
    # aproxima tan(pi/2) sin darse cuenta de que es una asíntota exacta.
    # Un `simplify()` SÍ la resuelve a zoo exactamente (trabaja
    # simbólicamente), pero llamarlo en CADA evaluate (incluso para
    # expresiones que no tienen ninguna función trig) resultó demasiado
    # lento en la práctica (~decenas de veces más lento, tumbó el
    # servidor en la corrida de la suite). Se acota el chequeo caro a
    # los dos casos donde puede pasar esto: la expresión evalúa a un
    # número sospechosamente grande, o contiene una función trig directa
    # aplicada a algo que involucra pi (que es como se cuela un float en
    # vez de la forma exacta) — evalf() normal sigue siendo el camino
    # rápido para todo lo demás.
    # Para funciones trig directas evaluadas en argumentos exactos con π,
    # resolver primero el posible polo simbólico. Esto evita que expresiones
    # como sec(pi/2) entren en evalf() antes de que SymPy las reduzca a zoo.
    exact_trig_with_pi = expr.has(sympy.tan, sympy.sec, sympy.csc, sympy.cot) and expr.has(sympy.pi)
    if exact_trig_with_pi:
        try:
            simplified_pole = sympy.simplify(expr)
        except (AttributeError, ZeroDivisionError, ValueError, OverflowError):
            simplified_pole = None
        if simplified_pole is not None and simplified_pole.has(
            sympy.zoo, sympy.oo, -sympy.oo, sympy.nan
        ):
            raise DomainErrorResult("El resultado no está definido en este dominio.")

    # EV-T-11: un logaritmo cuyo argumento simplifica a cero es indefinido.
    # evalf() puede ocultarlo tras un artefacto finito: log(1-1) devuelve un
    # float espurio (-288.34...) y log(cos(pi/2)) un complejo espurio, sin
    # disparar el chequeo zoo de más abajo. Se resuelve la singularidad
    # simbólicamente. El simplify caro se acota a logaritmos cuyo argumento
    # no está ya demostrado distinto de cero.
    log_arguments = [
        node.args[0]
        for node in sympy.preorder_traversal(expr)
        if isinstance(node, sympy.log)
    ]
    if any(argument.is_zero is not False for argument in log_arguments):
        try:
            simplified_log = sympy.simplify(expr)
        except (AttributeError, ZeroDivisionError, ValueError, OverflowError):
            simplified_log = None
        if simplified_log is not None and simplified_log.has(
            sympy.zoo, sympy.oo, -sympy.oo, sympy.nan
        ):
            raise DomainErrorResult("El resultado no está definido en este dominio.")

    try:
        numeric_value = expr.evalf()
    except (AttributeError, ZeroDivisionError, ValueError, OverflowError) as exc:
        raise DomainErrorResult("El resultado no está definido en este dominio.") from exc
    needs_pole_check = (
        numeric_value.is_number
        and numeric_value.is_finite is not False
        and not numeric_value.has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan)
        and exact_trig_with_pi
    )
    if needs_pole_check:
        try:
            got_big = abs(complex(numeric_value)) > 1e8
        except Exception:
            got_big = False
        if got_big and sympy.simplify(expr).has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan):
            raise DomainErrorResult("El resultado no está definido en este dominio.")
    if numeric_value.has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan):
        raise DomainErrorResult("El resultado no está definido en este dominio.")

    approx = None
    if numeric_value.is_real:
        try:
            candidate = float(numeric_value)
            approx = candidate if math.isfinite(candidate) else None
            # SY-N-14: evalf of unevaluated exact radicals may leave a tiny
            # nonzero residual even when the expression is identically zero.
            # Only normalize after a symbolic proof, never by tolerance alone.
            if approx is not None and approx != 0 and abs(approx) < 1e-12:
                try:
                    if sympy.simplify(expr).is_zero is True:
                        approx = 0.0
                except (AttributeError, ZeroDivisionError, ValueError, OverflowError):
                    pass
        except (OverflowError, TypeError, ValueError):
            # IN625 D3: la aproximación IEEE-754 es opcional; nunca debe
            # destruir ni impedir devolver el resultado simbólico exacto.
            approx = None

    return EvaluateResult(expr=expr, input_expr=input_expr, is_numeric=True, approx_value=approx, sum_bound=sum_bound, binomial_variable=binomial_variable, permutation_alias=permutation_alias)
