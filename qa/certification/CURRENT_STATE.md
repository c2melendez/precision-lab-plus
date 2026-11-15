# r551 — Canal HTTP literal IN-I-04 corregido; gates pendientes

Plus SHA técnico 259bc52312a2ea6516d23c13af9773ac21b62353: la entrada fuente `\\arctan(2x)\\ge\\frac{\\pi}{4}` se normaliza con reconocimiento acotado y sigue por las validaciones de seguridad. Test-first: el HTTP literal fallaba con PARSE_ERROR; 281 pruebas locales de parser, seguridad y filas IN-I-03/04 aprobaron tras la corrección, incluidos controles de entrada insegura. No acredita E2E visual. Push acumulativo 43737435007, H1d 43737435025, Native 43737435068, CI 43737435042, seguridad 43737435043 en curso. La mutación anterior 43736559614 usa otro SHA y continúa; no duplicar ni cancelar. S19 REVIEW, S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción: revisar jobs/logs del SHA técnico y reporte de mutación 43736559614; no declarar cierre sin evidencia.

---

# r550 — Reconciliación S19: nuevo SHA técnico; gates en curso

HEAD técnico 97c35059f373826858754d3016ad4cd1799a237f añade pruebas dirigidas en backend/tests/test_solve.py. Push acumulativo 43736559606 y seguridad/mutación 43736559614 en curso; H1d 43736559582/job 132880342531 ejecutó 38 pruebas aprobadas. CI 43736559554 en curso. No repetir gates.

IN-I-04 SHA previo Plus 85bd8f500cc82b983b51c3a4e6712fd230e77e79: acumulativo 43731842899/backend 132865800703 (3086 passed, 1 skipped, 11 xfailed) y frontend 132865800906 (1055 passed, 28 TODO); H1d 43731842898 (38). Lite ae784152e808fbe5e8139e8406c6431bdeb7526e: acumulativo 43731839741 (2588 passed, 8 expected fail, 34 TODO), H1d 43731839781 (22), Scientific 43731839744 (456). Evidencia funcional anterior revisada; nuevo SHA Plus pendiente de gates antes de cierre.

Seguridad: 43725643047/job 132846991188 terminó con runner shutdown, sin reporte. 43715315873/job 132815595041 finalizó failure, pero el log responde 404 BlobNotFound y la corrida no tiene artefactos; causa no determinada, no PASS. S19 REVIEW, S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción única: revisar acumulativo y mutación 43736559606/43736559614, conservar S19 REVIEW y reconciliar IN-I-04 sin duplicar corridas.

---

# r549 — IN-I-04 publicado; verificación CI pendiente

Lite SHA ae784152e808fbe5e8139e8406c6431bdeb7526e; Plus SHA 85bd8f500cc82b983b51c3a4e6712fd230e77e79. Test-first: Lite no resolvía arctan(2x)>=π/4; se implementó [1/2,∞), igualdad incluida, fallback preservado. Plus ya resolvía el caso y recibió tests de fuente, servicio y HTTP. Local: Lite 85 pruebas y build aprobados; Plus 66 pruebas aprobadas. Push Lite acumulativo 43731839741, H1d 43731839781, Scientific 43731839744, CI 43731839734; Plus acumulativo 43731842899, H1d 43731842898, CI 43731842944: en curso o cola al registrar. Seguridad Plus 43715315873/job 132815595041 y 43725643047/job 132846991188 en curso sobre SHA distintos; S19 REVIEW, no duplicar. S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción: revisar jobs/logs y alcance literal de IN-I-04, y resultados de mutación pendientes; no declarar cierre sin evidencia.

---

# r548 — IN-I-03 PASS_SCOPED funcional; iniciar IN-I-04

IN-I-03: Lite parser/motor y Plus servicio/HTTP (incluido literal fuente); E2E visual dedicado no acreditado. Lite SHA 63793b3a5ee263653835527462c4395172dc8b48: acumulativo 43710610622 (2582 passed, 8 expected fail, 34 TODO), H1d 43710610635 (22), Scientific 43710610666 (456). Plus SHA f9222b115fb2ed8bba46245cc7d8d3ecdea52b84: acumulativo 43725643080/backend 132846861090 (3082 passed, 1 skipped, 11 xfailed; literal y controles PASS), frontend 132846860774 (1055 passed, 28 TODO); H1d 43725643065 (38), Native 43725643032 (26 desktop, 52 tablet/móvil). Jobs y logs revisados. Seguridad 43725643047/job 132846991188 y mutación previa 43715315873/job 132815595041 siguen en curso; frontend omitido no es PASS. S19 REVIEW, S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción única: IN-I-04 arctan(2x)>=π/4, solución [1/2,∞); test-first bilateral y controles, sin duplicar gates de seguridad.

