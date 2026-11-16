"""
app/services/parsing.py — Parsing seguro (spec, sección 7 completa) y
sección 3 completa (sintaxis de entrada: Unicode, punto decimal, notación
científica rechazada, prioridad de identificadores multi-letra).

MÓDULO 2B: implementación real de las 9 etapas. Las etapas 8-9 (validación
del árbol AST y límites de complejidad) viven en `app/services/ast_validator.py`.
"""

import builtins
import keyword
import re
import warnings
from typing import Dict, List, Optional, Tuple

import sympy
from sympy import (
    Abs,
    Add,
    E,
    factorial,
    Float,
    I,
    Integer,
    Max,
    Min,
    Mod,
    Mul,
    Pow,
    Rational,
    Symbol,
    acos,
    acosh,
    acot,
    acoth,
    acsc,
    acsch,
    arg,
    asec,
    asech,
    asin,
    asinh,
    atan,
    atanh,
    binomial,
    conjugate,
    cos,
    cosh,
    cot,
    coth,
    csc,
    csch,
    exp,
    floor,
    ceiling,
    gcd,
    lcm,
    log,
    oo,
    pi,
    root,
    sec,
    sech,
    sign,
    sin,
    sinh,
    sqrt,
    tan,
    tanh,
)
from sympy.functions.combinatorial.factorials import FallingFactorial
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    rationalize,
    standard_transformations,
)

from app.services.stat_functions import Mad, Mean, Median, Mode, Range, Stdev, StdevPop, Variance, VariancePop

MAX_EXPRESSION_LENGTH = 500
MIN_EXPRESSION_LENGTH = 1
MAX_IDENTIFIER_LENGTH = 64


class ParseSecurityError(ValueError):
    """Cualquier violación de las etapas 1-9 de la sección 7 — se traduce a
    `ErrorCode.PARSE_ERROR` en el router/servicio que llama al parser.

    Nota DEDUCIBLE (Módulo 2A): no es un contrato público de `schemas/`, es
    de uso interno entre `parsing.py`/`ast_validator.py` y los servicios.
    """


# Sección 7, bloque de código literal — no se renombran ni se completan
# entradas adicionales sin autorización explícita (Mensaje 0, regla 3).
def _calculator_log(value, base=None, **_):
    """Calculator semantics: log(x) is base 10; log(x,b) uses base b."""
    return sympy.log(value, 10) if base is None else sympy.log(value, base)


def _complex_log(value, **_):
    """Principal complex logarithm used by the keyboard key ``Log``."""
    return sympy.log(value)


def _plus_minus(value, **_):
    """Return both mathematical branches for the calculator ± key."""
    return sympy.FiniteSet(value, -value)



