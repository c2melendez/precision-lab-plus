#!/usr/bin/env python3
"""S18 — differential/property gate: Plus ↔ Lite ↔ SymPy.

Seed fija, profundidad acotada y contraejemplos persistentes. El gate usa
los motores reales: API/TestClient de Plus y código TypeScript real de Lite
(checkout separado, pinneado por SHA en el workflow).
"""

from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SEED = 180018
LITE_SHA = "6cbec7645b73ad18875d4472182c704eb35228b0"
ABS_TOL = 1e-8
REL_TOL = 1e-8

client = TestClient(app, raise_server_exceptions=False)
rng = random.Random(SEED)


class S18Failure(AssertionError):
    pass


def fail(kind: str, payload: dict, detail: str) -> None:
    counterexample = {
        "module": "S18",
        "seed": SEED,
        "lite_sha": LITE_SHA,
        "kind": kind,
        "payload": payload,
        "detail": detail,
    }
    print("S18_COUNTEREXAMPLE=" + json.dumps(counterexample, ensure_ascii=False, sort_keys=True))
    raise S18Failure(detail)


def close(a: float, b: float, tol: float = ABS_TOL) -> bool:
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=tol)


def sympify_user(expr: str) -> sp.Expr:
    return sp.sympify(expr.replace("^", "**"), locals={"ln": sp.log})


def plus_eval(expr: str) -> float:
    response = client.post("/api/v1/evaluate", json={"expression": expr, "angle_unit": "rad"})
    if response.status_code != 200:
        fail("plus-evaluate-http", {"expression": expr}, f"status={response.status_code}: {response.text}")
    body = response.json()
    if not body.get("success"):
        fail("plus-evaluate-error", {"expression": expr}, json.dumps(body, ensure_ascii=False))
    value = body.get("result_approx")
    if value is None:
        try:
            value = float(sp.N(sympify_user(body["result_text"])))
        except Exception as exc:
            fail("plus-evaluate-nonnumeric", {"expression": expr}, f"{body!r}; {exc}")
    value = float(value)
    if not math.isfinite(value):
        fail("plus-evaluate-nonfinite", {"expression": expr}, repr(body))
    return value


def lite_batch(requests: list[dict]) -> list[dict]:
    command = ["npx", "-y", "tsx@4.20.6", str(ROOT / "qa/s18/lite_oracle.ts")]
    proc = subprocess.run(
        command,
        cwd=ROOT,
        input=json.dumps(requests),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
    )
    if proc.returncode != 0:
        fail("lite-oracle-crash", {"requests": requests[:3]}, proc.stderr[-4000:])
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        fail("lite-oracle-json", {"requests": requests[:3]}, f"{exc}: {proc.stdout[-2000:]}")
    raise AssertionError("unreachable")


def check_persisted_counterexamples() -> int:
    path = ROOT / "qa/s18/counterexamples.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if not cases:
        return 0
    lite_requests = [{"op": "eval", "expr": case["lite"]} for case in cases]
    lite_results = lite_batch(lite_requests)
    for case, lite in zip(cases, lite_results):
        plus_value = plus_eval(case["plus"])
        sym_value = float(sp.N(sympify_user(case["sympy"])))
        lite_value = float(lite["value"])
        if not (close(plus_value, sym_value) and close(lite_value, sym_value)):
            fail("persisted-counterexample", case, f"plus={plus_value}, lite={lite_value}, sympy={sym_value}")
    return len(cases)


def generated_numeric_cases(count: int = 60) -> list[dict]:
    cases: list[dict] = []
    for _ in range(count):
        family = rng.randrange(4)
        if family == 0:
            a, b, c = (rng.randint(-6, 6) for _ in range(3))
            x = rng.randint(-5, 5)
            plus = f"({a})*({x})**2+({b})*({x})+({c})"
            lite = f"({a})*({x})^2+({b})*({x})+({c})"
            sym = plus
        elif family == 1:
            x = rng.uniform(-3.0, 3.0)
            plus = f"sin({x})**2+cos({x})**2"
            lite = f"sin({x})^2+cos({x})^2"
            sym = plus
        elif family == 2:
            x = rng.uniform(-2.0, 2.0)
            a = rng.randint(-3, 3)
            plus = f"exp({x})+({a})*sin({x})"
            lite = plus
            sym = plus
        else:
            n = rng.randint(1, 12)
            plus = f"sqrt(({n})**2)+1/({n}+1)"
            lite = f"sqrt(({n})^2)+1/({n}+1)"
            sym = plus
        cases.append({"plus": plus, "lite": lite, "sympy": sym})
    return cases


