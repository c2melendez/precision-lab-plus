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
