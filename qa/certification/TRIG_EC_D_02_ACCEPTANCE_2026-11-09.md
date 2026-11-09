# Aceptación: Trigonometría EC-D-02

- Estado: **PASS_SCOPED bilateral**.
- Fuente congelada: \`qa/certification/legacy_sources/ejercicios_trigonometria.md.gz\`, blob \`3a41b0c2e0d79f2eef48e4684dc1324689d0a0fb\`.
- Fila original: \`EC-D-02\`; ecuación \`2\cos x-1=0,\quad x\in[0,2\pi)\`; resultado esperado \`x=\frac{\pi}{3},\ \frac{5\pi}{3}\`. La fila tiene tres columnas (ID, ejercicio y resultado esperado); no hay una nota separada.
- SHA técnico Plus: \`6a150e29bba160fd4f2cff92748dee0baccb35a2\`.
- Test focal: \`backend/tests/test_trigonometry_ec_d02.py\`; ancla la fila fuente y verifica vía \`POST /api/v1/solve\` las dos raíces exactas, el intervalo y la sustitución. La entrada HTTP usada es ASCII: \`2*cos(x)-1=0\`.
- Cumulative [42669733996](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669733996) SUCCESS: ambos tests EC-D-02 PASSED; backend 2,925 passed, 1 skipped, 11 xfailed. Guard: \`skip=false\`, \`evidence_run_id=""\`; ejecución real en este SHA.
- CI [42669734319](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734319) SUCCESS, backend y frontend; backend 2,925 passed, 1 skipped, 11 xfailed.
- H1d [42669734287](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734287) SUCCESS; guard \`skip=false\`, sin \`evidence_run_id\`.
- Runner [42669734406](https://github.com/c2melendez/precision-lab-plus/actions/runs/42669734406) SUCCESS, evento push; sin dispatch manual.

## Alcance y límites

- Verificado: las raíces exactas \`{\pi/3,5\pi/3}\` son las únicas del intervalo \`[0,2\pi)\`, pertenecen al intervalo y satisfacen la ecuación.
- La entrada de Plus fue ASCII por \`/api/v1/solve\`; esta evidencia no certifica ingesta literal LaTeX ni \`/api/v1/evaluate\`.
- No se certifica la familia periódica infinita sobre \(\mathbb R\); ese contrato distinto corresponde a EC-D-03.
- Resultado: **PASS_SCOPED**, no cierre de la matriz trigonométrica ni de IN625.
- Certificación global: **OPEN**. EV-D-01 en \`/api/v1/evaluate\` permanece BLOCKED; EV-HI PASS_SCOPED; S25, SG28, H2 y DIST continúan abiertos.
