"""Syntax309 SY-E first exponent witness: backend route only."""
import json
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}

def test_sye01_braced_two_digit_exponent_explicit_backend():
    """2^10=1024 at backend; original LaTeX 2^{10} is not tested at UI."""
    row = ROWS["SY-E-01"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "2^{10}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2^10"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1024, abs=1e-9)


def test_sye02_ascii_two_digit_exponent_backend_http():
    """SY-E-02 original ASCII 2^10 must be 1024, not 2^1 * 0."""
    row = ROWS["SY-E-02"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "2^10"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(1024, abs=1e-9)


def test_sye03_power_with_explicit_substitution_http():
    """SY-E-03: translated power and substitution; natural-language LaTeX annotation not tested in UI."""
    row = ROWS["SY-E-03"]
    assert row["operacion"] == "valor"
    assert "x^{12}" in row["entrada"] and "x=2" in row["entrada"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={
            "expression": "x^12", "substitutions": {"x": "2"}
        })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(4096, abs=1e-9)


def test_sye04_negative_exponent_http():
    """SY-E-04 explicit backend power only, not source LaTeX UI."""
    row = ROWS["SY-E-04"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "10^{-3}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "10^(-3)"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == pytest.approx(0.001, abs=1e-12)


def test_sye05_nested_powers_explicit_backend_http():
    """SY-E-05: explicit backend grouping; source MathLive LaTeX UI not covered."""
    row = ROWS["SY-E-05"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "2^{2^{2}}"
    assert row["esperado"] == "16"
    # The unequal-exponent control exposes wrong left-associative grouping.
    with TestClient(app) as client:
        for expression, expected in [("2^(2^2)", 16), ("2^(3^2)", 512), ("(2^3)^2", 64)]:
            response = client.post("/api/v1/evaluate", json={"expression": expression})
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["success"] is True, data
            assert data["result_approx"] == expected, (expression, data)


@pytest.mark.parametrize("x, expected", [
    ("0", 0), ("1/16", 0.25), ("1/4", 0.5), ("1", 1),
    ("4", 2), ("9", 3), ("16", 4), ("100", 10),
])
def test_sye06_fractional_power_real_domain_http(x, expected):
    """Explicit backend witnesses on x>=0; no source UI or complex-branch claim."""
    row = ROWS["SY-E-06"]
    assert row["operacion"] == "equivalente"
    assert row["entrada"] == r"x^{\frac{1}{2}}"
    assert row["esperado"] == r"\sqrt{x}"
    with TestClient(app) as client:
        for expression in ("x^(1/2)", "sqrt(x)"):
            response = client.post("/api/v1/evaluate", json={
                "expression": expression, "substitutions": {"x": x},
            })
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["success"] is True, data
            assert data["result_approx"] == pytest.approx(expected, rel=1e-12, abs=1e-12), (expression, x, data)


@pytest.mark.parametrize("x, expected", [
    ("0", 0), ("1/16", 0.25), ("1/4", 0.5), ("1", 1),
    ("4", 2), ("9", 3), ("16", 4), ("100", 10),
])
def test_sye07_decimal_power_real_domain_http(x, expected):
    """Explicit backend x^0.5 witnesses; source UI and complex branches remain open."""
    row = ROWS["SY-E-07"]
    assert row["operacion"] == "equivalente"
    assert row["entrada"] == "x^{0.5}"
    assert row["esperado"] == r"\sqrt{x}"
    with TestClient(app) as client:
        for expression in ("x^0.5", "sqrt(x)"):
            response = client.post("/api/v1/evaluate", json={
                "expression": expression, "substitutions": {"x": x},
            })
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["success"] is True, data
            assert data["result_approx"] == pytest.approx(expected, rel=1e-12, abs=1e-12), (expression, x, data)

# Explicit translations are traceable to the official source fixture.
# Independent anchors avoid using this backend to generate its own oracle.
REAL_INTEGER_POWER_CASES = {
    "SY-E-08": [
        "x^{-1}",
        "\\frac{1}{x}",
        [
            "x^(-1)",
            "1/x"
        ],
        [
            [
                -4,
                -0.25
            ],
            [
                -1,
                -1
            ],
            [
                -0.25,
                -4
            ],
            [
                0.25,
                4
            ],
            [
                1,
                1
            ],
            [
                4,
                0.25
            ]
        ]
    ],
    "SY-E-09": [
        "\\left(x^{2}\\right)^{3}",
        "x^{6}",
        [
            "(x^2)^3",
            "x^6"
        ],
        [
            [
                -3,
                729
            ],
            [
                -2,
                64
            ],
            [
                -1,
                1
            ],
            [
                0,
                0
            ],
            [
                0.5,
                0.015625
            ],
            [
                2,
                64
            ],
            [
                3,
                729
            ]
        ]
    ],
    "SY-E-10": [
        "x^{2^{3}}",
        "x^{8}",
        [
            "x^(2^3)",
            "x^8"
        ],
        [
            [
                -3,
                6561
            ],
            [
                -2,
                256
            ],
            [
                -1,
                1
            ],
            [
                0,
                0
            ],
            [
                0.5,
                0.00390625
            ],
            [
                2,
                256
            ],
            [
                3,
                6561
            ]
        ]
    ]
}

@pytest.mark.parametrize("case_id, x, expected", [
    (case_id, x, expected)
    for case_id, (_, _, _, anchors) in REAL_INTEGER_POWER_CASES.items()
    for x, expected in anchors
])
def test_sye08_10_real_integer_power_anchors_http(case_id, x, expected):
    """Backend-only real witnesses; original MathLive/keyboard UI not covered."""
    source, equivalent, expressions, _ = REAL_INTEGER_POWER_CASES[case_id]
    row = ROWS[case_id]
    assert row["operacion"] == "equivalente"
    assert row["entrada"] == source
    assert row["esperado"] == equivalent
    if case_id == "SY-E-08":
        assert x != 0  # Excluded domain; zero-base error belongs to SY-E-20.
    with TestClient(app) as client:
        for expression in expressions:
            response = client.post("/api/v1/evaluate", json={
                "expression": expression, "substitutions": {"x": str(x)},
            })
            assert response.status_code == 200, (case_id, response.text)
            data = response.json()
            assert data["success"] is True, (case_id, x, data)
            assert data["result_approx"] == pytest.approx(expected, rel=1e-12, abs=1e-12), (case_id, expression, x, data)

# Fixed independent anchors: 8*sqrt(2), 1/sqrt(2), and -8.
DECIMAL_AND_NEGATIVE_POWER_CASES = [
    [
        "SY-E-14",
        "2^{3.5}",
        "11.31370850",
        "2^3.5",
        11.313708498984761
    ],
    [
        "SY-E-15",
        "2^{-0.5}",
        "0.7071067812",
        "2^(-0.5)",
        0.7071067811865476
    ],
    [
        "SY-E-16",
        "(-2)^{3}",
        "-8",
        "(-2)^3",
        -8
    ]
]

@pytest.mark.parametrize("case_id, source, displayed, expression, expected", DECIMAL_AND_NEGATIVE_POWER_CASES)
def test_sye14_16_decimal_and_negative_power_http(case_id, source, displayed, expression, expected):
    """Backend HTTP semantics only; original LaTeX MathLive UI remains separate."""
    row = ROWS[case_id]
    assert row["operacion"] == "valor"
    assert row["entrada"] == source
    assert row["esperado"] == displayed
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, (case_id, response.text)
        data = response.json()
        assert data["success"] is True, (case_id, data)
        assert data["result_approx"] == pytest.approx(expected, rel=1e-12, abs=1e-12), (case_id, data)
        if case_id == "SY-E-16":
            # Preserve grouped negative base versus negation of an even power.
            for control, answer in [("(-2)^2", 4), ("-2^2", -4)]:
                result = client.post("/api/v1/evaluate", json={"expression": control})
                assert result.status_code == 200, result.text
                payload = result.json()
                assert payload["success"] is True, payload
                assert payload["result_approx"] == answer, (control, payload)