---

# r547 — Canal HTTP literal IN-I-03 corregido; gates pendientes

Plus SHA técnico f9222b115fb2ed8bba46245cc7d8d3ecdea52b84: la forma fuente `\\arctan x<1` se normaliza con reconocimiento acotado y sigue pasando validaciones de seguridad. Test-first: el canal HTTP fallaba con PARSE_ERROR; ahora pruebas de literal y entradas malformadas pasan junto a parser/seguridad: 273 pruebas locales. No implica E2E visual. Push acumulativo 43725643080, H1d 43725643065, Native 43725643032, CI 43725643052 y seguridad 43725643047 en cola al registrar. Mutación previa 43715315873/job 132815595041 sigue en curso; se conserva y la corrida nueva tiene código distinto. S19 REVIEW, S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción: revisar jobs/logs del SHA técnico y comparar reporte de mutación previa 43715315873 con 43684691979; no duplicar corridas ni cerrar sin evidencia.

---

# r546 — Gates funcionales revisados; canal literal IN-I-03 pendiente

Plus SHA ecfc786d8caf30aad82e83828902eaf10b029505: acumulativo 43715315872/backend 132815467936 (3078 passed, 1 skipped, 11 xfailed) y frontend 132815467653 (1055 passed, 28 TODO), H1d 43715315847 (38): pasos y logs revisados. Seguridad 43715315873: backend seguridad pasó, frontend omitido; mutación backend 132815595041 aún en curso, informe no disponible; WAIT sin duplicar. S19 permanece REVIEW.

Diagnóstico independiente local en SHA ecfc786: POST /api/v1/inequality con literal fuente `\\arctan x<1` devuelve success=false, PARSE_ERROR; `atan(x)<1` devuelve el intervalo correcto. La prueba cubre el canal HTTP directo, no demuestra la interfaz visual. IN-I-03 queda funcionalmente aprobado solo para formas normalizadas; el canal literal permanece pendiente. No se declara cierre completo. S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción: esperar y revisar reporte de mutación 43715315873; después corregir y verificar el canal HTTP literal IN-I-03, sin duplicar gates en curso.

---

# r545 — S19: pruebas dirigidas publicadas; mutación pendiente

Plus SHA técnico ecfc786d8caf30aad82e83828902eaf10b029505. Se añadieron pruebas en el archivo ya incluido en la selección de mutación: agregados finitos, índices/límites inválidos, normalización matemática y rechazo de ecuaciones fuera de solve. Selección existente completa: 456 pruebas locales aprobadas. No se cambian el harness, los mutantes ni umbrales; el impacto en el score aún no está verificado. Push acumulativo 43715315872, H1d 43715315847, seguridad/mutación 43715315873 y CI 43715315835 estaban en curso o cola. Mantener S19 REVIEW; no contar jobs omitidos como PASS. IN-I-03: funcional Lite acumulativo 43710610622 (2582 passed, 8 expected fail, 34 TODO), H1d 43710610635 (22), scientific 43710610666 (456); Plus acumulativo 43710615660/backend 132801135773 (3066 passed, 1 skipped, 11 xfailed) y frontend (1055 passed, 28 TODO), H1d 43710615637 (38). Falta reconciliar formalmente alcance literal y el nuevo SHA de Plus. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED.

Siguiente acción única: revisar el reporte y los gates del SHA técnico, comparar sobrevivientes y timeouts con 43684691979, mantener REVIEW mientras falte aceptación y reconciliar la evidencia funcional de IN-I-03.

---

# r544 — IN-D-08: reconciliación de mutación con la corrida 43691200778

Plus SHA verificado: 5f10389c4ec0217d1007aa22b5219c34ba91f0b9. Corrida 43691200778 (push); job plus-backend-mutmut 132742142853 completado con éxito a las 10:09 UTC; artefacto s19-plus-backend-mutmut 14157018061, digest SHA-256 b2cb0c1b27154bf309636dd3440cb94fefce0ccccdcf3c7e41eb741cd5ee17ee.

