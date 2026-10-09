"""IN625 H2 safe negative security tranche (in-process TestClient only).

Do not send payloads to deployment endpoints. These are rejection checks,
not proof of browser escaping, sandboxing, or resource-limit behavior.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-09", "__import__('os').system('ls')"),
    ("EN-SG-10", "open('/etc/passwd').read()"),
    ("EN-SG-11", "().__class__.__bases__[0].__subclasses__()"),
    ("EN-SG-12", "(lambda x: x)(1)"),
    ("EN-SG-13a", 'exec("print(1)")'),
    ("EN-SG-13b", 'eval("1+1")'),
    ("EN-SG-14", "import os"),
    ("EN-SG-15", "x.__class__"),
    ("EN-SG-16", "Symbol('x')"),
])
def test_in625_h2_rejects_python_constructs_without_evaluation(case_id, expression):
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code != 500, (case_id, response.text[:180])
    assert response.status_code == 200, (case_id, response.status_code)
    result = response.json()
    assert result.get("success") is False, (case_id, result)
    assert result.get("error_code") == "PARSE_ERROR", (case_id, result)
    assert "traceback" not in str(result.get("error_message", "")).lower()

# Additional variants explicitly listed in the source H2 security matrix.
@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-14 system", 'os.system("ls")'),
    ("EN-SG-15 dict", "x.__dict__"),
    ("EN-SG-16 Integer", "Integer(2)"),
    ("EN-SG-16 Function", "Function('f')"),
])
def test_in625_h2_rejects_additional_python_variants(case_id, expression):
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 200, (case_id, response.status_code)
    result = response.json()
    assert result.get("success") is False, (case_id, result)
    assert result.get("error_code") == "PARSE_ERROR", (case_id, result)
    assert "traceback" not in str(result.get("error_message", "")).lower()

def test_in625_h2_sg17_assignment_does_not_leak_between_evaluations():
    """EN-SG-17: a=7 must not persist as mutable shared CAS state."""
    client.post("/api/v1/evaluate", json={"expression": "a=7", "angle_unit": "rad"})
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "a+1", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text[:200]
    result = response.json()
    # Either an explicit unsupported symbolic evaluation, or an algebraic
    # result containing the free variable; never a leaked numeric 8.
    if result.get("success"):
        rendered = str(result.get("result", result.get("output", result)))
        assert rendered.strip() != "8", result
    else:
        assert result.get("error_code"), result

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-30 quote", 'x"y'),
    ("EN-SG-30 apostrophe", "x'y"),
    ("EN-SG-30 slash", "x\\\\y"),
    ("EN-SG-30 nul", "x\\x00y"),
    ("EN-SG-30 crlf", "x\\r\\ny"),
])
def test_in625_h2_sg30_special_characters_are_valid_json_requests(case_id, expression):
    """In-process JSON transport: malformed math should not crash the API."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code not in (400, 500), (case_id, response.text[:200])

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-18 clearall", "clearall"),
    ("EN-SG-18 draw", "draw"),
    ("EN-SG-18 run", "run"),
    ("EN-SG-18 last", "last"),
    ("EN-SG-18 lambda", "lambda"),
])
def test_in625_h2_sg18_reserved_words_cannot_execute_commands(case_id, expression):
    """Reserved words must remain inert: symbolic result or controlled rejection."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 200, (case_id, response.status_code)
    result = response.json()
    if result.get("success") is False:
        assert result.get("error_code"), (case_id, result)
    else:
        serialized = str(result).lower()
        assert "traceback" not in serialized, (case_id, result)

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-18 symbol S", "S"),
    ("EN-SG-18 symbol N", "N"),
])
def test_in625_h2_sg18_remaining_reserved_symbols_are_inert(case_id, expression):
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 200, (case_id, response.status_code)
    result = response.json()
    if not result.get("success"):
        assert result.get("error_code"), (case_id, result)
    else:
        assert "traceback" not in str(result).lower(), (case_id, result)

@pytest.mark.parametrize("expression", ["clearall", "draw", "run", "last", "lambda", "S", "N"])
def test_in625_h2_sg18_reserved_word_request_preserves_following_calculation(expression):
    """A reserved-token request must not disrupt subsequent independent calls."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 200, (expression, response.status_code)
    probe = client.post(
        "/api/v1/evaluate",
        json={"expression": "2+3", "angle_unit": "rad"},
    )
    assert probe.status_code == 200, (expression, probe.status_code)
    result = probe.json()
    assert result.get("success") is True, (expression, result)
    assert result.get("result_approx") == pytest.approx(5.0), (expression, result)

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-30 tab", "x\ty"),
    ("EN-SG-30 newline", "x\ny"),
])
def test_in625_h2_sg30_additional_json_control_characters(case_id, expression):
    """Additional JSON control characters are safely transported in-process."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code not in (400, 500), (case_id, response.text[:200])

@pytest.mark.parametrize("expression", ["clearall", "draw", "run", "last", "lambda", "S", "N"])
def test_in625_h2_sg18_reserved_word_does_not_change_symbolic_variable(expression):
    """SG18: after a reserved-token probe, a free symbol remains unbound."""
    client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    response = client.post("/api/v1/evaluate", json={"expression": "a+1", "angle_unit": "rad"})
    assert response.status_code == 200, (expression, response.status_code)
    result = response.json()
    if result.get("success"):
        assert result.get("result_approx") != 8, (expression, result)
    else:
        assert result.get("error_code"), (expression, result)

@pytest.mark.parametrize("expression", ["clearall", "draw", "run", "last", "lambda", "S", "N"])
def test_in625_h2_sg18_reserved_word_cannot_corrupt_independent_numeric_result(expression):
    """SG18: a second independent numeric operation is stable after a reserved token."""
    client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    response = client.post("/api/v1/evaluate", json={"expression": "7*6", "angle_unit": "rad"})
    assert response.status_code == 200, (expression, response.status_code)
    result = response.json()
    assert result.get("success") is True, (expression, result)
    assert result.get("result_approx") == pytest.approx(42.0), (expression, result)

@pytest.mark.parametrize("expression", ["clearall", "draw", "run", "last", "lambda", "S", "N"])
def test_in625_h2_sg18_repeated_reserved_request_preserves_calculation(expression):
    """Check three sequential inert probes before a separate numerical query."""
    for _ in range(3):
        probe = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
        assert probe.status_code == 200, (expression, probe.status_code)
    response = client.post("/api/v1/evaluate", json={"expression": "3^2+1", "angle_unit": "rad"})
    assert response.status_code == 200, (expression, response.status_code)
    result = response.json()
    assert result.get("success") is True, (expression, result)
    assert result.get("result_approx") == pytest.approx(10.0), (expression, result)

@pytest.mark.parametrize("expression", ["clearall", "draw", "run", "last", "lambda", "S", "N"])
def test_in625_h2_sg18_reserved_token_does_not_change_subsequent_fraction(expression):
    """SG18: preserve independent exact rational evaluation after inert tokens."""
    client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    response = client.post("/api/v1/evaluate", json={"expression": "1/2+1/4", "angle_unit": "rad"})
    assert response.status_code == 200, (expression, response.status_code)
    body = response.json()
    assert body.get("success") is True, (expression, body)
    assert body.get("result_approx") == pytest.approx(0.75), (expression, body)

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-19", "(" * 50 + "1" + ")" * 50),
    ("EN-SG-20", "(" * 1000 + "1" + ")" * 1000),
])
def test_in625_h2_sg19_sg20_parentheses_depth_controlled(case_id, expression):
    """Bounded in-process nested input; no expensive symbolic expansion."""
    response = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    result = response.json()
    if case_id == "EN-SG-19":
        assert response.status_code == 200, (case_id, response.status_code)
        assert result.get("success") is True, (case_id, result)
        assert result.get("result_approx") == pytest.approx(1.0), (case_id, result)
    else:
        # EvaluateRequest has max_length=500. The 2,001-character SG20 input
        # is rejected at the request-validation boundary, before parser depth.
        # This certifies safe rejection, NOT an internal recursion-depth guard.
        assert response.status_code == 422, (case_id, response.status_code, result)
        assert result.get("success") is False, (case_id, result)
        assert result.get("error_code") == "VALIDATION_ERROR", (case_id, result)
        assert result.get("error_message"), (case_id, result)
        assert "traceback" not in str(result).lower(), (case_id, result)

@pytest.mark.parametrize("case_id, expression", [
    ("EN-SG-22", "1" * 100_000),
])
def test_in625_h2_oversized_expression_rejected_at_request_boundary(case_id, expression):
    """EN-SG-22: request schema safely rejects a 100k-character expression.

    EN-SG-31 5 MiB body is covered separately by its dedicated HTTP 413 test.
    """
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 422, (case_id, response.status_code)
    body = response.json()
    assert body.get("success") is False, (case_id, body)
    assert body.get("error_code") == "VALIDATION_ERROR", (case_id, body)

def test_in625_h2_sg31_five_mib_json_body_returns_413():
    """EN-SG-31: explicit content-length 5 MiB is rejected before schema parsing."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "1" * (5 * 1024 * 1024), "angle_unit": "rad"},
    )
    assert response.status_code == 413, response.status_code
    body = response.json()
    assert body.get("success") is False, body
    assert body.get("error_code") == "PAYLOAD_TOO_LARGE", body
    assert body.get("error_message"), body

def test_in625_h2_sg31_body_without_content_length_is_rejected():
    """ASGI request without length header: 5 MiB body gets HTTP 413."""
    import json
    import httpx

    payload = json.dumps({"expression": "1" * (5 * 1024 * 1024), "angle_unit": "rad"}).encode()
    async def body_stream():
        for offset in range(0, len(payload), 8192):
            yield payload[offset:offset + 8192]

    # TestClient's streaming body generally sets transfer-encoding: chunked,
    # with no Content-Length, while staying within the local ASGI app.
    response = client.post(
        "/api/v1/evaluate",
        content=body_stream_sync(payload),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413, response.status_code
    assert response.json().get("error_code") == "PAYLOAD_TOO_LARGE"


def body_stream_sync(payload):
    for offset in range(0, len(payload), 8192):
        yield payload[offset:offset + 8192]
