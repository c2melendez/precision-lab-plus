#!/usr/bin/env python3
"""Derive `edcx_ejecutables.jsonl` from the frozen EDCX source.

The frozen source is `qa/certification/legacy_sources/matriz_edo_variable_compleja.md.gz`
(sha256 pinned in MANIFEST.json). This script only extracts the table rows and
normalizes the documented JSONL fields; it never computes or alters an oracle.

Usage (from the repository root):

    python3 qa/certification/derive_edcx_ejecutables.py
    python3 qa/certification/derive_edcx_ejecutables.py --check

`--check` regenerates in memory and reports whether the committed JSONL matches.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_GZ = HERE / "legacy_sources" / "matriz_edo_variable_compleja.md.gz"
OUTPUT = HERE / "edcx_ejecutables.jsonl"

EXPECTED_TOTAL = 638
EXPECTED_BY_PART = {"A": 210, "B": 428}
# Documented in MATRIX_SOURCE_INVENTORY.md / the frozen source headings.
EXPECTED_BY_BLOCK = {
    "A1": 53, "A2": 50, "A3": 16, "A4": 24, "A5": 10, "A6": 26, "A7": 25, "A8": 6,
    "B1": 49, "B2": 41, "B3": 19, "B4": 34, "B5": 25, "B6": 53, "B7": 27, "B8": 32,
    "B9": 44, "B10": 26, "B11": 24, "B12": 18, "B13": 9, "B14": 15, "B15": 12,
}

BLOCK_RE = re.compile(r"^##\s+([AB])(\d+)\.\s*(.*)$")
SUB_RE = re.compile(r"^###\s+([AB])(\d+)\.([A-Z])(?:\s|$)")
ID_RE = re.compile(r"^(?:ED|VC)-[A-Z]+(?:-[A-Z])?-\d{2}$")


def uncode(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        return value[1:-1].strip()
    return value


def parse_rows(text: str) -> list[dict]:
    part = None
    block = None
    subblock = None
    rows: list[dict] = []
    in_summary = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# PARTE A"):
            part = "A"
            in_summary = False
            continue
        if stripped.startswith("# PARTE B"):
            part = "B"
            in_summary = False
            continue
        if stripped.startswith("## Resumen de cobertura"):
            in_summary = True
            continue
        header = BLOCK_RE.match(stripped)
        if header:
            part = header.group(1)
            block = f"{header.group(1)}{header.group(2)}"
            subblock = None
            continue
        sub = SUB_RE.match(stripped)
        if sub:
            subblock = sub.group(3)
            continue
        if in_summary or part is None or block is None:
            continue
        if not stripped.startswith("|") or set(stripped) <= set("|-: "):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells[0] in ("ID", "Forma de entrada", "Binómica", "Polar", "Trigonométrica", "Exponencial"):
            continue
        if len(cells) == 4:
            case_id, level, exercise, expected = cells
            channel = ""
        elif len(cells) == 5:
            case_id, level, channel, exercise, expected = cells
        else:
            raise SystemExit(f"unexpected row shape ({len(cells)}): {stripped[:120]}")
        if not ID_RE.match(case_id):
            raise SystemExit(f"unexpected id: {case_id}")
        rows.append({
            "matriz": "EDCX",
            "parte": part,
            "bloque": block,
            "subbloque": subblock,
            "id": case_id,
            "nivel": level,
            "canal": channel,
            "ejercicio": uncode(exercise),
            "esperado": uncode(expected),
        })
    return rows


def validate(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    if len(rows) != EXPECTED_TOTAL:
        errors.append(f"total rows {len(rows)} != {EXPECTED_TOTAL}")
    by_part = Counter(row["parte"] for row in rows)
    if dict(by_part) != EXPECTED_BY_PART:
        errors.append(f"rows by part {dict(by_part)} != {EXPECTED_BY_PART}")
    by_block = Counter(row["bloque"] for row in rows)
    if dict(by_block) != EXPECTED_BY_BLOCK:
        errors.append(f"rows by block {dict(by_block)} != {EXPECTED_BY_BLOCK}")
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        errors.append(f"duplicate ids: {dupes}")
    return errors


def render(rows: list[dict]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"


def main() -> int:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    rows = parse_rows(text)
    errors = validate(rows)
    if errors:
        for error in errors:
            print(f"invalid derivation: {error}", file=sys.stderr)
        return 1
    rendered = render(rows)
    if "--check" in sys.argv[1:]:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != rendered:
            print(f"{OUTPUT.name} is stale: re-run without --check", file=sys.stderr)
            return 1
        print(f"PASS_EDCX_FIXTURE {len(rows)} rows (A {EXPECTED_BY_PART['A']} / B {EXPECTED_BY_PART['B']})")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