Verificación: mutmut-results.txt, mutmut-survived.txt, mutmut-timeout.txt y mutmut-exit-code.txt son idénticos byte a byte a los de la corrida 43684691979 (5.836 mutantes; 2.498 eliminados, 42,80 %; 3.312 sobrevivientes; 12 timeout; 14 sin pruebas). El cambio entre a2bb123f y 5f10389c (phase2_service.py y pruebas de IN-D-08) no toca los siete módulos mutados del workflow, así que el resultado idéntico es coherente. El backend sigue sin umbral de score.

Reconciliación: r535 (IN-D-08 PASS_SCOPED bilateral) citó la corrida 43691200778 mientras seguía en curso. Su componente de mutación no estaba verificado entonces, y la frase «jobs, pasos y logs revisados» no cubría ese job. Se corrige: el componente de mutación backend de IN-D-08 queda REVIEW, con la misma evidencia que r543. Los gates funcionales citados en r535 no cambian; frontend-audit y stryker de esa corrida están omitidos, no son PASS.

Decisión: IN-D-08 no se cierra. Sus componentes funcionales siguen PASS_SCOPED; la mutación backend queda REVIEW. El cierre requiere resolver ese REVIEW o aceptarlo explícitamente con justificación. S19 backend sigue REVIEW. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED. Lite no se modificó.

Siguiente acción: decidir entre pruebas dirigidas para las seis brechas de r543 o aceptación explícita con justificación; luego evaluar los 13 avisos de auditoría frontend.

---

# r543 — Mutación backend 43684691979 registrada como REVIEW

Plus SHA de la corrida de seguridad: a2bb123f2babfc8c4e8df725f3b00806af606061 (job plus-backend-mutmut 132722665975, artefacto s19-plus-backend-mutmut 14153208898). Estado: REVIEW, no PASS. El job terminó con código 0, pero el backend no tiene umbral de score, así que ese código no acredita calidad de mutación.

Totales leídos del log del job: 5.836 mutantes; 2.498 eliminados (42,80 %); 3.312 sobrevivientes; 14 sin pruebas; 12 timeout. Línea base estable (qa/s19/BASELINE_MUTATION.md): 1.028 mutantes, 590 eliminados (57,39 %). El score bajó 14,6 puntos. Otros componentes de la corrida: pip-audit sin vulnerabilidades; Bandit sin hallazgos de severidad alta; pruebas de seguridad aprobadas; auditoría frontend con 13 avisos (11 moderados, 2 bajos), pendientes de evaluación según la política.

Causas identificadas:
1. Crecimiento del código fuera del harness. Desde 7568020 solve_service suma +1.841 líneas, parsing +293, evaluate +238 y ast_validator +43. 2.389 sobrevivientes están en 30 funciones de solve_service añadidas después de la línea base; evaluate (92) y parsing (23) también tienen sobrevivientes en funciones nuevas.
2. El harness no cambió en lo que mide: mismos cinco módulos (only_mutate), mismos cuatro archivos de prueba seleccionados, mutmut 3.8.0. Los cambios del workflow son ceilings de timeout y clasificación de alcance. Los archivos seleccionados crecieron (test_solve 9→78, test_parsing 21→41, test_evaluate 25→51 pruebas), pero ninguno contiene pruebas de hiperbólicas; esas viven en otros archivos fuera de la selección.
3. Sin caída en código estable. Funciones sin cambio AST desde la línea base mantienen sus sobrevivientes: _quadratic_steps 74→74, _linear_steps 31→31, _to_equation_solution 6→6, validate_ast_safety 3→3, _expand_sqrt_tokens 39→37; parse_inequality_tree baja de 52 a 1.
4. Brechas reales en funciones modificadas: solve_equation 25→244; normalize_unicode 7→104; parse_expression_tree 11→52; check_complexity_limits 15→66; _parse_side 9→29; _try_parse_finite_aggregate 83→98.

Decisión: REVIEW. No se acepta el score degradado ni se cierra S19 backend. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED sin cambios. La entrada r535 (IN-D-08 PASS_SCOPED) citó la corrida 43691200778 como en curso; no verifiqué su resultado en esta revisión, y su componente de mutación debe reconciliarse con este REVIEW antes de cualquier cierre.

Siguiente acción: evaluar los 13 avisos de auditoría frontend según la política y decidir cómo tratar las seis brechas de la causa 4 (pruebas dirigidas, sin cambiar umbrales ni mutantes). Ampliar la selección de pruebas de mutmut cambia el harness y requiere autorización explícita.

---

