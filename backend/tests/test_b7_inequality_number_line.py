"""B7: canonical interval semantics for the one-variable number line."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def solve(expression):
    response = client.post("/api/v1/inequality", json={"inequality": expression})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["inequality_variable"] == "x"
    return body


def test_open_and_closed_endpoints():
    strict = solve("x>0")
    inclusive = solve("x>=0")
    assert strict["inequality_intervals"] == [{"lower": 0.0, "upper": None,
        "lower_text": "0", "upper_text": None, "lower_included": False, "upper_included": False}]
    assert inclusive["inequality_intervals"][0]["lower_included"] is True
    assert strict["result_latex"] != inclusive["result_latex"]


def test_union_empty_and_all_real_numbers():
    union = solve("x**2>=1")["inequality_intervals"]
    assert len(union) == 2
    assert union[0]["upper"] == -1 and union[0]["upper_included"] is True
    assert union[1]["lower"] == 1 and union[1]["lower_included"] is True
    assert solve("x**2<0")["inequality_intervals"] == []
    whole = solve("x**2>=0")["inequality_intervals"]
    assert len(whole) == 1 and whole[0]["lower"] is None and whole[0]["upper"] is None
