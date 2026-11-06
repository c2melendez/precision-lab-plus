# Algebra229 AS-A-17 — aceptación scoped bilateral

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre solo AS-A-17; no certifica el cierre de las 229 filas ni la certificación global.

## Contrato y fuente
- Entrada: `(2x-y)^5`.
- Salida contractual: `32x^5 - 80x^4y + 80x^3y^2 - 40x^2y^3 + 10xy^4 - y^5`.
- Fixture congelado: `qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz`; SHA-256 del contenido descomprimido `8cd36ff08343f98f92abd83e2b162d565e0cbe5c59dc73f26b1c018f77d663c7`.
- Test Plus: `backend/tests/test_algebra229_as_a17.py`, blob `ed9052343bec6a4347d3075933135e2839809bfd`; coteja las celdas de contrato, el servicio y HTTP `POST /api/v1/expand`, y siete pares enteros con coeficientes Python nativos independientes.
- La primera aserción `"**5" not in result_text` fue un falso negativo del harness: prohibía los monomios válidos (x^5) y (y^5). Se corrigió para rechazar únicamente la potencia original sin expandir y exigir `sp.expand(got) == got`; no hubo cambio de producto.

## Evidencia ejecutada
- SHA corregido Plus: `6b1bf9b9f731d6f6d36c16f33f09d1a9f2eb3238`.
- Acumulativo [42040844511](https://github.com/c2melendez/precision-lab-plus/actions/runs/42040844511): **SUCCESS**, guard `skip=false`; ambos focales PASSED; backend 2,800 passed, 1 skipped, 10 xfailed; cobertura 88.93%.
- H1d [42040844847](https://github.com/c2melendez/precision-lab-plus/actions/runs/42040844847): **SUCCESS**, 38/38.
- CI [42040844459](https://github.com/c2melendez/precision-lab-plus/actions/runs/42040844459): **SUCCESS**, backend 2,800 passed y frontend 1,055 passed.
- Runner [42040844455](https://github.com/c2melendez/precision-lab-plus/actions/runs/42040844455): job **SUCCESS**.

## Alcance y decisión
Los gates relevantes de Plus aprobaron la fila corregida. En conjunto con los gates matemáticos/UI aprobados de Lite, AS-A-17 queda PASS_SCOPED bilateral. El conflicto contractual EDCX-B6 VC-FE-45/EV-I-12 y H2/SG28 distribuido siguen bloqueados por separado. No se cambió código de producto.