# r542 — IN-I-03 publicado; verificación CI pendiente

Lite SHA 63793b3a5ee263653835527462c4395172dc8b48; Plus SHA 4575c8f13578cd9b45216e1c0567669b6d747df5. Test-first: Lite no resolvía arctan(x)<1; se implementó x<tan(1), frontera estricta en radianes y fallback preservado. Plus ya resolvía el caso y recibió tests de fuente, servicio y HTTP. Local: Lite 79 pruebas y build aprobados; Plus 58 pruebas aprobadas. Push Lite acumulativo 43710610622, H1d 43710610635, Scientific 43710610666, CI 43710610689; Plus acumulativo 43710615660, H1d 43710615637, CI 43710615647: en curso al registrar. Seguridad 43695734343 terminó por runner shutdown sin reporte final; no repetir bloqueo idéntico. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED.

Siguiente acción: revisar jobs/logs y alcance literal del SHA técnico antes de cerrar IN-I-03.

---

# r541 — IN-I-02 PASS_SCOPED; iniciar IN-I-03

IN-I-02 aprobado en alcance parser/motor Lite y servicio/HTTP Plus; no acredita E2E dedicado de la fila. Lite SHA 92ee3a2d47ff6219e5550d171ee5747cbd96161a: acumulativo 43705873823/job 132786702663 (2576 passed, 8 expected fail, 34 TODO; focal 6), H1d 43705873862 (22), Scientific 43705873864 (456). Plus SHA b141e34275bb1f965cfabeda4ea7e978b636853f: acumulativo 43705883021/backend 132786731076 (3062 passed, 1 skipped, 11 xfailed) y frontend 132786730866 (1055 passed, 28 TODO), H1d 43705883049 (38). Jobs y logs revisados; omisiones no son PASS. Seguridad 43695734343/job 132755851381: runner shutdown 2026-11-15T11:21:05Z, sin informe final; perfiles frontend omitidos. S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción única: IN-I-03 arctan(x)<1, solución (-∞,tan(1)); test-first bilateral, frontera estricta y regresiones.

---

# r540 — IN-I-02 publicado; verificación CI pendiente

Lite SHA 92ee3a2d47ff6219e5550d171ee5747cbd96161a; Plus SHA b141e34275bb1f965cfabeda4ea7e978b636853f. Test-first: Lite no resolvía arccos(x)<=π/3; se implementó [1/2,1] respetando dominio real y fallback. Plus ya resolvía el caso y recibió tests de fuente, servicio y HTTP. Local: Lite 73 pruebas y build aprobados; Plus 54 pruebas aprobadas. Push Lite acumulativo 43705873823, H1d 43705873862, Scientific 43705873864, CI 43705873839; Plus acumulativo 43705883021, H1d 43705883049, CI 43705883014: en curso o cola al registrar. Seguridad dinámica pendiente; no duplicar gates. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED.

Siguiente acción: revisar jobs/logs y alcance literal del SHA técnico antes de cerrar IN-I-02.

---

# r539 — IN-I-01 PASS_SCOPED; iniciar IN-I-02

IN-I-01 aprobado en alcance parser/motor Lite y servicio/HTTP Plus; no acredita E2E dedicado de la fila. Lite SHA f5c56e21abcd71e2d893aa87e06d8975d4bb3a6f: acumulativo 43701096046/job 132772192776 (2570 passed, 8 expected fail, 34 TODO), H1d 43701096051 (22), Scientific 43701096048 (456). Plus SHA dca31e3d87e26c8505d5a7ca639a6c1072ad4ba3: acumulativo 43701103600/backend 132772216342 (3058 passed, 1 skipped, 11 xfailed) y frontend 132772216124 (1055 passed, 28 TODO), H1d 43701103574 (38). Jobs y logs revisados; omisiones no son PASS. Seguridad Plus 43695734343/backend mutmut 132755851381 en curso; frontend omitido. S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción única: IN-I-02 arccos(x)<=π/3, solución [1/2,1]; test-first bilateral, dominio y extremos, reverso y regresiones.

---

# r538 — IN-I-01 publicado; verificación CI pendiente

