"""Algebra229 AS-B-30 `valor` primality question: frozen row, HTTP, independent oracle."""
import gzip
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = r"\text{¿es primo }1000000007?"
ORIGINAL = 1000000007


def _evaluate(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "evaluate", result
    assert result["request_id"], result
    return result


def _trial_division_is_prime(value: int) -> bool:
    """Independent primality check; does not use the product's Miller-Rabin."""
    if type(value) is not int or value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def test_as_b30_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-B-30 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-B-30",
        "N3",
        "`valor`",
        r"`\text{¿es primo }1000000007?`",
        "sí, es primo",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_b30_http_answers_the_prime_question_exactly():
    result = _evaluate(INPUT)
    assert result["result_text"] == "sí, es primo", result
    assert result["result_type"] == "boolean", result
    assert result["error_code"] is None, result


def test_as_b30_independent_oracle_confirms_prime_and_rejects_composite():
    assert _trial_division_is_prime(ORIGINAL) is True
    assert _evaluate(INPUT)["result_text"] == "sí, es primo"

    composite = 1000000008
    assert _trial_division_is_prime(composite) is False
    result = _evaluate(r"\text{¿es primo }" + str(composite) + "?")
    assert result["result_text"] == "no, es compuesto", result
