# Algebra229 AS-B-12 — aceptación scoped bilateral (Plus)

**Resultado: PASS_SCOPED bilateral.** Esta aceptación cubre exclusivamente AS-B-12.

## Contrato y fuente
- Fila congelada: AS-B-12, N2, `factorizar`, `x^{5}-x` → `x \left(x - 1\right) \left(x + 1\right) \left(x^{2} + 1\right)`.
- Test: `backend/tests/test_algebra229_as_b12.py`, blob `2f9aa3e6c51711567e1c78e6a974497aef6ba968`.
- Celdas exactas + `result_latex` exacto + cuatro factores + 10 sustituciones AST independientes.

## Evidencia SHA Plus `59f50596e617c09a75f9bc805d1e02fe8ac3824b`
- Acumulativo [42154151449](https://github.com/c2melendez/precision-lab-plus/actions/runs/42154151449): **SUCCESS**.
- H1d [42154151319](https://github.com/c2melendez/precision-lab-plus/actions/runs/42154151319): **FAILURE** en Install Playwright (flake infra npm; no contenido del test).
- CI [42154151439](https://github.com/c2melendez/precision-lab-plus/actions/runs/42154151439): **SUCCESS**.
- Runner [42154151387](https://github.com/c2melendez/precision-lab-plus/actions/runs/42154151387): **SUCCESS**.

## Decisión
PASS_SCOPED bilateral. El fallo H1d es infraestructura. Cumulative (tests unitarios) verde. Sin cambio de producto.