Lite SHA f5c56e21abcd71e2d893aa87e06d8975d4bb3a6f; Plus SHA dca31e3d87e26c8505d5a7ca639a6c1072ad4ba3. Test-first: Lite no resolvía arcsin(x)>π/6; se implementó (1/2,1] respetando dominio real y fallback. Plus ya resolvía el caso y recibió tests de fuente, servicio y HTTP. Local: Lite 67 pruebas y build aprobados; Plus 50 pruebas aprobadas. Push Lite acumulativo 43701096046, H1d 43701096051, Scientific 43701096048, CI 43701096049; Plus acumulativo 43701103600, H1d 43701103574, CI 43701103568: en curso al registrar. Seguridad dinámica pendiente de revisión; no duplicar gates. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED.

Siguiente acción: revisar jobs/logs y alcance literal del SHA técnico antes de cerrar IN-I-01.

---

# r537 — IN-D-09 PASS_SCOPED; iniciar IN-I-01

IN-D-09 aprobado en alcance parser/motor periódico Lite y servicio/HTTP Plus con advertencia de período; no acredita entrada literal del dominio ni E2E dedicado de la fila. Lite SHA 8c2045339735d39eccd710f186fe53b366a99931: acumulativo 43695728687/job 132755703577 (2564 passed, 8 expected fail, 34 TODO; focal 6), H1d 43695728658 (22), Scientific 43695728670 (456). Plus SHA 831197d61a845fd737022b1037e7bbf5acd2cc12: acumulativo 43695734403/backend 132755721185 (3054 passed, 1 skipped, 11 xfailed), frontend 132755720847 (1055 passed, 28 TODO); H1d 43695734378 (38), Native 43695734357 (26 desktop, 52 tablet/móvil). Pasos y logs revisados; omisiones no son PASS. Seguridad Plus 43695734343/backend mutmut 132755851381 en curso; frontend omitido. S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN.

Siguiente acción única: IN-I-01 arcsin(x)>π/6, solución (1/2,1]; test-first bilateral, dominio y extremos, reverso y regresiones.

---

# r536 — IN-D-09 publicado; verificación CI pendiente

Lite SHA 8c2045339735d39eccd710f186fe53b366a99931; Plus SHA 831197d61a845fd737022b1037e7bbf5acd2cc12. Test-first: Lite no resolvía csc(x)<-2 y Plus no advertía su período. Se implementó la solución (π,7π/6) ∪ (11π/6,2π), extremos abiertos, con periodicidad explícita y regresiones de fallback. Local: Lite 61 pruebas trigonométricas y build aprobados; Plus 46 pruebas aprobadas. Push Lite acumulativo 43695728687, H1d 43695728658, Scientific 43695728670, CI 43695728663; Plus acumulativo 43695734403, H1d 43695734378, Native 43695734357, CI 43695734385, seguridad 43695734343: pendientes de revisar. No duplicar. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED.

Siguiente acción: revisar jobs y logs de los SHA técnicos y diagnosticar fallos; validar alcance literal y paridad antes de cerrar IN-D-09.

---

# r535 — IN-D-08 PASS_SCOPED; iniciar IN-D-09

IN-D-08 aprobado en alcance: parser/motor periódico Lite y servicio/HTTP Plus con advertencia de rama principal; la ingesta literal completa del dominio y un E2E dedicado de la fila no están acreditados. Lite SHA 75558880204e15cfd23a1a1dacdcefe5e558de4f: acumulativo 43681790954 (2558 passed, 8 expected fail, 34 TODO), H1d 43681790797 (22), Scientific 43681790844 (456). Plus SHA 5f10389c4ec0217d1007aa22b5219c34ba91f0b9: acumulativo 43691200764/backend 132742038460 (3049 passed, 1 skipped, 11 xfailed) y frontend 132742038378 (1055 passed, 28 TODO); H1d 43691200749 (38), Native 43691200755 (26 desktop, 52 tablet/móvil). Jobs, pasos y logs revisados; omisiones no son PASS. Seguridad 43691200778/backend mutmut 132742142853 en curso; perfiles frontend omitidos. Global OPEN; S25, SG28/DIST y EV-D-01 BLOCKED.

Siguiente acción única: IN-D-09 csc(x)<-2 en [0,2π), solución (π,7π/6) ∪ (11π/6,2π); test-first bilateral, polos y extremos abiertos, conservar fallback; verificar gates sin duplicar.

---

# r534 — IN-D-08: advertencia de período publicada; gates en curso