def property_numeric_differential() -> int:
    cases = generated_numeric_cases()
    lite_results = lite_batch([{"op": "eval", "expr": c["lite"]} for c in cases])
    for case, lite in zip(cases, lite_results):
        plus_value = plus_eval(case["plus"])
        lite_value = float(lite["value"])
        sym_value = float(sp.N(sympify_user(case["sympy"])))
        if not close(plus_value, sym_value):
            fail("plus-vs-sympy", case, f"plus={plus_value}, sympy={sym_value}")
        if not close(lite_value, sym_value):
            fail("lite-vs-sympy", case, f"lite={lite_value}, sympy={sym_value}")
        if not close(plus_value, lite_value):
            fail("plus-vs-lite", case, f"plus={plus_value}, lite={lite_value}")
    return len(cases)


def property_derivative_of_integral() -> int:
    families = [
        ("x", "x"),
        ("x**2", "x^2"),
        ("x**3+2*x", "x^3+2*x"),
        ("sin(x)", "sin(x)"),
        ("cos(x)", "cos(x)"),
        ("exp(x)", "exp(x)"),
        ("2*x**2+3*x+1", "2*x^2+3*x+1"),
    ]
    lite_results = lite_batch(
        [{"op": "derivativeOfIntegral", "expr": lite, "variable": "x"} for _, lite in families]
    )
    x = sp.Symbol("x")
    for (plus_expr, lite_expr), lite in zip(families, lite_results):
        integral = client.post(
            "/api/v1/integral", json={"expression": plus_expr, "variable": "x"}
        ).json()
        if not integral.get("success"):
            fail("plus-integral", {"expression": plus_expr}, repr(integral))
        anti = integral["result_text"].removesuffix(" + C")
        derivative = client.post(
            "/api/v1/derivative",
            json={"expression": anti, "variable": "x", "order": 1},
        ).json()
        if not derivative.get("success"):
            fail("plus-derivative-after-integral", {"expression": plus_expr, "anti": anti}, repr(derivative))

        target = sympify_user(plus_expr)
        plus_diff = sp.simplify(sympify_user(derivative["result_text"]) - target)
        lite_diff = sp.simplify(sympify_user(lite["expression"]) - target)
        if plus_diff != 0:
            fail("d-integral-plus", {"expression": plus_expr, "anti": anti}, f"difference={plus_diff}")
        if lite_diff != 0:
            fail("d-integral-lite", {"expression": lite_expr}, f"lite={lite['expression']}; difference={lite_diff}")
    return len(families)


def property_solution_substitution() -> int:
    equations: list[dict] = []
    expected_sets: list[set[int]] = []
    for _ in range(12):
        r1 = rng.randint(-7, 7)
        r2 = rng.randint(-7, 7)
        while r2 == r1:
            r2 = rng.randint(-7, 7)
        plus_poly = f"(x-({r1}))*(x-({r2}))"
        lite_poly = plus_poly
        equations.append({"plus": plus_poly, "lite": lite_poly})
        expected_sets.append({r1, r2})

    lite_results = lite_batch(
        [{"op": "rootsResiduals", "expr": item["lite"], "variable": "x"} for item in equations]
    )
    x = sp.Symbol("x")
    for item, expected, lite in zip(equations, expected_sets, lite_results):
        body = client.post(
            "/api/v1/solve",
            json={"equation": item["plus"] + "=0", "variable": "x", "angle_unit": "rad"},
        ).json()
        if not body.get("success"):
            fail("plus-solve", item, repr(body))
        plus_roots = {int(sp.Integer(sp.sympify(sol["text"]))) for sol in body["result_data"]}
        if plus_roots != expected:
            fail("plus-root-set", item, f"expected={sorted(expected)}, got={sorted(plus_roots)}")

        poly = sympify_user(item["plus"])
        for root in plus_roots:
            if sp.simplify(poly.subs(x, root)) != 0:
                fail("plus-root-residual", {**item, "root": root}, "residual != 0")

        lite_roots = set()
        for entry in lite["roots"]:
            if abs(float(entry["residual"])) > ABS_TOL:
                fail("lite-root-residual", {**item, "root": entry["root"]}, f"residual={entry['residual']}")
            lite_roots.add(int(round(float(sp.N(sympify_user(entry["root"]))))))
        if lite_roots != expected:
            fail("lite-root-set", item, f"expected={sorted(expected)}, got={sorted(lite_roots)}")
    return len(equations)


