"""Precision Lab canonical certification pilot v1.

Runs product HTTP endpoints through FastAPI TestClient and writes the same
machine-readable result schema used by Lite. This is product execution, not an
oracle generator: expected values come from the independently audited fixture.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import sympy
from fastapi.testclient import TestClient

from app.main import app

ROOT = BACKEND_ROOT
FIXTURE = ROOT / "qa" / "certification" / "certification_cases_v1.json"
OUTPUT = ROOT / "artifacts" / "certification-results-plus.json"
client = TestClient(app, raise_server_exceptions=False)


def equivalent(actual: str, expected: str) -> bool:
    try:
        return sympy.simplify(sympy.sympify(actual) - sympy.sympify(expected)) == 0
    except Exception:
        return False


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = []
    for case in fixture["cases"]:
        adapter = case["adapters"]["plus"]
        operation = case["operation"]
        row = {"id": case["id"], "operation": operation, "expected": adapter["expected"]}
        try:
            if operation == "derivative":
                payload = {
                    "expression": adapter["expression"],
                    "variable": adapter.get("variable", "x"),
                    "order": adapter.get("order", 1),
                }
            else:
                payload = {"expression": adapter["expression"]}
            response = client.post(f"/api/v1/{operation}", json=payload)
            body = response.json()
            if response.status_code != 200 or not body.get("success"):
                row.update(status="ERROR", error=f"HTTP {response.status_code}: {body}")
            else:
                actual = body.get("result_text")
                ok = isinstance(actual, str) and equivalent(actual, adapter["expected"])
                row.update(status="PASS" if ok else "FAIL", actual=actual)
        except Exception as exc:
            row.update(status="ERROR", error=repr(exc))
        rows.append(row)

    summary = {
        "total": len(rows),
        "pass": sum(r["status"] == "PASS" for r in rows),
        "fail": sum(r["status"] == "FAIL" for r in rows),
        "error": sum(r["status"] == "ERROR" for r in rows),
    }
    report = {
        "schema_version": "1.0",
        "suite_id": fixture["suite_id"],
        "engine": "plus",
        "layer": "L1",
        "git_sha": os.environ.get("GITHUB_SHA"),
        "summary": summary,
        "results": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["fail"] == 0 and summary["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
