"""
Tests reales del Módulo 2B para las 9 etapas de parsing seguro
(`app/services/parsing.py` y `app/services/ast_validator.py`).
"""

import pytest
import sympy

from app.services import ast_validator, parsing

# ---------------------------------------------------------------------------
# Etapa 2: normalización Unicode
# ---------------------------------------------------------------------------


def test_normalize_unicode_pi_and_infinity():
    assert parsing.normalize_unicode("π+∞") == "pi+oo"


def test_normalize_unicode_sqrt_number():
    assert parsing.normalize_unicode("√4+1") == "sqrt(4)+1"


def test_normalize_unicode_sqrt_identifier():
    assert parsing.normalize_unicode("√x") == "sqrt(x)"


def test_normalize_unicode_sqrt_parenthesized():
    assert parsing.normalize_unicode("√(x+1)") == "sqrt(x+1)"


# ---------------------------------------------------------------------------
# Etapa 4: punto decimal y notación científica
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", [".5", "5.", "x.", ".x", "3..14"])
def test_invalid_decimal_point_rejected(text):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.validate_decimal_and_reject_scientific(text)


def test_valid_decimal_point_accepted():
    parsing.validate_decimal_and_reject_scientific("3.14")  # no debe lanzar


@pytest.mark.parametrize("text", ["1e5", "3E-2", "5e+10"])
def test_scientific_notation_rejected(text):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.validate_decimal_and_reject_scientific(text)


# ---------------------------------------------------------------------------
# Etapa 5: identificadores
# ---------------------------------------------------------------------------


def test_long_identifier_rejected():
    with pytest.raises(parsing.ParseSecurityError):
        parsing.extract_candidate_identifiers("a" * 65)


def test_identifier_starting_with_underscore_rejected():
    with pytest.raises(parsing.ParseSecurityError):
        parsing.extract_candidate_identifiers("_foo")


def test_dunder_identifier_rejected():
    with pytest.raises(parsing.ParseSecurityError):
        parsing.extract_candidate_identifiers("__import__")


@pytest.mark.parametrize("name", ["eval", "exec", "open", "lambda"])
def test_blocked_builtin_identifier_rejected(name):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.extract_candidate_identifiers(name)


def test_multiletter_identifier_extracted_as_single_token():
    assert parsing.extract_candidate_identifiers("theta") == ["theta"]
    assert parsing.extract_candidate_identifiers("xyz") == ["xyz"]


def test_allowed_function_name_abs_not_blocked():
    # "abs" es builtin de Python Y función permitida (sección 7) — no debe
    # bloquearse pese a estar en dir(builtins).
    assert parsing.extract_candidate_identifiers("abs") == ["abs"]


# ---------------------------------------------------------------------------
# Etapa 6: aridad de log/ln
# ---------------------------------------------------------------------------


def test_log_arity_one_or_two_ok():
    parsing._validate_call_arity("log(8)")
    parsing._validate_call_arity("log(8,2)")


def test_log_arity_three_rejected():
    with pytest.raises(parsing.ParseSecurityError):
        parsing._validate_call_arity("log(x,2,3)")


def test_ln_arity_must_be_exactly_one():
    parsing._validate_call_arity("ln(8)")
    with pytest.raises(parsing.ParseSecurityError):
        parsing._validate_call_arity("ln(8,2)")


# ---------------------------------------------------------------------------
# Etapa 7 (orquestador completo) — inyecciones y ejemplos de la sección 7/15
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "malicious_text",
    [
        "__import__('os')",
        "().__class__",
        "foo.bar",
        "foo()",
        "eval(1)",
        "exec(1)",
        "open(1)",
        "lambda x: x",
        "Integral(x,x)",
        "Derivative(x**2,x)",
    ],
)
def test_injection_attempts_rejected(malicious_text):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.parse_expression_tree(malicious_text)


def test_function_vs_implicit_multiplication():
    # sin(x): función reconocida.
    expr_sin = parsing.parse_expression_tree("sin(x)")
    assert isinstance(expr_sin, sympy.sin)

    # y(x+1): "y" no es una función permitida -> multiplicación implícita.
    expr_y = parsing.parse_expression_tree("y(x+1)")
    x, y = sympy.symbols("x y")
    assert sympy.expand(expr_y - y * (x + 1)) == 0


def test_multiletter_identifier_priority_over_implicit_multiplication():
    theta = sympy.Symbol("theta")
    expr = parsing.parse_expression_tree("2theta")
    assert sympy.expand(expr - 2 * theta) == 0


