from pathlib import Path
import gzip

from fastapi.testclient import TestClient

from backend.main import app


def test_ev_d05_source_row_is_present_and_frozen():
    source = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
    with gzip.open(source, "rt", encoding="utf-8") as handle:
        text = handle.read()
    row = next((line for line in text.splitlines() if "| EV-D-05 |" in line), "")
    assert row
    assert r"\sec\left(\frac{\pi}{3}\right)" in row
    assert "| 2 |" in row or "| `2` |" in row


def test_ev_d05_sec_pi_over_3_evaluates_to_exact_two_over_http():
    client = TestClient(app)
    response = client.post("/api/v1/evaluate", json={"expression": "sec(pi/3)"})
    assert response.status_code == 200
    payload = response.json()
    result = payload.get("result", payload.get("output", ""))
    assert str(result).replace(" ", "") == "2"
