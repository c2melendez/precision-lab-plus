"""Suite exhaustiva original — Módulo 6: Matrices.

QA-only. No modifica código de producto.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

A = [["2","1"],["1","2"]]

def test_m6_add_subtract_multiply():
    add = post("matrix/operations", {
        "matrix_a": [["1","2"],["3","4"]],
        "matrix_b": [["5","6"],["7","8"]],
        "operation": "add",
    }).json()
    assert add["success"] is True
    assert add["result_data"] == [["6","8"],["10","12"]]

    sub = post("matrix/operations", {
        "matrix_a": [["1","2"],["3","4"]],
        "matrix_b": [["5","6"],["7","8"]],
        "operation": "subtract",
    }).json()
    assert sub["success"] is True
    assert sub["result_data"] == [["-4","-4"],["-4","-4"]]

    mul = post("matrix/operations", {
        "matrix_a": [["1","2"],["3","4"]],
        "matrix_b": [["5","6"],["7","8"]],
        "operation": "multiply",
    }).json()
    assert mul["success"] is True
    assert mul["result_data"] == [["19","22"],["43","50"]]

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

def test_m6_ref_rref():
    ref = post("matrix/ref", {"matrix": [["1","2"],["2","4"]]}).json()
    assert ref["success"] is True
    assert ref["result_data"] == [["1","2"],["0","0"]]

    rref = post("matrix/rref", {"matrix": [["1","2","3"],["2","4","6"]]}).json()
    assert rref["success"] is True
    assert rref["result_data"] == [["1","2","3"],["0","0","0"]]

def test_m6_power_zero_positive_and_negative():
    p0 = post("matrix/power", {"matrix": A, "exponent": 0}).json()
    assert p0["success"] is True
    assert p0["result_data"] == [["1","0"],["0","1"]]

    p2 = post("matrix/power", {"matrix": A, "exponent": 2}).json()
    assert p2["success"] is True
    assert p2["result_data"] == [["5","4"],["4","5"]]

    pm1 = post("matrix/power", {"matrix": A, "exponent": -1}).json()
    assert pm1["success"] is True
    assert pm1["result_data"] == [["2/3","-1/3"],["-1/3","2/3"]]

def test_m6_eigen_known_matrix():
    b = post("matrix/eigen", {"matrix": A}).json()
    assert b["success"] is True, b
    text = b["result_text"]
    assert "λ=1" in text and "λ=3" in text

def test_m6_singular_inverse_and_dimension_errors():
    singular = post("matrix/inverse", {"matrix": [["1","2"],["2","4"]]}).json()
    assert singular["success"] is False
    assert singular["error_code"] == "SINGULAR_MATRIX"

    nonsquare_det = post("matrix/determinant", {"matrix": [["1","2","3"],["4","5","6"]]}).json()
    assert nonsquare_det["success"] is False
    assert nonsquare_det["error_code"] == "DIMENSION_MISMATCH"

    nonsquare_trace = post("matrix/trace", {"matrix": [["1","2","3"],["4","5","6"]]}).json()
    assert nonsquare_trace["success"] is False
    assert nonsquare_trace["error_code"] == "DIMENSION_MISMATCH"

    badmul = post("matrix/operations", {
        "matrix_a": [["1","2","3"]],
        "matrix_b": [["1","2"],["3","4"]],
        "operation": "multiply",
    }).json()
    assert badmul["success"] is False
    assert badmul["error_code"] == "DIMENSION_MISMATCH"