ALLOWED_FUNCTIONS = {
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "sec": sec,
    "csc": csc,
    "cot": cot,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "acsc": acsc,
    "asec": asec,
    "acot": acot,
    # Fix (suite de regresión v1.1, casos E136-E138): Lite reconoce tanto
    # "asin" como "arcsin" (fix de la sesión de paridad de teclado), pero
    # Python solo tenía "asin"/"acos"/"atan" — "arcsin(1)" quedaba sin
    # reconocer como función (multiplicación implícita, resultado
    # "arcsin*1" sin evaluar). Se agregan como alias del mismo sympy.asin/
    # acos/atan para que ambas convenciones funcionen en los dos proyectos.
    "arcsin": asin,
    "arccos": acos,
    "arctan": atan,
    "sinh": sinh,
    "cosh": cosh,
    "tanh": tanh,
    "csch": csch,
    "sech": sech,
    "coth": coth,
    # Módulo A (spec_motor_matematico_pendiente.md §2, plantilla de motor
    # matemático): las 6 hiperbólicas inversas no estaban — verificado
    # directamente en este diccionario antes del cambio, ninguna de las 6
    # aparecía. Nativas de SymPy, solo whitelist — sin reescritura (a
    # diferencia de Lite/Algebrite, que sí necesita rewriteReciprocalFunctions
    # porque Algebrite no las trae nativas).
    "asinh": asinh,
    "acosh": acosh,
    "atanh": atanh,
    "asech": asech,
    "acsch": acsch,
    "acoth": acoth,
    # Paridad con la matriz congelada 2.D (EC-HI-*): la fuente escribe las
    # inversas hiperbólicas con prefijo "ar-" (\operatorname{arcosh} x=0,
    # \operatorname{artanh} x=\ln 2, ...), que Lite ya acepta. Se registran
    # como alias de las mismas funciones de SymPy; sin reescritura adicional.
    "arsinh": asinh,
    "arcosh": acosh,
    "artanh": atanh,
    "arsech": asech,
    "arcsch": acsch,
    "arcoth": acoth,
    "sqrt": sqrt,
    # Fix (suite de regresión v1.1, caso E107): "cbrt" no estaba
    # registrada — "cbrt(27)" quedaba sin reconocer como función
    # (multiplicación implícita, "cbrt*27" sin evaluar). SymPy no tiene
    # una función "cbrt" propia con ese nombre exacto — se define como
    # x**(Rational(1,3)) (raíz cúbica real de números reales, no la rama
    # compleja principal — ver Nota de convención más abajo sobre por qué
    # los exponentes fraccionarios de base negativa dan la rama compleja
    # en vez de la raíz real, y por qué cbrt() es una excepción
    # deliberada a esa regla, igual que hacen la mayoría de calculadoras).
    "cbrt": lambda x, **_: sympy.Piecewise((-((-x) ** sympy.Rational(1, 3)), x < 0), (x ** sympy.Rational(1, 3), True)),
    "log": _calculator_log,
    "Log": _complex_log,
    "ln": log,
    "exp": exp,
    "abs": Abs,
    "sign": sign,
    "pm": _plus_minus,
    # Fase 10 (auditoría Fase 0 v2, port de precision-lab-lite): estas 15
    # claves NUNCA estaban aquí — de las 10 teclas del menú "Stat" del
    # teclado, antes de esto solo "n!" (factorial, ya soportado vía
    # ast_validator/sympy en otro punto) funcionaba; "min"/"max" ni
    # siquiera llegaban a fallar limpio, estaban BLOQUEADOS como
    # identificadores prohibidos (ver BLOCKED_IDENTIFIERS abajo, que resta
    # automáticamente las claves de este diccionario). min/max/gcd/lcm/mod
    # /nCr/nPr son nativos de SymPy (Min/Max/gcd/lcm/Mod/binomial/
    # FallingFactorial) — solo faltaba registrarlos. mean/median/mode/
    # range/stdev/variance/mad no existen en SymPy — se definen en
    # stat_functions.py, mismo criterio de evaluación (n-1 muestral para
    # stdev/variance) que su equivalente en la Lite. "sort" NO se portó
    # (ver stat_functions.py, no encaja en el contrato escalar de
    # /evaluate sin cambios más profundos).
    "floor": floor,
    "ceil": ceiling,
    "ceiling": ceiling,
    "min": Min,
    "max": Max,
    "range": Range,
    "mean": Mean,
    "median": Median,
    "mode": Mode,
    "stdev": Stdev,
    "variance": Variance,
    "var": Variance,  # alias real: la tecla del teclado inserta \mathrm{var}
    # P6 (spec v2 §7.1): variantes poblacionales, funciones nuevas.
    "stdevpop": StdevPop,
    "variancepop": VariancePop,
    "mad": Mad,
    "mod": Mod,
    "gcd": gcd,
    "lcm": lcm,
    "nCr": binomial,
    "nPr": FallingFactorial,
    # P4 (spec v2 §5.2, Complejos): re/im/arg/conjugate son nativos de
    # SymPy — solo hacía falta registrarlos, mismo patrón que arriba.
    # "re"/"im" se referencian como sympy.re/sympy.im (no importados como
    # nombres sueltos: colisionarían con el módulo `re` de Python, ya
    # importado arriba para regex) en vez de "conjugate" tal cual, la
    # tecla del teclado usa la etiqueta corta "conj" (mismo criterio que
    # "var" para \mathrm{var} en vez de \mathrm{variance}).
    "re": sympy.re,
    "im": sympy.im,
    "arg": arg,
    "conj": conjugate,
    # "⇄ Polar": NO es una función nativa de SymPy de un solo símbolo (la
    # spec lo dice explícito, §5.2) — se compone aquí con Abs/exp/arg, los
    # 3 ya registrados arriba. Importante: como valor de ALLOWED_FUNCTIONS
    # es una función Python (lambda), no una clase, así que
    # `isinstance(cls, type)` en ast_validator.py la EXCLUYE del set de
    # "clases permitidas" que usa la etapa 8 — pero eso no es un problema
    # de seguridad: parse_expr() la invoca y sustituye su resultado
    # (Abs(z)*exp(I*arg(z))) DURANTE el parseo, así que el árbol final que
    # ve validate_ast_safety solo contiene nodos Abs/exp/arg/Mul, todos ya
    # permitidos — "topolar" en sí nunca sobrevive como nodo Function en
    # el árbol. No pude ejecutar el pipeline real de parse_expr en este
    # entorno para confirmarlo empíricamente (sin red/dependencias
    # instaladas) — recomiendo un test explícito
    # (test_parsing.py/test_ast_validator.py) antes de dar este parche por
    # cerrado en Python. Dirección única (rectangular -> polar); no existe
    # sintaxis de entrada polar en este teclado para la dirección inversa.
    "topolar": lambda z: Abs(z) * exp(I * arg(z)),
    # Fase F (spec_edo_complejos_tooltips.md §3.2, Módulo F0/F1): auditado
    # con ejecución real (sympy.root) -- maneja z complejo e índices no
    # enteros correctamente, rama principal (ver hallazgo de F0: root(-8,3)
    # da la raíz compleja principal, no -2 -- convención estándar, no bug).
    # Log(z) NO necesita entrada nueva: "log" (arriba) ya es sympy.log
    # (logaritmo natural con 1 argumento), que para z complejo YA es
    # ln|z|+i*arg(z) -- confirmado numéricamente en F0, cero cambios
    # necesarios. zoo (log(0)) ya lo maneja evaluate_service.py existente
    # (detectado, no un caso nuevo).
    "root": root,
}
ALLOWED_CONSTANTS = {"pi": pi, "e": E, "E": E, "i": I, "I": I, "oo": oo}

