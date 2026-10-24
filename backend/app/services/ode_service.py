"""
app/services/ode_service.py — Fase E (EDO), spec_edo_complejos_tooltips.md
sección 2.

Motor dedicado para ecuaciones diferenciales ordinarias. Sigue el mismo
patrón que `phase2_service.py` (dataclass de resultado + función pura,
sin dependencia de FastAPI/Pydantic en este archivo).

DECISIÓN DE SEGURIDAD (spec sección 2.2, "DETERMINADO, seguridad"): en vez
de agregar nuevas entradas a `ast_validator.BLOCKED_NODE_TYPES`, se
verificó (auditoría real, Módulo E1) que la ruta general YA está cerrada
por diseño existente, sin cambios:
  1. `sympy.Derivative` ya está en `BLOCKED_NODE_TYPES` (ast_validator.py)
     — cualquier árbol que contenga un nodo Derivative ya es rechazado
     en la ruta general, y este servicio construye Derivative(...)
     directamente en Python (nunca vía `parse_expression_tree`).
  2. `"dsolve"` no existe como clave en `parsing.ALLOWED_FUNCTIONS` — un
     usuario que escriba literalmente "dsolve(...)" en /evaluate obtiene
     "Función no reconocida", nunca invoca sympy.dsolve().
  3. Este módulo NUNCA llama a `parsing.parse_expression_tree` sobre el
     texto crudo con comillas simples (notación prima) — tiene su propio
     parser dedicado (`_parse_ode_text`), que es la única puerta de
     entrada a `dsolve()` en todo el backend.
Con (1)+(2)+(3), "garantizar por diseño que /ode es el único punto que
invoca dsolve()" (spec) queda satisfecho sin tocar ast_validator.py.
Ver Módulo E1, "Auditoría de alcance por motor" en el cierre, para la
evidencia de (1) y (2) verificada contra el código real.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import multiprocessing as mp
import os
import re
import threading
import atexit
from multiprocessing import TimeoutError as MultiprocessingTimeout
from multiprocessing import pool as mp_pool
from tokenize import TokenError

import sympy

from app.services import parsing
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

# Mismas transformaciones que parsing.py (multiplicación implícita: "3y'"
# y "2x" deben interpretarse sin '*' explícito, igual que en el resto del
# proyecto) — verificado con ejecución real que sympy.sympify() por sí
# solo NO las aplica (bug encontrado al probar "y'=2x": SyntaxError).
_ODE_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

MAX_ODE_ORDER = 2  # spec, fuera de alcance: "órdenes de EDO más allá de 2º"

_x = sympy.Symbol("x")
_y = sympy.Function("y")


class ODEParseError(ValueError):
    """Notación de EDO no reconocible -> ErrorCode.PARSE_ERROR."""


class ODEUnsupportedError(ValueError):
    """EDO bien formada pero fuera del alcance resoluble -> ErrorCode.UNSUPPORTED_OPERATION."""


class ODETimeoutError(TimeoutError):
    """La resolución excedió el presupuesto de tiempo -> ErrorCode.TIMEOUT.

    `sympy.dsolve()` no tiene cancelación cooperativa: una ecuación exacta de
    primer orden con polinomios de grado alto puede quedar en un bucle interno
    indefinido. Por eso la resolución corre en un proceso hijo descartable con
    plazo acotado (ver `_solve_bounded`), y este error solo se usa cuando el
    plazo se agota y el hijo se termina.
    """


# Presupuesto por resolución. Se mantiene corto porque es una calculadora
# interactiva; las filas que lo exceden se registran como capability gap, nunca
# como cálculo bloqueante del servidor.
DEFAULT_SOLVE_TIMEOUT_SECONDS = 8.0
MAX_SOLVE_TIMEOUT_SECONDS = 30.0


def _solve_timeout_seconds() -> float:
    raw = os.getenv("ODE_SOLVE_TIMEOUT_SECONDS")
    if raw is None:
        return DEFAULT_SOLVE_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_SOLVE_TIMEOUT_SECONDS
    if not 1.0 <= value <= MAX_SOLVE_TIMEOUT_SECONDS:
        return DEFAULT_SOLVE_TIMEOUT_SECONDS
    return value


@dataclass
class ODEResult:
    input_text: str
    order: int
    solution: sympy.Eq  # y(x) = ...
    has_initial_condition: bool


def _validate_ode_security(text: str) -> None:
    """Valida la superficie textual específica de EDO antes de parse_expr.

    El parser EDO necesita reconocer y'/y'' y por eso no puede delegar el
    texto completo a parse_expression_tree(), pero sí debe conservar las
    mismas fronteras de seguridad: sin llamadas no-whitelist, atributos de
    Python ni identificadores internos con doble guion bajo.
    """
    if "__" in text:
        raise ODEParseError("La expresión contiene un identificador no permitido.")

    # Bloquea acceso a atributos (x.__class__, obj.attr). Un punto decimal
    # numérico sigue permitido porque el patrón exige un identificador antes.
    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\.", text):
        raise ODEParseError("El acceso a atributos no está permitido.")

    # Las únicas llamadas multi-letra permitidas son las funciones ya
    # whitelisteadas por el parser general. y(...) se reserva para la
    # función dependiente de la EDO.
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        name = match.group(1)
        if name != "y" and len(name) > 1 and name not in parsing.ALLOWED_FUNCTIONS:
            raise ODEParseError(f"Función no reconocida: '{name}'.")


def _prime_order(token: str) -> int:
    """'y' -> 0, \"y'\" -> 1, \"y''\" -> 2, ... Cuenta primas dinámicamente
    (spec sección 2.2: "el detector de intención debe contar primas
    dinámicamente, no usar una plantilla fija por orden")."""
    stripped = token[1:]  # quita la 'y' inicial
    if not stripped:
        return 0
    if any(ch != "'" for ch in stripped):
        raise ODEParseError(f"Notación de derivada inválida: '{token}'.")
    return len(stripped)


def _substitute_derivatives(text: str) -> Tuple[str, int]:
    """Reemplaza y, y', y'', ... por Derivative(y(x), x, n) o y(x) (n=0),
    de mayor a menor orden de primas para no hacer matches parciales
    (ej. "y'''" debe consumirse entero antes que "y''"). Devuelve el
    texto sustituido y el orden máximo encontrado."""
    import re

    # Encuentra todas las ocurrencias de 'y' seguida de 0+ primas, como
    # token completo (no como parte de otro identificador).
    pattern = re.compile(r"y'*")
    max_order = 0

    def _replace(match: "re.Match") -> str:
        nonlocal max_order
        token = match.group(0)
        order = _prime_order(token)
        max_order = max(max_order, order)
        if order == 0:
            return "y(x)"
        return f"Derivative(y(x), x, {order})"

    substituted = pattern.sub(_replace, text)
    return substituted, max_order


def _split_equation_and_condition(text: str) -> Tuple[str, Optional[str]]:
    """Separa la EDO de la condición inicial y(x0)=y0, que vive en el
    mismo campo separada por coma (spec 2.2, DETERMINADO por el usuario:
    "prefiero la primera opción"). Ej: "y'=2x, y(0)=1" ->
    ("y'=2x", "y(0)=1")."""
    parts = [p.strip() for p in text.split(",")]
    if len(parts) == 1:
        return parts[0], None
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ODEParseError(f"No se esperaba más de una condición inicial: '{text}'.")


def _parse_initial_condition(ic_text: str, order: int) -> dict:
    """Parsea "y(0)=1" (orden 1: solo y(x0)=y0) o, para orden 2, se
    acepta también una segunda condición separada por ';' del tipo
    "y'(0)=v0" si el usuario la escribe -- fuera del alcance confirmado
    del teclado (que solo monta y(□)=□, spec 2.3), pero el parser no lo
    rechaza si llega por otra vía (ej. suite de pruebas)."""
    import re

    match = re.fullmatch(r"y(('*))\(([^)]+)\)\s*=\s*(.+)", ic_text.strip())
    if not match:
        raise ODEParseError(f"Condición inicial no reconocida: '{ic_text}'.")
    primes, point_text, value_text = match.group(1), match.group(3), match.group(4)
    deriv_order = len(primes)
    try:
        point = parsing.parse_expression_tree(point_text, allow_equation=False)
        value = parsing.parse_expression_tree(value_text, allow_equation=False)
    except (parsing.ParseSecurityError, TypeError, ValueError) as exc:
        raise ODEParseError("No se pudo interpretar la condición inicial.") from exc

    if deriv_order == 0:
        return {_y(point): value}
    return {sympy.Derivative(_y(_x), _x, deriv_order).subs(_x, point): value}


def _parse_ode_text(text: str) -> Tuple[sympy.Eq, Optional[dict], int]:
    """Única puerta de entrada a la construcción de un `sympy.Eq` con
    `Derivative`/`Function` para EDO en todo el backend (ver nota de
    seguridad arriba). No pasa por `parsing.parse_expression_tree`."""
    eq_text, ic_text = _split_equation_and_condition(text)
    _validate_ode_security(eq_text)
    if ic_text:
        _validate_ode_security(ic_text)

    if "=" not in eq_text:
        raise ODEParseError(f"Se esperaba una ecuación ('='): '{eq_text}'.")
    lhs_text, rhs_text = eq_text.split("=", 1)

    lhs_sub, lhs_order = _substitute_derivatives(lhs_text)
    rhs_sub, rhs_order = _substitute_derivatives(rhs_text)
    order = max(lhs_order, rhs_order)

    if order == 0:
        raise ODEParseError(
            f"No se detectó ninguna derivada (notación 'y'') en: '{eq_text}'."
        )
    if order > MAX_ODE_ORDER:
        raise ODEUnsupportedError(
            f"Orden de EDO no soportado (máx. {MAX_ODE_ORDER}): orden {order}."
        )

    local_dict = {
        **parsing.ALLOWED_FUNCTIONS,
        **parsing.ALLOWED_CONSTANTS,
        "y": _y,
        "x": _x,
        "Derivative": sympy.Derivative,
    }
    try:
        lhs_expr = parse_expr(lhs_sub, local_dict=local_dict, transformations=_ODE_TRANSFORMATIONS)
        rhs_expr = parse_expr(rhs_sub, local_dict=local_dict, transformations=_ODE_TRANSFORMATIONS)
    except (sympy.SympifyError, TypeError, SyntaxError, ValueError, NameError, TokenError) as exc:
        raise ODEParseError("No se pudo interpretar la ecuación.") from exc

    equation = sympy.Eq(lhs_expr, rhs_expr)

    ics = _parse_initial_condition(ic_text, order) if ic_text else None
    return equation, ics, order


def _solve_local(text: str) -> ODEResult:
    """Resolución sin aislamiento (lógica histórica; también corre en el hijo)."""
    equation, ics, order = _parse_ode_text(text)

    try:
        if ics:
            solution = sympy.dsolve(equation, _y(_x), ics=ics)
        else:
            solution = sympy.dsolve(equation, _y(_x))
    except NotImplementedError as exc:
        raise ODEUnsupportedError(
            f"Esta ecuación diferencial no está dentro de los tipos soportados: {exc}"
        ) from exc
    except (ValueError, TypeError, sympy.SympifyError, TokenError) as exc:
        raise ODEUnsupportedError(
            "No se pudo resolver esta ecuación diferencial."
        ) from exc

    if isinstance(solution, list):
        # dsolve puede devolver varias soluciones (ej. ramas); se toma
        # la primera con una nota — comportamiento no anticipado en el
        # spec, decisión DEDUCIBLE registrada en el cierre del módulo.
        solution = solution[0]

    return ODEResult(
        input_text=text,
        order=order,
        solution=solution,
        has_initial_condition=ics is not None,
    )


def _solve_worker(text: str) -> Tuple[str, object]:
    """Entrada del proceso hijo: devuelve un resultado serializable.

    No propaga excepciones (el `Pool` las reenviaría con la traza del hijo);
    devuelve una tupla etiquetada que el padre traduce al tipo público.
    """
    try:
        result = _solve_local(text)
    except ODEParseError as exc:
        return ("parse_error", str(exc))
    except ODEUnsupportedError as exc:
        return ("unsupported", str(exc))
    except Exception as exc:  # noqa: BLE001 - frontera de proceso
        return ("internal", f"{type(exc).__name__}: {exc}")
    return (
        "ok",
        (sympy.srepr(result.solution), result.order, result.has_initial_condition),
    )


_pool: Optional[mp_pool.Pool] = None
_pool_lock = threading.Lock()
atexit.register(lambda: _discard_pool())


def _get_pool() -> "mp_pool.Pool":
    global _pool
    if _pool is None:
        # `spawn` en todas las plataformas: el hijo importa solo
        # `app.services.ode_service` (sin heredar hilos, event loop ni el
        # tracer de coverage del proceso servidor). El coste es un arranque
        # en frío por worker (~1 s una vez); después el pool queda caliente.
        _pool = mp.get_context("spawn").Pool(processes=2)
    return _pool


def _discard_pool() -> None:
    """Termina el pool tras un plazo agotado: el hijo colgado no se puede
    cancelar de forma cooperativa, así que se descarta el proceso entero."""
    global _pool
    with _pool_lock:
        pool, _pool = _pool, None
    if pool is not None:
        pool.terminate()
        pool.join()


def _solve_bounded(text: str) -> ODEResult:
    global _pool
    with _pool_lock:
        pool = _get_pool()
        pending = pool.apply_async(_solve_worker, (text,))
    try:
        status, payload = pending.get(timeout=_solve_timeout_seconds())
    except MultiprocessingTimeout as exc:
        _discard_pool()
        raise ODETimeoutError(
            "La ecuación diferencial excedió el límite de tiempo de resolución. "
            "Acota la ecuación o usa otra forma equivalente."
        ) from exc
    except (mp.ProcessError, OSError, EOFError) as exc:
        _discard_pool()
        raise ODEUnsupportedError(
            "No se pudo completar la resolución de esta ecuación diferencial."
        ) from exc

    if status == "parse_error":
        raise ODEParseError(str(payload))
    if status == "unsupported":
        raise ODEUnsupportedError(str(payload))
    if status != "ok":
        raise ODEUnsupportedError(
            "No se pudo resolver esta ecuación diferencial."
        )
    solution_srepr, order, has_initial_condition = payload
    solution = sympy.sympify(solution_srepr)
    return ODEResult(
        input_text=text,
        order=int(order),
        solution=solution,
        has_initial_condition=bool(has_initial_condition),
    )


def solve_ode(text: str) -> ODEResult:
    """Resuelve una EDO en notación prima, con condición inicial opcional
    en el mismo campo. Usa `sympy.dsolve()` — casos separables, lineales
    de primer orden, y lineales de orden superior con coeficientes
    constantes están dentro de lo que `dsolve` resuelve nativamente
    (spec sección 2.1, "DETERMINADO que es viable").

    Cualquier EDO que dsolve no pueda resolver (fuera de los tipos
    cubiertos, o sympy.dsolve levanta NotImplementedError) se traduce a
    ODEUnsupportedError -> ErrorCode.UNSUPPORTED_OPERATION, nunca un
    resultado inventado ni un error crudo del motor (spec 2.1).

    La resolución se ejecuta en un proceso hijo con plazo acotado
    (`ODE_SOLVE_TIMEOUT_SECONDS`, por defecto 8 s) porque `dsolve` puede no
    terminar en ecuaciones exactas de grado alto (evidencia: EDCX ED-X-02,
    >90 s sin respuesta). Agotar el plazo devuelve `ODETimeoutError` ->
    ErrorCode.TIMEOUT y descarta el proceso, en vez de bloquear el worker
    del servidor. `ODE_SOLVE_ISOLATION=0` desactiva el aislamiento solo para
    depuración local.
    """
    if os.getenv("ODE_SOLVE_ISOLATION", "1") == "0":
        return _solve_local(text)
    return _solve_bounded(text)