Plus SHA técnico 5f10389c4ec0217d1007aa22b5219c34ba91f0b9: la solución principal de cot(x)>=1 se identifica como restringida a (0,π), con período π. Test-first: dos fallos por advertencia ausente; corrección y 41 pruebas locales trigonométricas aprobadas. Push CI 43691200754, acumulativo 43691200764, H1d 43691200749, Native 43691200755 y seguridad 43691200778, en cola o curso al registrar. No duplicar; revisar pasos y logs antes de aceptar. Seguridad previa 43684691979 también seguía en curso. Lite conserva evidencia r533. Global OPEN; S25, SG28/DIST, EV-D-01 BLOCKED.

Siguiente acción: revisar corridas del SHA técnico, reconciliar resultados y verificar alcance literal y paridad antes de cerrar IN-D-08.

---

# r533 — Reconciliación IN-D-08; revisión pendiente

El índice registra el SHA técnico a2bb123f2babfc8c4e8df725f3b00806af606061 y huellas de los gates ejecutados; solo CURRENT_STATE.md difiere entre ese commit técnico y el HEAD anterior. La corrida Plus de seguridad 43684691979 continúa en curso; sus perfiles no se declaran globalmente aprobados. S25, SG28/DIST y EV-D-01 permanecen BLOCKED; certificación global OPEN. Siguiente acción: revisar alcance literal y paridad IN-D-08 y finalizar evaluación de seguridad sin duplicar corridas.

---

# r532 — IN-D-08: evidencia acumulativa revisada; reconciliación pendiente

HEAD técnico Lite 75558880204e15cfd23a1a1dacdcefe5e558de4f; Plus a2bb123f2babfc8c4e8df725f3b00806af606061. IN-D-08: cot(x)>=1, x∈(0,π), resultado (0,π/4]. Lite acumulativo 43681790954/job 132713777141: 2558 passed, 8 expected fail, 34 TODO; focal 10. H1d 43681790797: 22 passed; científico 43681790844: 456 passed. Plus acumulativo 43681802532/backend 132713812218: 3049 passed, 1 skipped, 11 xfailed; frontend 132713812291: 1055 passed, 28 TODO. H1d 43681802533: 38 passed. Pasos y logs revisados; omisiones no son PASS. Global OPEN; S25, SG28/DIST y EV-D-01 permanecen BLOCKED.

Siguiente acción: reconciliar continuity.json y verificar todos los gates y el alcance literal de IN-D-08 antes de declarar cierre; no repetir corridas equivalentes. El índice r531 aún no refleja los SHA técnicos.


---

# r531 — IN-D-07 PASS_SCOPED bilateral; siguiente IN-D-08

Global OPEN. IN-D-07: sec(x)>2 en (-π/2,π/2), solución (-π/2,-π/3) ∪ (π/3,π/2). Alcance: parser/motor Lite periódico y servicio/HTTP Plus normalizado con aviso de rama principal; no ingesta literal completa del dominio ni E2E dedicado de la fila.

Evidencia ejecutada: Lite SHA d043c6b792490a504dd097496aa4c10eccda25ec; CI 43664661117, Cumulative 43664661133/job 132661261373 (2548 passed, 8 expected fail, 34 TODO; focal 6/6), H1d 43664661082/job 132661261195 (22/22), Scientific 43664661126/job 132661261425 (456/456). Plus SHA 308a40821b500478a317f2e2aa1c234d8fae402e; CI 43664684498 (3043 passed, 1 skipped, 11 xfailed), Cumulative 43664684548/backend 132661336785 (3043 passed, 1 skipped, 11 xfailed; focal 6/6) y frontend 132661337055 (1055 passed, 28 TODO), H1d 43664684521/job 132661336789 (38/38), Native 43664684545/job 132661336931 (26 desktop y 52 tablet/móvil). Guards consultados skip=false y SHA técnico; TODO/SKIP/XFAIL no son PASS.

Comparación Git de cada HEAD con su SHA técnico: solo CURRENT_STATE.md, EXECUTION_LOG.md y continuity.json cambiaron, exclusiones exactas de huella; se reutiliza evidencia ejecutada sin nueva corrida. Seguridad Plus 43664684565/job 132661426597 está en curso; perfiles frontend omitidos no son PASS. S25, SG28/DIST y EV-D-01 permanecen BLOCKED.

## Siguiente acción única
IN-D-08: `cot x≥1`, x∈(0,π), solución (0,π/4]. Congelar las tres celdas originales; test-first bilateral en parser/motor y servicio/HTTP; probar polo excluido 0, igualdad incluida π/4, extremo de dominio π excluido, signos y controles. Corregir solo brechas demostradas; publicar con expected_sha y verificar gates push. No avanzar a IN-D-09.