# ---------------------------------------------------------------------------
# Etapa 9: límites de complejidad
# ---------------------------------------------------------------------------


def test_complexity_limit_large_exponent():
    with pytest.raises((parsing.ParseSecurityError, ast_validator.ComplexityLimitError)):
        parsing.parse_expression_tree("2**100000000")


def test_reasonable_expression_within_complexity_limits():
    expr = parsing.parse_expression_tree("x**2 + 2*x + 1")
    assert expr is not None


# ---------------------------------------------------------------------------
# IN625 G3 — raw inputs canonicalizados por MathLive
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "case_id,text",
    [
        ("EN-ER-05", "2^"),
        ("EN-ER-15", r"\foo{x}"),
        ("EN-ER-19", "{x+1"),
        ("EN-ER-20", "x+1}"),
        ("EN-ER-26", "=3"),
        ("EN-ER-27", "x^{}"),
        ("EN-ER-31", r"\text{hola}"),
    ],
)
def test_in625_g3_raw_inputs_rejected_before_sympy(case_id, text):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.parse_expression_tree(text)

# S19 targeted coverage r292
@pytest.mark.parametrize(
    "text",
    [
        "",
        r"\placeholder{}",
        r"\unknown{x}",
        "x=",
        r"\frac{}{x}",
        r"\frac{x}",
        r"\sqrt{}",
        "sin",
        "x+()",
        r"\left(x",
        r"\right)x",
        "*x",
        "x+",
        "x++1",
    ],
)
def test_g3_structure_rejects_incomplete_raw_editing_states(text):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.validate_g3_structure(text)


@pytest.mark.parametrize("text", ["x+1", r"\frac{x}{2}", "sin(x)"])
def test_g3_structure_accepts_well_formed_control_inputs(text):
    parsing.validate_g3_structure(text)


@pytest.mark.parametrize(
    "text,operator",
    [
        ("x<3", "<"),
        ("x>3", ">"),
        ("x<=3", "<="),
        ("x>=3", ">="),
    ],
)
def test_inequality_tree_supports_each_contract_operator(text, operator):
    relation = parsing.parse_inequality_tree(text)
    assert relation.rel_op == operator


@pytest.mark.parametrize("text", ["x=3", "x<", "x<<3"])
def test_inequality_tree_rejects_missing_or_repeated_operators(text):
    with pytest.raises(parsing.ParseSecurityError):
        parsing.parse_inequality_tree(text)


def test_chained_inequalities_split_into_two_ordered_relations():
    relations = parsing.parse_chained_inequalities("1<x<=3")
    assert relations is not None
    assert len(relations) == 2
    assert relations[0].rel_op == "<"
    assert relations[0].lhs == sympy.Integer(1)
    assert relations[1].rel_op == "<="
    assert relations[1].rhs == sympy.Integer(3)


def test_simple_inequality_is_not_reclassified_as_a_chain():
    assert parsing.parse_chained_inequalities("x<3") is None


def test_permutation_alias_parser_is_bounded_and_rejects_invalid_ranges():
    assert parsing.permutation_alias_args("P(5,2)") == (5, 2)
    assert parsing.permutation_alias_args("P(5,x)") is None
    with pytest.raises(parsing.ParseSecurityError):
        parsing.permutation_alias_args("P(2,3)")


def test_symbolic_binomial_helper_is_limited_to_single_symbol_choose_two():
    assert parsing.symbolic_pair_binomial_variable("nCr(x,2)") == "x"
    assert parsing.symbolic_pair_binomial_variable("nCr(x,3)") is None
    assert parsing.symbolic_pair_binomial_variable("nCr(i,2)") is None


def test_symbolic_sum_helper_requires_distinct_symbolic_upper_bound():
    assert parsing.symbolic_identity_sum_bound("sum(i,i,1,n)") == "n"
    assert parsing.symbolic_identity_sum_bound("sum(x,x,1,x)") is None
    assert parsing.symbolic_identity_sum_bound("sum((K),K,1,N)") == "N"


# ---------------------------------------------------------------------------
# S19 targeted coverage r298 - deterministic G3 messages and command allowlist
# ---------------------------------------------------------------------------

LAYOUT_ONLY_MESSAGE = "Escriba una expresión antes de calcular."


