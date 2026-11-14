# r526 — Reconciliación requerida por pérdida de continuidad

Global OPEN. El índice r525 de Lite omitió gates, evidencia, bloqueos, historial de runs y exclusiones; el de Plus omitió gates de evidencia y reemplazó la huella acumulativa por un marcador no calculado. Se recuperan las estructuras y antecedentes del índice r523 sin borrar r525; los datos anteriores son históricos, no prueba automática para el HEAD actual. Se conserva el SHA técnico Plus aa1f2821bb2d4df92dc94db0848a67141f4fb76a y el run Cumulative 43647668540 reportado en r525 para revisión. No se declara REUSE ni se despacha CI basándose en una huella textual.

Única acción siguiente: recuperar HEAD y runs completos push/PR de ambos productos, comparar árboles auténticos y acceptance_revision con `scripts/certification/continuity.py`, revisar gates del SHA técnico Plus aa1f2821 y reconciliar cierre IN-D-05 antes de ejecutar IN-D-06. Conservar S25, SG28/DIST y EV-D-01 BLOCKED hasta su evidencia propia; no repetir corridas equivalentes.

---

# r525 — IN-D-05: Cumulative Plus SUCCESS tras fix de timeout; cierre bilateral

Global OPEN; IN-D-05 se cierra PASS_SCOPED. Fix técnico aa1f2821bb2d4df92dc94db0848a67141f4fb76a (early structural filter in _arccot_two_pi_thirds_result) resolvió el timeout. Cumulative 43647668540 terminó SUCCESS: backend job 132608950017 3031 passed, 1 skipped, 11 xfailed (AS-PAR-05 pasó en 39.24s); frontend SUCCESS. Native 43647668581 SUCCESS. Lite mantiene evidencia SUCCESS previa (Cumulative 43637613663 etc.).

No se relajó oráculo ni límite. S25, SG28/DIST y EV-D-01 siguen BLOCKED.

Siguiente acción única: iniciar IN-D-06 según protocolo; no reabrir IN-D-05.

---

# r524 — Native SUCCESS; Cumulative WAIT para verificación del fix de timeout AS-PAR-05

Global OPEN; IN-D-05 no se cierra. Fix técnico aa1f2821bb2d4df92dc94db0848a67141f4fb76a: early structural filter in arccot handler to avoid CI timeout on unrelated equations. Native Syntax 43647668581 SUCCESS (26 desktop, 52 tablet/móvil).

Cumulative 43647668540 en curso: frontend SUCCESS, backend job 132608950017 in_progress (regresión). No reutilizar el fallo previo 43637618246. Si el backend pasa sin timeout en AS-PAR-05, reconciliar cierre bilateral; no avanzar a IN-D-06.

S25, SG28/DIST y EV-D-01 siguen BLOCKED. Lite mantiene evidencia previa SUCCESS.

Siguiente acción única: esperar y revisar el job backend del Cumulative 43647668540; clasificar resultado y actualizar estado. No despachar equivalentes.

---

# r523 — IN-D-05: fallo acumulativo Plus en diagnóstico

Global OPEN; IN-D-05 no se cierra. Plus Cumulative 43637618246/job backend 132577800977 terminó FAILURE: 3030 passed, 1 failed, 1 skipped, 11 xfailed. Las seis pruebas IN-D-05 pasaron, pero AS-PAR-05 (`tests/test_algebra114_as_par05.py::test_as_par_05_original_real_domain_parameter_quadratic_service_and_http`) agotó el timeout de pytest de 60 s en SymPy. La causa de rendimiento aún no está demostrada; no clasificar el fallo como producto o harness sin reproducirlo. El CI separado 43637618227/backend 132577801082 pasó con 3031 passed, 1 skipped y 11 xfailed; no sustituye el gate acumulativo fallido. No relanzar idéntico hasta diagnóstico y cambio de insumos/precondición.

Lite Scientific 43637613653 pasó 456/456 y Plus Native 43637618217 pasó 26 desktop y 52 tablet/móvil, según r522. Plus campaña de seguridad 43637618276/job 132577946517 continúa en curso; los jobs frontend omitidos no son PASS. S25, SG28/DIST y EV-D-01 siguen bloqueados.

Siguiente acción única: diagnosticar el timeout de AS-PAR-05 con reproducción focal y perfilado bajo las condiciones de Cumulative, preservar todas las aserciones y el límite contractual; corregir la causa demostrada en la capa correspondiente y verificar el gate acumulativo sobre el nuevo SHA. Después reconciliar IN-D-05; no avanzar a IN-D-06 hasta cierre bilateral.
