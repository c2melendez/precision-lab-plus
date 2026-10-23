"""Integración HTTP del contrato S26 de resultados.

Prueba el pipeline parser -> motor -> MathResponse, no solo helpers aislados.
"""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_evaluate_rational_keeps_domain_and_contextual_views():
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "(x**2-1)/(x-1)"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["result_kind"] == "rational"
    keys = [view["key"] for view in body["result_views"]]
    assert "original" in keys
    assert "simplified" in keys
    assert any(
        condition["kind"] == "denominator"
        and condition["variable"] == "x"
        for condition in body["domain_conditions"]
    )


def test_numeric_trig_input_keeps_trigonometric_family():
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "sin(pi/6)"},
    )
    body = response.json()

    assert body["success"] is True
    assert body["result_kind"] == "trigonometric"
    assert body["result_approx"] is not None
    assert body["result_views"][0]["key"] == "original"


def test_complex_scalar_exposes_four_forms_plus_original():
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "2+3*i"},
    )
    body = response.json()

    assert body["success"] is True
    assert body["result_kind"] == "complex"
    assert [view["key"] for view in body["result_views"]] == [
        "original",
        "complex_binomial",
        "complex_polar",
        "complex_trigonometric",
        "complex_exponential",
    ]


def test_quadratic_complex_roots_use_original_and_solution_only():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "x**2+1=0", "variable": "x", "angle_unit": "rad"},
    )
    body = response.json()

    assert body["success"] is True
    assert body["result_kind"] == "equation"
    assert [view["key"] for view in body["result_views"]] == ["original", "solution"]
    assert len(body["result_data"]) == 2
    assert all(solution["is_complex"] for solution in body["result_data"])


def test_factor_view_carries_its_verified_steps():
    response = client.post(
        "/api/v1/factor",
        json={"expression": "x**2-4"},
    )
    body = response.json()

    assert body["success"] is True
    factor_view = next(view for view in body["result_views"] if view["key"] == "factored")
    assert factor_view["has_detailed_steps"] is True
    assert factor_view["steps"]
    assert factor_view["steps"][0]["title"] == "Diferencia de cuadrados"