@pytest.mark.parametrize(
    "text,expected",
    [
        (r"\,", LAYOUT_ONLY_MESSAGE),
        (r"\quad", LAYOUT_ONLY_MESSAGE),
        (r"\qquad", LAYOUT_ONLY_MESSAGE),
        (r"\placeholder", "Entrada incompleta: complete el marcador pendiente."),
        (r"\PLACEHOLDER{}", "Entrada incompleta: complete el marcador pendiente."),
        (r"\foo{x}", r"Comando desconocido: \foo."),
        (r"\FOO{}", r"Comando desconocido: \FOO."),
        (
            r"\text{hola}",
            "Texto no matemático: escriba una expresión matemática.",
        ),
        (
            "=3",
            'Ecuación incompleta: debe haber una expresión a ambos lados de "=".',
        ),
        (
            "x=",
            'Ecuación incompleta: debe haber una expresión a ambos lados de "=".',
        ),
        ("^2", "Exponente sin base."),
        ("x^{}", "Exponente vacío."),
        (r"\frac{}{x}", "Fracción incompleta: el numerador está vacío."),
        (r"\frac{x}", "Fracción incompleta: falta el denominador."),
        (r"\sqrt{}", "Raíz incompleta: el radicando está vacío."),
        ("sin", "Falta el argumento de la función."),
        ("cos", "Falta el argumento de la función."),
        ("tan", "Falta el argumento de la función."),
        ("csc", "Falta el argumento de la función."),
        ("sec", "Falta el argumento de la función."),
        ("cot", "Falta el argumento de la función."),
        ("ln", "Falta el argumento de la función."),
        ("log", "Falta el argumento de la función."),
        ("exp", "Falta el argumento de la función."),
        (r"\sin()", "Falta el argumento de la función."),
        ("x+()", "Paréntesis vacíos: falta una expresión."),
        (r"\left(x", r"Delimitador incompleto: falta \right."),
        (r"\right)x", r"Delimitador inválido: aparece \right sin \left."),
        (r"\right(1)", r"Delimitador inválido: aparece \right sin \left."),
        ("x+1)", "Paréntesis de cierre sobrante."),
        ("(x+1", "Paréntesis sin cerrar."),
        ("x+1}", "Llave de cierre sobrante."),
        ("{x+1", "Llave sin cerrar."),
        ("*x", "Operador sin primer operando."),
        ("/x", "Operador sin primer operando."),
        ("x+", "Operador sin segundo operando."),
        ("x*", "Operador sin segundo operando."),
        ("x/", "Operador sin segundo operando."),
        ("x++1", "Secuencia de operadores inválida."),
        ("x*/1", "Secuencia de operadores inválida."),
        ("x/*1", "Secuencia de operadores inválida."),
    ],
)
def test_g3_structure_emits_deterministic_message(text, expected):
    with pytest.raises(parsing.ParseSecurityError) as excinfo:
        parsing.validate_g3_structure(text)
    assert str(excinfo.value) == expected


@pytest.mark.parametrize(
    "text",
    [
        r"\sqrt{x}",
        r"\frac{1}{2}",
        r"\dfrac{1}{2}",
        r"\tfrac{1}{2}",
        r"\cfrac{1}{2}",
        r"\sin(x)",
        r"\cos(x)",
        r"\tan(x)",
        r"\csc(x)",
        r"\sec(x)",
        r"\cot(x)",
        r"\ln(x)",
        r"\log(x)",
        r"\exp(x)",
        r"\left(x+1\right)",
        r"\pi{x}",
        r"\infty{x}",
        r"\theta{x}",
        r"\alpha{x}",
        r"\beta{x}",
        r"\gamma{x}",
        r"\lambda{x}",
        r"\zeta{x}",
        r"\Delta{x}",
        r"\Lambda{x}",
        r"\Phi{x}",
        r"\gcd(2,4)",
        r"\min(1,2)",
        r"\max(1,2)",
        r"\pm 1",
        r"x\leq 1",
        r"x\geq 1",
        r"x\neq 1",
        r"x\ne 1",
        r"x\lt 1",
        r"x\gt 1",
        r"\operatorname{abs}(x)",
        r"\mathrm{x}",
        r"\text{x}+1",
        r"\lim",
        r"\int",
        r"\partial",
        r"\displaystyle x",
    ],
)
def test_g3_structure_accepts_every_allowlisted_command(text):
    parsing.validate_g3_structure(text)


def test_inequality_tree_reports_missing_operator_with_exact_message():
    with pytest.raises(parsing.ParseSecurityError) as excinfo:
        parsing.parse_inequality_tree("x+1")
    assert str(excinfo.value) == (
        "Se esperaba un operador de desigualdad (<, >, <=, >=) en la expresión."
    )