def property_trig_identity() -> int:
    cases = []
    for _ in range(20):
        x = rng.uniform(-8.0, 8.0)
        cases.append(
            {
                "plus": f"sin({x})**2+cos({x})**2",
                "lite": f"sin({x})^2+cos({x})^2",
                "sympy": f"sin({x})**2+cos({x})**2",
            }
        )
    lite_results = lite_batch([{"op": "eval", "expr": c["lite"]} for c in cases])
    for case, lite in zip(cases, lite_results):
        plus_value = plus_eval(case["plus"])
        lite_value = float(lite["value"])
        if not close(plus_value, 1.0, 1e-7):
            fail("trig-identity-plus", case, f"value={plus_value}")
        if not close(lite_value, 1.0, 1e-6):
            fail("trig-identity-lite", case, f"value={lite_value}")
    return len(cases)


def property_log_inverse() -> int:
    cases = []
    for _ in range(20):
        base = rng.choice([2, 3, 4, 5, 7, 10])
        exponent = rng.randint(-4, 5)
        plus = f"log(({base})**({exponent}),{base})"
        lite = f"log(({base})^({exponent}),{base})"
        cases.append({"plus": plus, "lite": lite, "sympy": plus, "expected": exponent})
    lite_results = lite_batch([{"op": "eval", "expr": c["lite"]} for c in cases])
    for case, lite in zip(cases, lite_results):
        plus_value = plus_eval(case["plus"])
        lite_value = float(lite["value"])
        expected = float(case["expected"])
        if not close(plus_value, expected, 1e-7):
            fail("log-inverse-plus", case, f"value={plus_value}")
        if not close(lite_value, expected, 1e-6):
            fail("log-inverse-lite", case, f"value={lite_value}")
    return len(cases)


def property_parser_serializer_roundtrip() -> int:
    expressions = [
        "2x+3",
        "(x+1)(x-1)",
        "sin(x)^2+cos(x)^2",
        "log(8,2)+x",
        "sqrt(x^2+1)",
        "3x^2-2x+5",
    ]
    samples = [-2, -0.5, 0, 1.25, 3]
    results = lite_batch(
        [{"op": "roundtrip", "expr": expr, "variable": "x", "samples": samples} for expr in expressions]
    )
    for expr, result in zip(expressions, results):
        for value in result["values"]:
            if not close(float(value["before"]), float(value["after"]), 1e-6):
                fail(
                    "lite-parser-serializer-roundtrip",
                    {"expression": expr, "latex": result["latex"], "x": value["x"]},
                    f"before={value['before']}, after={value['after']}",
                )
    return len(expressions) * len(samples)


def main() -> int:
    totals = {
        "persisted_counterexamples": check_persisted_counterexamples(),
        "numeric_differential": property_numeric_differential(),
        "derivative_of_integral": property_derivative_of_integral(),
        "solution_substitution": property_solution_substitution(),
        "trig_identity": property_trig_identity(),
        "log_inverse": property_log_inverse(),
        "parser_serializer_roundtrip_samples": property_parser_serializer_roundtrip(),
    }
    print(
        json.dumps(
            {
                "module": "S18",
                "status": "PASS",
                "seed": SEED,
                "lite_sha": LITE_SHA,
                "plus_sha": os.getenv("GITHUB_SHA", "local"),
                "totals": totals,
                "total_assertion_cases": sum(totals.values()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
