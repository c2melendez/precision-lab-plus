#!/usr/bin/env python3
import base64, zlib
from pathlib import Path
parts = sorted(Path("scripts/mvf_blob_chunks").glob("chunk_*.txt"))
blob = "".join(p.read_text() for p in parts)
path = Path("backend/app/services/matrix_service.py")
path.write_bytes(zlib.decompress(base64.b64decode(blob)))
print("restored", path, path.stat().st_size)
assert b"MAX_MATRIX_POWER_EXPONENT = 32" in path.read_bytes()
assert b"def determinant" in path.read_bytes()
