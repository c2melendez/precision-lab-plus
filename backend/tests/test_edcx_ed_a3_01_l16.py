"""EDCX Parte A · A3 "Sistemas y exponencial matricial" (16 filas).

Canal
-----
La fuente congela sistemas como `\\begin{cases}x'=x\\\\y'=2y\\end{cases}`. El motor
EDO del producto es escalar (`y(x)`), así que el canal `/api/v1/ode` no acepta un
sistema: se mide y se registra como BLOCKED, nunca como PASS. La clasificación
cualitativa del origen (ED-M-11..13) sí tiene canal real: `/matrix/eigen` devuelve
los autovalores; la etiqueta «silla / foco estable / centro» la deduce el usuario
a partir de ellos, y así se documenta (PASS_SCOPED).

Oráculo
-------
Autovalores calculados aquí con SymPy sobre la misma matriz; se exige que cada
valor aparezca con su forma exacta en la respuesta del producto. No se compara
contra el texto de la columna «Resultado esperado».

Bloqueos medidos
----------------
- ED-M-01..07: sistema de EDOs; `/ode` devuelve `PARSE_ERROR` (solo `y(x)`).
- ED-M-08..10: `e^{At}`; no existe operación de exponencial matricial: el enum
  de `/matrix/operations` rechaza `expm` con 422 y `/ode` devuelve `PARSE_ERROR`.
- ED-M-14..16: sistemas no lineales / Lyapunov; `/ode` devuelve `PARSE_ERROR`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services import ode_service

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_edo_variable_compleja.md.gz"
JSONL = ROOT / "qa/certification/edcx_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
A3 = [row for row in ROWS if row["bloque"] == "A3"]

# Sistemas: el campo único del producto no los representa (sin `y(x)`).
SYSTEM_INPUT = {
    "ED-M-01": "x'=x, y'=2*y",
    "ED-M-02": "x'=y, y'=-x",
    "ED-M-03": "x'=3*x+y, y'=x+3*y",
    "ED-M-04": "x'=x-y, y'=x+y",
    "ED-M-05": "x'=2*x+y, y'=2*y",
    "ED-M-06": "x'=y+1, y'=-x",
    "ED-M-07": "x'=y, y'=-2*x-3*y, x(0)=1, y(0)=0",
    "ED-M-14": "x'=x*(1-y), y'=y*(x-1)",
    "ED-M-15": "x'=-y+x*(1-x^2-y^2), y'=x+y*(1-x^2-y^2)",
    "ED-M-16": "x'=-y-x^3, y'=x-y^3",
}

MATRIX_EXPONENTIAL_INPUT = {
    "ED-M-08": "exp(A*t), A=[[0,1],[-1,0]]",
    "ED-M-09": "exp(A*t), A=[[lambda,1],[0,lambda]]",
    "ED-M-10": "exp(A*t), A=[[2,1],[1,2]]",
}

# ED-M-11..13: clasificación del origen desde los autovalores.
EIGEN = {
    "ED-M-11": [["1", "2"], ["3", "2"]],
    "ED-M-12": [["-1", "1"], ["-1", "-1"]],
    "ED-M-13": [["0", "1"], ["-1", "0"]],
}
EXPECTED_EIGENVALUES = {
    "ED-M-11": [sympy.Integer(4), sympy.Integer(-1)],
    "ED-M-12": [sympy.Integer(-1) - sympy.I, sympy.Integer(-1) + sympy.I],
    "ED-M-13": [sympy.I, -sympy.I],
}

BLOCKED = set(SYSTEM_INPUT) | set(MATRIX_EXPONENTIAL_INPUT)


def frozen_source() -> str:
    import gzip

    return gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")


def test_edcx_fixture_a3_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A3) == 16
    assert set(EIGEN) | BLOCKED == {row["id"] for row in A3}
    assert not (set(EIGEN) & BLOCKED)
    source = frozen_source()
    for row in A3:
        assert f"| {row['id']} |" in source


@pytest.mark.parametrize("row", [r for r in A3 if r["id"] in EIGEN], ids=lambda r: r["id"])
def test_edcx_a3_origin_classification_reports_the_exact_eigenvalues(row: dict):
    with TestClient(app) as client:
        response = client.post("/api/v1/matrix/eigen", json={"matrix": EIGEN[row["id"]]})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body.get("error_message")
    assert body["operation"] == "matrix_eigen"
    text = body["result_text"]
    for value in EXPECTED_EIGENVALUES[row["id"]]:
        assert sympy.sstr(value) in text, f"{row['id']}: falta {sympy.sstr(value)} en {text}"
    # La etiqueta cualitativa (silla/foco/centro) no la emite el producto.
    assert "silla" not in text.lower() and "foco" not in text.lower()


@pytest.mark.parametrize("row", [r for r in A3 if r["id"] in SYSTEM_INPUT], ids=lambda r: r["id"])
def test_edcx_a3_systems_are_rejected_by_the_scalar_ode_channel(row: dict):
    with TestClient(app) as client:
        body = client.post("/api/v1/ode", json={"expression": SYSTEM_INPUT[row["id"]]}).json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert body["error_message"]


@pytest.mark.parametrize("row", [r for r in A3 if r["id"] in MATRIX_EXPONENTIAL_INPUT], ids=lambda r: r["id"])
def test_edcx_a3_matrix_exponential_has_no_operation(row: dict):
    with TestClient(app) as client:
        ode = client.post(
            "/api/v1/ode", json={"expression": MATRIX_EXPONENTIAL_INPUT[row["id"]]}
        ).json()
        assert ode["success"] is False
        assert ode["error_code"] == "PARSE_ERROR"
        # El enum de operaciones matriciales no expone exponencial: 422 medido.
        operations = client.post(
            "/api/v1/matrix/operations",
            json={"matrix_a": [["0", "1"], ["-1", "0"]], "operation": "expm"},
        )
    assert operations.status_code == 422, operations.text
    assert operations.json()["success"] is False
