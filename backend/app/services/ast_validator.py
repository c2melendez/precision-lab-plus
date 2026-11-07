"""
app/services/ast_validator.py — Parsing seguro (spec, sección 7), etapas 8-9.

MÓDULO 2B: implementación real. Se ejecuta sobre el `sympy.Expr` producido
por `parsing._parse_side` (etapa 7), inmediatamente después de `parse_expr`.
"""

from typing import Set, Type

import sympy

MAX_AST_NODES = 200
MAX_AST_DEPTH = 30
MAX_INTEGER_LITERAL_DIGITS = 64
MAX_ABS_INTEGER_EXPONENT = 10_000


class ComplexityLimitError(ValueError):
    """Se excede alguno de los límites de la etapa 9 (sección 7) — se
    traduce a `ErrorCode.COMPLEXITY_LIMIT` en el router/servicio que llama.

    Separada de `ParseSecurityError` (parsing.py) a propósito: ambas se
    mapean a `ErrorCode` distintos (`COMPLEXITY_LIMIT` vs `PARSE_ERROR`,
    sección 4) y el llamador necesita poder distinguirlas sin parsear el
    mensaje (decisión DEDUCIBLE, Módulo 2A/2B).
    """


# Tipos de nodo de SymPy que la etapa 8 rechaza explícitamente (sección 7):
# Lambda, Derivative, Integral, Sum, Product, Limit, Matrix. "Function no
# reconocida" y "acceso a atributos" se validan aparte (ver
# `validate_ast_safety`): la primera contra `parsing.ALLOWED_FUNCTIONS` por
# tipo de clase, la segunda ya la bloquea `parsing.validate_decimal_and_
# reject_scientific` (etapa 4) al no dejar sobrevivir ningún '.' que no sea
# 'dígito.dígito' — ningún nodo de acceso a atributos llega a existir en el
# árbol de SymPy resultante.
BLOCKED_NODE_TYPES: Set[Type[sympy.Basic]] = {
    sympy.Lambda,
    sympy.Derivative,
    sympy.Integral,
    sympy.Sum,
    sympy.Product,
    sympy.Limit,
    sympy.MatrixBase,
    # sympy.Tuple: cubre un vector real encontrado en el testing del Módulo
    # 2B, no anticipado por la spec — cuando un identificador NO reconocido
    # como función (ej. "foo", "Integral") va seguido de paréntesis con
    # contenido separado por comas ("foo()", "Integral(x,x)"), SymPy no
    # lanza una excepción: la transformación de multiplicación implícita
    # deja pasar un `sympy.Tuple` "colado" dentro de un `Mul`
    # (`Mul(Symbol('foo'), Tuple())`, con warning de deprecación de SymPy).
    # Sin este tipo bloqueado, "foo()" e "Integral(x,x)" (ambos listados en
    # la sección 7 como ejemplos que DEBEN producir PARSE_ERROR) pasaban
    # silenciosamente. Decisión DEDUCIBLE, registrada en el cierre.
    sympy.Tuple,
}


def validate_ast_safety(tree: sympy.Basic) -> None:
    """Etapa 8 (sección 7): recorre el árbol resultante y rechaza `Lambda`,
    `Function` no reconocida, `Derivative`, `Integral`, `Sum`, `Product`,
    `Limit`, `Matrix`. Lanza `ParseSecurityError` si encuentra alguno.

    Ejemplos de la sección 7 cubiertos: `Integral(x,x)`,
    `Derivative(x**2,x)`, `Function('f')(x)` — este último nunca produce
    una `Function` de SymPy real porque `Function` no está en
    `ALLOWED_FUNCTIONS` ni en `global_dict_minimo`; se clasifica como
    `Symbol('Function')` (etapa 6) y la llamada `Symbol(...)('f')(x)` falla
    en `parse_expr` con un `TypeError` (objeto no invocable), ya capturado
    como `ParseSecurityError` antes de llegar aquí. Esta función es, para
    ese caso, una segunda capa de defensa.
    """
    # Import diferido: evita el ciclo `parsing -> ast_validator -> parsing`.
    from app.services.parsing import ALLOWED_FUNCTIONS, ParseSecurityError

    allowed_function_classes = tuple(
        cls for cls in ALLOWED_FUNCTIONS.values() if isinstance(cls, type)
    )

    for node in sympy.preorder_traversal(tree):
        for blocked_type in BLOCKED_NODE_TYPES:
            if isinstance(node, blocked_type):
                raise ParseSecurityError(
                    f"Construcción no permitida en la expresión: '{type(node).__name__}'."
                )
        if isinstance(node, sympy.Function) and not isinstance(node, allowed_function_classes):
            raise ParseSecurityError(f"Función no reconocida: '{node.func.__name__}'.")