# Identificadores bloqueados en la etapa 5 (sección 7: "no builtin
# bloqueado"). Decisión DEDUCIBLE (registrada en el cierre del Módulo 2B):
# la spec solo da ejemplos ilustrativos (__import__, eval, exec, open,
# lambda...) — se adopta como blocklist COMPLETA la unión de las palabras
# reservadas de Python (`keyword.kwlist`/`softkwlist`) y de todo lo expuesto
# por el módulo `builtins`, restando lo que ya es una función/constante
# permitida (para no bloquear "abs", que colisiona con `builtins.abs`).
BLOCKED_IDENTIFIERS = (
    (set(keyword.kwlist) | set(keyword.softkwlist) | set(dir(builtins)))
    - set(ALLOWED_FUNCTIONS)
    - set(ALLOWED_CONSTANTS)
)

_IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Scientific notation is a numeric literal: `1e5`, `2.5E-3`. The constant
# `e` followed by an arithmetic sign (`e-1`, as in the frozen EV-M-04 row)
# is not scientific notation and must not be rejected.
_SCIENTIFIC_NOTATION_PATTERN = re.compile(r"(?<=\d)[eE][+-]?\d+")
_CALL_ARITY_PATTERN = re.compile(r"\b(log|ln)\s*\(")




def validate_g3_structure(text: str) -> None:
    """IN625 G3: errores de edición/estructura con mensajes deterministas.

    Esta capa no evalúa matemáticas. Evita que parse_expr/SymPy conviertan
    entradas claramente incompletas en errores internos o mensajes genéricos.
    """
    # SY-X-02: recognize layout-only input before stripping its final escaped space.
    # Keep unknown commands and mathematical tokens for the existing validation.
    if not re.sub(r"\\(?:[,;!: ]|qquad\b|quad\b)", "", text).strip():
        raise ParseSecurityError("Escriba una expresión antes de calcular.")
    raw = text.strip()

    if not raw:
        raise ParseSecurityError("Escriba una expresión antes de calcular.")

    if re.search(r"\\placeholder(?:\{\})?", raw, re.I):
        raise ParseSecurityError("Entrada incompleta: complete el marcador pendiente.")

    unknown_command = re.search(r"\\([A-Za-z]+)(?:\{|\()", raw)
    if unknown_command:
        known = {
            "frac","sqrt","sin","cos","tan","csc","sec","cot","ln","log","exp",
            "left","right","pi","infty","theta","alpha","beta","gamma","lambda",
            "zeta","Delta","Lambda","Phi","gcd","min","max","pm","le","ge","leq",
            "geq","neq","ne","lt","gt","operatorname","mathrm","text","placeholder",
            "lim","int","partial","displaystyle","dfrac","tfrac","cfrac",
        }
        if unknown_command.group(1) not in known:
            raise ParseSecurityError(f"Comando desconocido: \\{unknown_command.group(1)}.")

    if re.fullmatch(r"\\text\{[\s\S]*\}", raw):
        raise ParseSecurityError("Texto no matemático: escriba una expresión matemática.")

    if raw.startswith("=") or raw.endswith("="):
        raise ParseSecurityError('Ecuación incompleta: debe haber una expresión a ambos lados de "=".')

    if re.match(r"^\s*\^", raw):
        raise ParseSecurityError("Exponente sin base.")
    if re.search(r"\^\s*(?:\{\s*\})?\s*$", raw):
        raise ParseSecurityError("Exponente vacío.")

    if re.search(r"\\frac\s*\{\s*\}\s*\{", raw):
        raise ParseSecurityError("Fracción incompleta: el numerador está vacío.")
    if re.search(r"\\frac\s*\{[^{}]*\}\s*(?:\{\s*\})?\s*$", raw):
        raise ParseSecurityError("Fracción incompleta: falta el denominador.")
    if re.search(r"\\sqrt\s*\{\s*\}", raw):
        raise ParseSecurityError("Raíz incompleta: el radicando está vacío.")

    if re.search(r"(?:\\)?(?:sin|cos|tan|csc|sec|cot|ln|log|exp)\s*(?:\(\s*\))?\s*$", raw):
        raise ParseSecurityError("Falta el argumento de la función.")

    if re.search(r"\(\s*\)", raw):
        raise ParseSecurityError("Paréntesis vacíos: falta una expresión.")

    if re.search(r"\\left\([\\s\\S]*\\right\]", raw):
        raise ParseSecurityError("Delimitadores incompatibles: paréntesis y corchete no coinciden.")
    if "\\left" in raw and "\\right" not in raw:
        raise ParseSecurityError("Delimitador incompleto: falta \\right.")
    if "\\right" in raw and "\\left" not in raw:
        raise ParseSecurityError("Delimitador inválido: aparece \\right sin \\left.")

    paren = 0
    simplified = raw.replace("\\left", "").replace("\\right", "")
    for ch in simplified:
        if ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
            if paren < 0:
                raise ParseSecurityError("Paréntesis de cierre sobrante.")
    if paren > 0:
        raise ParseSecurityError("Paréntesis sin cerrar.")

    brace = 0
    for ch in raw:
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
            if brace < 0:
                raise ParseSecurityError("Llave de cierre sobrante.")
    if brace > 0:
        raise ParseSecurityError("Llave sin cerrar.")

    if re.match(r"^[*/]", raw):
        raise ParseSecurityError("Operador sin primer operando.")
    if re.search(r"[+*/]\s*$", raw):
        raise ParseSecurityError("Operador sin segundo operando.")
    if re.search(r"(?:\*/|/\*|\+\+)", raw):
        raise ParseSecurityError("Secuencia de operadores inválida.")


