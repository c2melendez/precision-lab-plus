"""SY-P structural interpretation witnesses via Plus evaluate HTTP.

Numeric substitution witnesses only; no frontend MathLive or echo certification.
"""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_sy_p_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(s) for s in DATA.read_text(encoding="utf-8").splitlines() if s.strip())}

# Original LaTeX translated explicitly to the Plus backend expression language.
CASES = {
    "SY-P-04": ("2*x^2", {"x": "3"}, 18.0),
    "SY-P-05": ("-x^2", {"x": "3"}, -9.0),
    "SY-P-20": ("(1/2)*x", {"x": "6"}, 3.0),
    "SY-P-22": ("1/(2*x)", {"x": "2"}, 0.25),
    "SY-P-26": ("x^2*y", {"x": "3", "y": "2"}, 18.0),
}


def test_syp_interpretation_source_ids():
    assert all(ROWS[id]["operacion"] == "interpretacion" for id in CASES)


@pytest.mark.parametrize("case_id", list(CASES))
def test_syp_interpretation_numeric_witness_via_http(case_id):
    expression, substitutions, expected = CASES[case_id]
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/evaluate",
            json={"expression": expression, "substitutions": substitutions},
        )
    assert response.status_code == 200, (case_id, response.text)
    body = response.json()
    assert body["success"] is True, (case_id, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


# These tests intentionally send concatenated variables to the real parser.
# Rewriting xy as x*y in the fixture would bypass the behavior under audit.
@pytest.mark.parametrize(
    "case_id,expression,substitutions,expected",
    [
        ("SY-P-24", "xy", {"x": "2", "y": "3"}, 6.0),
        ("SY-P-25", "xyz", {"x": "2", "y": "3", "z": "5"}, 30.0),
    ],
)
def test_syp_concatenated_variables_via_http(case_id, expression, substitutions, expected):
    assert ROWS[case_id]["operacion"] == "interpretacion"
    assert ROWS[case_id]["entrada"] == expression
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/evaluate",
            json={"expression": expression, "substitutions": substitutions},
        )
    assert response.status_code == 200, (case_id, response.text)
    body = response.json()
    assert body["success"] is True, (case_id, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "case_id,expression,substitutions,expected",
    [
        ("SY-P-18", "8/2(2+2)", None, 16.0),
        ("SY-P-19", "6/2(1+2)", None, 9.0),
        ("SY-P-21", "1/2x", {"x": "6"}, 3.0),
    ],
)
def test_syp_ambiguous_implicit_precedence_current_convention(case_id, expression, substitutions, expected):
    """Characterize the current convention; a PASS does not certify a UI warning."""
    assert ROWS[case_id]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression, **({"substitutions": substitutions} if substitutions else {})})
    assert response.status_code == 200, (case_id, response.text)
    body = response.json()
    assert body["success"] is True, (case_id, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.xfail(strict=True, reason="SY-P-23: bc currently parsed as a named symbol; no declared splitting convention")
def test_syp_23_separate_b_c_substitutions_pending():
    """Known product/convention gap: do not certify as PASS."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "a/bc",
            "substitutions": {"a": "12", "b": "3", "c": "2"},
        })
    assert response.status_code == 200
    assert response.json()["result_approx"] == pytest.approx(8.0)


def test_syp_23_existing_named_bc_identifier_convention():
    """Current behavior: bc denotes a single symbol, so a/bc can be numeric."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "a/bc",
            "substitutions": {"a": "12", "bc": "6"},
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(2.0)



def test_syp_32_undefined_single_letter_function_is_not_invented():
    """SY-P-32: f(x+1) is a product under the permitted single-letter convention."""
    assert ROWS["SY-P-32"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "f(x+1)",
            "substitutions": {"f": "2", "x": "3"},
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(8.0)


@pytest.mark.parametrize(
    "expression,expected",
    [("(a/b)*c", 8.0), ("a/(b*c)", 2.0)],
)
def test_syp_23_explicit_grouping_distinguishes_two_readings(expression, expected):
    """Explicit parenthesization is unambiguous; bare a/bc remains unsettled."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression,substitutions,expected",
    [
        # When both spellings exist, bare bc must retain its own binding.
        ("a/bc", {"a": "12", "bc": "6", "b": "3", "c": "2"}, 2.0),
        # An explicitly written product must not consume the named bc binding.
        ("a/(b*c)", {"a": "12", "bc": "99", "b": "3", "c": "2"}, 2.0),
        ("(a/b)*c", {"a": "12", "bc": "99", "b": "3", "c": "2"}, 8.0),
    ],
)
def test_syp_23_named_bc_does_not_shadow_explicit_b_times_c(expression, substitutions, expected):
    """Protect named-identifier semantics while keeping the alternative raw reading XFAIL."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": substitutions,
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize("expression", ["a/(b*c)", "((a)/(b*c))"])
def test_syp_23_redundant_fraction_grouping_preserves_explicit_product(expression):
    """Parenthesis differences must not change numeric meaning or consume named bc."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "99", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(2.0, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize("expression", ["(a/b)*c", "(((a)/(b)))*c"])
def test_syp_23_redundant_numerator_grouping_preserves_explicit_product(expression):
    """Parentheses around the divided numerator must not absorb c into denominator."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "99", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(8.0, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "expression,expected",
    [("(a/b)*c", 7.5), ("a/(b*c)", 1.2), ("((a)/(b*c))", 1.2)],
)
def test_syp_23_decimal_witness_with_named_bc_shadow(expression, expected):
    """Explicit multiplication must not become a named bc even with fractional inputs."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "9", "b": "3", "c": "2.5", "bc": "99"},
        })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1+(a/b)*c", 9.0),
        ("1+a/(b*c)", 3.0),
        ("2*((a/b)*c)", 16.0),
        ("2*(a/(b*c))", 4.0),
        ("(a/b)*c+3", 11.0),
        ("a/(b*c)+3", 5.0),
    ],
)
def test_syp_23_compound_context_preserves_explicit_grouping_with_bc_shadow(expression, expected):
    """Independent numeric evidence for both grouped readings even when bc exists."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "99", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, (expression, response.text)
    body = response.json()
    assert body["success"] is True, (expression, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1+a/bc", 3.0),
        ("2*(a/bc)", 4.0),
        ("a/bc+3", 5.0),
    ],
)
def test_syp_23_named_bc_in_extended_expression_with_separate_b_c_present(expression, expected):
    """A declared bc must remain a named identifier in larger arithmetic contexts."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "6", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, (expression, response.text)
    body = response.json()
    assert body["success"] is True, (expression, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("(1+a/bc)", 3.0),
        ("((2*(a/bc)))", 4.0),
        ("(a/bc+3)", 5.0),
    ],
)
def test_syp_23_named_bc_extended_expression_outer_parentheses(expression, expected):
    """Outer grouping must preserve a declared compound identifier bc."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "6", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, (expression, response.text)
    body = response.json()
    assert body["success"] is True, (expression, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1+a/bc", 4.0),
        ("2*(a/bc)", 6.0),
        ("a/bc+3", 6.0),
    ],
)
def test_syp_23_named_bc_value_is_independent_of_b_times_c(expression, expected):
    """Changing bc independently of b*c must change the value of bare a/bc."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "4", "b": "3", "c": "2"},
        })
    assert response.status_code == 200, (expression, response.text)
    body = response.json()
    assert body["success"] is True, (expression, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("a/bc", -2.0),
        ("a/(b*c)", 2.0),
        ("(a/b)*c", 8.0),
    ],
)
def test_syp_23_negative_named_identifier_preserves_explicit_multiplication(expression, expected):
    """Sign-sensitive independent witness: bc is not interchangeable with b*c."""
    assert ROWS["SY-P-23"]["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": expression,
            "substitutions": {"a": "12", "bc": "-6", "b": "-3", "c": "-2"},
        })
    assert response.status_code == 200, (expression, response.text)
    body = response.json()
    assert body["success"] is True, (expression, body)
    assert body["result_approx"] == pytest.approx(expected, rel=1e-9, abs=1e-12)
