"""Suite exhaustiva original — Módulo 6: Matrices.

QA-only. No modifica código de producto.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

A = [["2","1"],["1","2"]]

def test_m6_determinant_inverse_transpose_rank_trace():
    det = post("matrix/determinant", {"matrix": A}).json()
    assert det["success"] is True and det["result_text"] == "3"

    inv = post("matrix/inverse", {"matrix": A}).json()
    assert inv["success"] is True
    assert inv["result_data"] == [["2/3","-1/3"],["-1/3","2/3"]]

    tr = post("matrix/transpose", {"matrix": [["1","2","3"],["4","5","6"]]}).json()
    assert tr["success"] is True
    assert tr["result_data"] == [["1","4"],["2","5"],["3","6"]]

    rank = post("matrix/rank", {"matrix": [["1","2"],["2","4"]]}).json()
    assert rank["success"] is True and rank["result_text"] == "1"

    trace = post("matrix/trace", {"matrix": A}).json()
    assert trace["success"] is True and trace["result_text"] == "4"

def test_m6_ref_rref_and_multiply():
    ref = post("matrix/ref", {"matrix": [["1","2"],["2","4"]]}).json()
    assert ref["success"] is True

    rref = post("matrix/rref", {"matrix": [["1","2","3"],["2","4","6"]]}).json()
    assert rref["success"] is True
    assert rref["result_data"][0] == ["1","2","3"]

    mul = post("matrix/operations", {
        "matrix_a": [["1","2"],["3","4"]],
        "matrix_b": [["5","6"],["7","8"]],
        "operation": "multiply",
    }).json()
    assert mul["success"] is True
    assert mul["result_data"] == [["19","22"],["43","50"]]

def test_m6_eigen_known_matrix():
    b = post("matrix/eigen", {"matrix": A}).json()
    assert b["success"] is True, b
    text = b["result_text"]
    assert "1" in text and "3" in text

def test_m6_singular_inverse_and_dimension_errors():
    singular = post("matrix/inverse", {"matrix": [["1","2"],["2","4"]]}).json()
    assert singular["success"] is False
    assert singular["error_code"] == "SINGULAR_MATRIX"

    nonsquare_det = post("matrix/determinant", {"matrix": [["1","2","3"],["4","5","6"]]}).json()
    assert nonsquare_det["success"] is False
    assert nonsquare_det["error_code"] == "DIMENSION_MISMATCH"

    badmul = post("matrix/operations", {
        "matrix_a": [["1","2","3"]],
        "matrix_b": [["1","2"],["3","4"]],
        "operation": "multiply",
    }).json()
    assert badmul["success"] is False
    assert badmul["error_code"] == "DIMENSION_MISMATCH"