def _bounded_integer_value(node: sympy.Basic, limit: int) -> int | None:
    """Evalúa aritmética entera pequeña sin construir torres de potencias.

    Devuelve None si no puede demostrar que el valor está dentro de `limit`.
    Se usa para exponentes numéricos expresados como AST (p. ej. 10**10),
    que no son `Integer` aunque representan un entero.
    """
    if node.is_Integer:
        value = int(node)
        return value if abs(value) <= limit else None

    if node.is_Add:
        values = [_bounded_integer_value(arg, limit) for arg in node.args]
        if any(value is None for value in values):
            return None
        total = sum(value for value in values if value is not None)
        return total if abs(total) <= limit else None

    if node.is_Mul:
        result = 1
        for arg in node.args:
            value = _bounded_integer_value(arg, limit)
            if value is None:
                return None
            result *= value
            if abs(result) > limit:
                return None
        return result

    if node.is_Pow:
        base_node, exponent_node = node.args
        base = _bounded_integer_value(base_node, limit)
        exponent = _bounded_integer_value(exponent_node, limit)
        if base is None or exponent is None:
            return None
        if exponent < 0:
            if base == 1:
                return 1
            if base == -1:
                return -1 if abs(exponent) % 2 else 1
            return None
        if exponent == 0:
            return 1
        if base in (0, 1):
            return base
        if base == -1:
            return -1 if exponent % 2 else 1
        result = 1
        factor = base
        remaining = exponent
        while remaining:
            if remaining & 1:
                result *= factor
                if abs(result) > limit:
                    return None
            remaining >>= 1
            if remaining:
                factor *= factor
                if abs(factor) > limit:
                    factor = limit + 1
        return result

    return None


def check_complexity_limits(expr: sympy.Basic) -> None:
    """Etapa 9 (sección 7): nodos ≤ 200, profundidad ≤ 30, dígitos máximos
    por entero literal ≤ 64, exponente entero absoluto máximo ≤ 10,000.
    Exceder cualquiera -> `ComplexityLimitError`.

    Caso de prueba de la sección 15: `2**100000000` -> `COMPLEXITY_LIMIT`
    (el exponente, 100000000, excede `MAX_ABS_INTEGER_EXPONENT`; el árbol
    en sí, con `evaluate=False`, tiene solo 3 nodos — nunca se llega a
    calcular el número real de ~30 millones de dígitos).
    """

    def _walk(node: sympy.Basic, depth: int, counters: dict) -> None:
        counters["nodes"] += 1
        if counters["nodes"] > MAX_AST_NODES:
            raise ComplexityLimitError(f"La expresión excede el máximo de {MAX_AST_NODES} nodos.")
        if depth > MAX_AST_DEPTH:
            raise ComplexityLimitError(
                f"La expresión excede la profundidad máxima de {MAX_AST_DEPTH}."
            )

        if node.is_Integer:
            digit_count = len(str(abs(int(node))))
            if digit_count > MAX_INTEGER_LITERAL_DIGITS:
                raise ComplexityLimitError(
                    f"Literal entero con demasiados dígitos (máx. "
                    f"{MAX_INTEGER_LITERAL_DIGITS}): {digit_count}."
                )

        if node.is_Pow:
            _base, exponent = node.args
            # Las expresiones anidadas como 10**(10**10) tienen un exponente
            # entero, aunque su nodo raíz no sea sympy.Integer. Evaluamos solo
            # aritmética pequeña con un tope; si excede el rango o no puede
            # acotarse sin expandirla, se rechaza antes de evalf/simplify.
            if exponent.is_number and exponent.is_integer is True:
                exponent_value = _bounded_integer_value(
                    exponent, MAX_ABS_INTEGER_EXPONENT
                )
                if exponent_value is None or abs(exponent_value) > MAX_ABS_INTEGER_EXPONENT:
                    raise ComplexityLimitError(
                        f"Exponente entero fuera de rango (máx. "
                        f"{MAX_ABS_INTEGER_EXPONENT} en valor absoluto): {exponent}."
                    )

        for child in node.args:
            _walk(child, depth + 1, counters)

    _walk(expr, 0, {"nodes": 0})