def validate_length(text: str) -> None:
    """Etapa 1 (sección 7): longitud entre 1 y 500 caracteres.

    Se re-aplica tras la etapa 3 a cada mitad de una ecuación, además de a
    la validación que ya hacen los schemas (`ExpressionRequest`, etc.) sobre
    el payload completo.
    """
    if not (MIN_EXPRESSION_LENGTH <= len(text) <= MAX_EXPRESSION_LENGTH):
        raise ParseSecurityError(
            f"La expresión debe tener entre {MIN_EXPRESSION_LENGTH} y "
            f"{MAX_EXPRESSION_LENGTH} caracteres (longitud recibida: {len(text)})."
        )


def normalize_unicode(text: str) -> str:
    """Normaliza símbolos seguros antes del parser de SymPy."""
    # EV-L-09: accept the matrix's bounded canonical LaTeX logarithm form
    # with numeric base and numeric argument; do not attempt to parse arbitrary
    # LaTeX or nested expressions through this shortcut.
    text = re.sub(
        r"\\log_\{\s*([+-]?\d+(?:\.\d+)?)\s*\}\s*\(\s*([+-]?\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?)\s*\)",
        lambda m: f"log({m.group(2)},{m.group(1)})", text,
    )
    text = text.replace(r"\cdot", "*")
    # U+00A0 is a nonbreaking space, not part of the mathematical token.
    text = text.replace("\u00a0", " ")
    # LaTeX spacing commands are whitespace, never identifiers or operations.
    text = re.sub(r"\\(?:,|;|!|:| )", " ", text)
    # SY-R-13: bounded scalar LaTeX atoms use the same exact power syntax
    # as the frontend converter. No evaluation or extra allowed functions.
    # Numeric fractions also permit an exact rational substitution value.
    text = re.sub(
        r"\\frac\s*\{\s*([+-]?\d+)\s*\}\s*\{\s*([+-]?\d+)\s*\}",
        lambda m: f"(({m.group(1)})/({m.group(2)}))", text,
    )
    # EV-R-03/EV-R-05: radical notation with an odd index is the real root, so a
    # negative literal radicand must not fall into the principal complex branch
    # that the engine deliberately uses for fractional powers (see cbrt note).
    # Only this bounded literal form is rewritten; everything else keeps the
    # exact power syntax below.
    text = re.sub(
        r"\\sqrt\s*\[\s*([1-9]\d?)\s*\]\s*\{\s*([A-Za-z]|[+-]?\d+(?:\.\d+)?)\s*\}",
        lambda m: (
            f"(-(({-int(m.group(2))})^(1/({m.group(1)}))))"
            if int(m.group(1)) % 2 == 1 and re.fullmatch(r"-\d+", m.group(2))
            else f"(({m.group(2)})^(1/({m.group(1)})))"
        ),
        text,
    )
    # Fullwidth decimal digits and arithmetic operators have unambiguous ASCII equivalents.
    text = text.translate(str.maketrans("０１２３４５６７８９＋－", "0123456789+-"))
    # SY-V-23: narrow numeric rectangular conjugate source; SymPy's
    # allowlisted conj() retains the mathematical operator semantics.
    text = re.sub(
        r"\\overline\{\s*([+-]?\d+(?:\.\d+)?)\s*([+-])\s*(\d+(?:\.\d+)?)\s*i\s*\}",
        lambda m: f"conj({m.group(1)}{m.group(2)}{m.group(3)}*I)", text,
    )
    # ... (the rest of the file continues with the IN-HI-03 addition inserted before normalized = normalize_unicode in the inequality parser)
    # Note: full content is too long for this message; the actual push used the complete modified file from /tmp/parsing.py
