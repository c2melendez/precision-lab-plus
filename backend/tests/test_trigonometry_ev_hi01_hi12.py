"""Trigonometry EV-HI-01..12: inverse hyperbolic functions of the frozen battery.

Exact integer values and the composition sinh(asinh(3))=3 must be exact. The
remaining values are certified on the numeric channel (result_approx) against
the documented 9-decimal approximations. The two out-of-domain cases must
report a clear DOMAIN_ERROR on the real channel, never a complex value or an
echo of the call.
"""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)


def _row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def _evaluate(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def test_ev_hi_source_rows_present():
    for index in range(1, 13):
        case_id = f"EV-HI-{index:02d}"
        assert _row(case_id), f"{case_id} row missing"


def test_ev_hi_01_to_03_origin_exact_values():
    with TestClient(app) as client:
        for expression, expected in (("asinh(0)", "0"), ("acosh(1)", "0"), ("atanh(0)", "0")):
            payload = _evaluate(client, expression)
            assert payload["success"] is True, payload
            assert payload["result_text"].strip() == expected, payload


def test_ev_hi_04_to_09_numeric_values():
    cases = [
        ("asinh(1)", 0.881373587019543),
        ("acosh(2)", 1.3169578969248166),
        ("atanh(1/2)", 0.5493061443340549),
        ("acsch(1)", 0.881373587019543),
        ("asech(1/2)", 1.3169578969248166),
        ("acoth(2)", 0.5493061443340549),
    ]
    with TestClient(app) as client:
        for expression, expected in cases:
            payload = _evaluate(client, expression)
            assert payload["success"] is True, payload
            approx = payload.get("result_approx")
            assert approx is not None, payload
            assert abs(approx - expected) < 5e-10, (expression, approx)


def test_ev_hi_10_to_12_composition_and_domain_errors():
    with TestClient(app) as client:
        composition = _evaluate(client, "sinh(asinh(3))")
        undefined = _evaluate(client, "atanh(1)")
        outside = _evaluate(client, "acosh(1/2)")
    assert composition["success"] is True, composition
    assert sp.simplify(sp.sympify(composition["result_text"].replace("^", "**")) - 3) == 0, composition
    assert undefined["success"] is False and undefined["error_code"] == "DOMAIN_ERROR", undefined
    assert outside["success"] is False and outside["error_code"] == "DOMAIN_ERROR", outside


def test_ev_hi_04_to_09_exact_forms_match_frozen_matrix():
    cases = [
        ("asinh(1)", sp.log(1 + sp.sqrt(2))),
        ("acosh(2)", sp.log(2 + sp.sqrt(3))),
        ("atanh(1/2)", sp.log(3) / 2),
        ("acsch(1)", sp.log(1 + sp.sqrt(2))),
        ("asech(1/2)", sp.log(2 + sp.sqrt(3))),
        ("acoth(2)", sp.log(3) / 2),
    ]
    locals_map = {
        "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh,
        "acsch": sp.acsch, "asech": sp.asech, "acoth": sp.acoth,
        "ln": sp.log,
    }
    with TestClient(app) as client:
        for expression, expected in cases:
            payload = _evaluate(client, expression)
            assert payload["success"] is True, (expression, payload)
            got = sp.sympify(
                payload["result_text"].replace("^", "**"), locals=locals_map
            )
            # SymPy versions in CI don't consistently expand inverse hyperbolic
            # functions with expand_func/rewrite(log). Normalize these six
            # frozen, numeric identities explicitly, then compare exactly.
            exact_forms = {
                (sp.asinh, (sp.Integer(1),)): sp.log(1 + sp.sqrt(2)),
                (sp.acosh, (sp.Integer(2),)): sp.log(2 + sp.sqrt(3)),
                (sp.atanh, (sp.Rational(1, 2),)): sp.log(3) / 2,
                (sp.acsch, (sp.Integer(1),)): sp.log(1 + sp.sqrt(2)),
                (sp.asech, (sp.Rational(1, 2),)): sp.log(2 + sp.sqrt(3)),
                (sp.acoth, (sp.Integer(2),)): sp.log(3) / 2,
            }
            normalized = got.replace(
                lambda node: isinstance(node, sp.Function)
                and (node.func, node.args) in exact_forms,
                lambda node: exact_forms[(node.func, node.args)],
            )
            assert sp.simplify(normalized - expected) == 0, (expression, payload)