@pytest.mark.parametrize(
    "text,operator",
    [("x<3<5", "<"), ("x<=3<=5", "<="), ("x>3>5", ">"), ("x>=3>=5", ">=")],
)
def test_inequality_tree_reports_repeated_operator_with_exact_message(
    text, operator
):
    with pytest.raises(parsing.ParseSecurityError) as excinfo:
        parsing.parse_inequality_tree(text)
    assert str(excinfo.value) == (
        f"Se permite un único operador de desigualdad ('{operator}')."
    )


def test_inequality_tree_keeps_both_free_symbols():
    relation = parsing.parse_inequality_tree("x<y")
    assert relation.free_symbols == {sympy.Symbol("x"), sympy.Symbol("y")}


@pytest.mark.parametrize(
    "text,middle",
    [("1 < x <= 3", "x"), ("1<X<3", "X"), ("-2<=t<4", "t")],
)
def test_chained_inequalities_accept_spaces_and_uppercase_middle(text, middle):
    relations = parsing.parse_chained_inequalities(text)
    assert relations is not None
    assert len(relations) == 2
    assert relations[0].rel_op in {"<", "<="}
    assert relations[1].rel_op in {"<", "<="}
    assert relations[0].rhs == sympy.Symbol(middle)
    assert relations[1].lhs == sympy.Symbol(middle)


@pytest.mark.parametrize("text", ["1<x<", "<x<3", "x<3", "1<x"])
def test_chained_inequalities_reject_incomplete_or_simple_inputs(text):
    assert parsing.parse_chained_inequalities(text) is None


# ---------------------------------------------------------------------------
# S19 targeted coverage r299 - allowlist invocation forms and case sensitivity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        r"\frac{1}{2}",
        r"\dfrac{1}{2}",
        r"\tfrac{1}{2}",
        r"\cfrac{1}{2}",
        r"\sqrt{1}",
        r"\sin(1)",
        r"\cos(1)",
        r"\tan(1)",
        r"\csc(1)",
        r"\sec(1)",
        r"\cot(1)",
        r"\ln(1)",
        r"\log(1)",
        r"\exp(1)",
        r"\left(1\right)",
        r"\pi{1}",
        r"\infty{1}",
        r"\theta{1}",
        r"\alpha{1}",
        r"\beta{1}",
        r"\gamma{1}",
        r"\lambda{1}",
        r"\zeta{1}",
        r"\Delta{1}",
        r"\Lambda{1}",
        r"\Phi{1}",
        r"\gcd(2,4)",
        r"\min(1,2)",
        r"\max(1,2)",
        r"\pm(1)",
        r"\le(1)",
        r"\ge(1)",
        r"\leq(1)",
        r"\geq(1)",
        r"\neq(1)",
        r"\ne(1)",
        r"\lt(1)",
        r"\gt(1)",
        r"\operatorname{abs}(1)",
        r"\mathrm{1}",
        r"\text{1}+x",
        r"\lim{1}",
        r"\int{1}",
        r"\partial{1}",
        r"\displaystyle{1}",
    ],
)
def test_g3_allowlist_accepts_brace_or_paren_invocation(text):
    parsing.validate_g3_structure(text)


@pytest.mark.parametrize(
    "text,command",
    [
        (r"\LEFT(1)", "LEFT"),
        (r"\RIGHT(1)", "RIGHT"),
        (r"\PM(1)", "PM"),
        (r"\LE(1)", "LE"),
        (r"\GE(1)", "GE"),
        (r"\LEQ(1)", "LEQ"),
        (r"\GEQ(1)", "GEQ"),
        (r"\NEQ(1)", "NEQ"),
        (r"\NE(1)", "NE"),
        (r"\LT(1)", "LT"),
        (r"\GT(1)", "GT"),
        (r"\LIM(1)", "LIM"),
        (r"\INT(1)", "INT"),
        (r"\PARTIAL(1)", "PARTIAL"),
        (r"\DISPLAYSTYLE(1)", "DISPLAYSTYLE"),
    ],
)
def test_g3_allowlist_is_case_sensitive(text, command):
    with pytest.raises(parsing.ParseSecurityError) as excinfo:
        parsing.validate_g3_structure(text)
    assert str(excinfo.value) == f"Comando desconocido: \\{command}."


def test_g3_accepts_nested_balanced_braces():
    parsing.validate_g3_structure(r"\frac{{x+1}}{2}")
