# Algebra229 AS-A-15 — aceptación bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Este registro certifica únicamente AS-A-15; no certifica el cierre de las 229 filas ni la certificación global.

## Contrato y oráculo
- Caso: `(x+1/x)^3 = x^3 + 3x + 3/x + 1/x^3`, con dominio explícito `x != 0`.
- Fuente normativa: `legacy_sources/matriz_algebra_simbolica.md.gz`, SHA-256 descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test: `backend/tests/test_algebra229_as_a15.py`, blob `f57231bd0e9625bcc7eeef2068d8e9260cb3298b`. Verifica la fila fuente completa, la ruta de servicio/HTTP, igualdad simbólica y siete fracciones no nulas con aritmética Python `Fraction` independiente.

## Evidencia ejecutada
- Checkout técnico Plus: `1f462162d74effb8f1a9a1c45271f99a6b3887eb`.
- Acumulativo [42035518039](https://github.com/c2melendez/precision-lab-plus/actions/runs/42035518039): **SUCCESS**, guard `skip=false`; ambos tests focales PASSED; backend 2,800 passed / 1 skipped / 10 xfailed; cobertura 88.91%.
- H1d [42035518483](https://github.com/c2melendez/precision-lab-plus/actions/runs/42035518483): **SUCCESS**, 38/38.
- CI estándar [42035518143](https://github.com/c2melendez/precision-lab-plus/actions/runs/42035518143): **SUCCESS**; backend 2,800 passed; frontend 150 archivos / 1,055 passed.
- Runner [42035518500](https://github.com/c2melendez/precision-lab-plus/actions/runs/42035518500): SUCCESS, push-only.

## Cierre
AS-A-15 queda **PASS_SCOPED** para Plus y, junto con el registro Lite, bilateralmente aceptado. Siguiente caso: AS-A-16. Certificación global: **OPEN**.
