# TR324 — lote 80-01: inventario inicial

Fuente congelada `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`; SHA-256 descomprimido `8d3904fd1c53f8af694caf66171b99caf821ca5d94dfbef8677d73b7a76054f7`. Snapshot del producto `b0a809798bcceccab221cde1ad29f1a4cc605b8f`. Los estados se refieren únicamente a este producto. La selección consta de 80 IDs consecutivos a partir de DV-I-04. REVIEW significa evidencia histórica aún no reconciliada; no presume ausencia de cobertura ni PASS. PASS_SCOPED no acredita UI específica ni cierre global.

> Acumulativo 45201649129 SUCCESS: backend job 137786433124, 3439 aprobadas, 1 omitida y 11 xfail; frontend job 137786432680 SUCCESS. DV-H-01..12 y DV-HI-01..10 con pruebas de servicio y HTTP; faltan extremos, dominio, paridad Lite y UI; no son cierres completos.

> Lite: DV-HI-01..10 bloqueados por derivadas inversas sin resolver; la protección del commit 649c068 evita reportar un resultado falso. Paridad bilateral pendiente.

> Lite: implementación para DV-HI-01..10 publicada en 7cbbed39; pruebas locales en puntos interiores, CI en curso y paridad completa pendiente.

> Lite: pruebas locales para DV-H-01..12 publicadas en fa355ca; CI y paridad completa pendientes.

> Lite: CI acumulativo 45217595942 revisado y aprobado para DV-H-01..12 en el alcance probado; paridad integral, dominio y UI pendientes.

> Lite: anclaje de entrada y resultados DV-H-01..12 verificado por CI 45228151225; dominios, canales y paridad completa pendientes.

| ID | Estado | Evidencia y alcance / pendiente |
|---|---|---|
| DV-I-04 | PASS_SCOPED | `backend/tests/test_trigonometry_dv_i04_i06.py`; acumulativo [45185775213](https://github.com/c2melendez/precision-lab-plus/actions/runs/45185775213); SHA `b0a809798bcceccab221cde1ad29f1a4cc605b8f`; UI específica pendiente. |
| DV-I-05 | PASS_SCOPED | `backend/tests/test_trigonometry_dv_i04_i06.py`; acumulativo [45185775213](https://github.com/c2melendez/precision-lab-plus/actions/runs/45185775213); SHA `b0a809798bcceccab221cde1ad29f1a4cc605b8f`; UI específica pendiente. |
| DV-I-06 | PASS_SCOPED | `backend/tests/test_trigonometry_dv_i04_i06.py`; acumulativo [45185775213](https://github.com/c2melendez/precision-lab-plus/actions/runs/45185775213); SHA `b0a809798bcceccab221cde1ad29f1a4cc605b8f`; UI específica pendiente. |
| DV-I-07 | EN_CURSO | Servicio y API aprobados en CI anterior; paridad Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-I-08 | EN_CURSO | Servicio y API aprobados en CI anterior; paridad Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-I-09 | EN_CURSO | Servicio y API aprobados en CI anterior; paridad Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-I-10 | EN_CURSO | Servicio y API aprobados en CI anterior; paridad Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-I-11 | EN_CURSO | Servicio y API aprobados en CI anterior; paridad Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-I-12 | EN_CURSO | Servicio y API aprobados en CI anterior; paridad Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-01 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-02 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-03 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-04 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-05 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-06 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-07 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-08 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-09 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-10 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-11 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-H-12 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-01 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-02 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-03 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-04 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-05 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-06 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-07 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-08 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-09 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| DV-HI-10 | EN_CURSO | Servicio y HTTP 44/44 locales para el conjunto de 22 casos; CI en curso; Lite pendiente; SHA `ac143bfb6d748517ae29160059a42307dd427a1c`, [run 45201649129](https://github.com/c2melendez/precision-lab-plus/actions/runs/45201649129). |
| IT-D-01 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-02 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-03 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-04 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-05 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-06 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-07 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-08 | FAIL | Plus: prueba numérica local servicio XFAIL estricto por rama logarítmica real; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-09 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-10 | FAIL | Plus: prueba numérica local servicio XFAIL estricto por rama logarítmica real; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-11 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-12 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-13 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-14 | FAIL | Plus: prueba numérica local servicio XFAIL estricto por rama logarítmica real; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-15 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-16 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-17 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-D-18 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-01 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-02 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-03 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-04 | REVIEW | Plus: XFAIL diferencia de rama; revisar contrato; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-05 | BLOCKED | Plus: XFAIL integral no resuelta; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-06 | BLOCKED | Plus: XFAIL integral no resuelta; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-07 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-08 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-09 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-10 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-I-11 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-01 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-02 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-03 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-04 | REVIEW | Plus: XFAIL rama real requiere revisión; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-05 | EN_CURSO | Plus: integrales definidas probadas en intervalos interiores, SHA `f80f16325c290753185d491a5b1bda1262c2cea8`, CI pendiente; cruce de polo, Lite y canales pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-06 | EN_CURSO | Plus: integrales definidas probadas en intervalos interiores, SHA `f80f16325c290753185d491a5b1bda1262c2cea8`, CI pendiente; cruce de polo, Lite y canales pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-07 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-08 | REVIEW | Plus: XFAIL rama real requiere revisión; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-09 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-10 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-11 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-12 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-13 | REVIEW | Plus: XFAIL rama real requiere revisión; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-14 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-15 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-H-16 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-HI-01 | EN_CURSO | Plus: PASS parcial local en puntos interiores; SHA `56524b2c5b48c592c9f4b41c13474f99e46c2575`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-HI-02 | EN_CURSO | Plus: extremo x=1 probado localmente; SHA `83a393597da753e1a3119e2a95d1cc265bd94e86`; CI, Lite, canales y dominio completo pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-HI-03 | EN_CURSO | Plus: PASS parcial local en puntos interiores; SHA `56524b2c5b48c592c9f4b41c13474f99e46c2575`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |
| IT-HI-04 | REVIEW | Plus: XFAIL rama real negativa; SHA `56524b2c5b48c592c9f4b41c13474f99e46c2575`; CI, Lite, fuente literal y HTTP pendientes. HTTP parcial local: SHA `5c1471e343b86372120edf3e486a809b0a84ee09`; CI pendiente. |

## Reconciliación CI por caso — 2026-11-24

Resultados de pruebas existentes; no constituyen PASS contractual. La información siguiente actualiza las menciones históricas de CI pendiente; no modifica ni borra el historial. Fuente y hash arriba. Falta verificar entrada literal, dominios completos y otros canales.

Plus `5c1471e343b86372120edf3e486a809b0a84ee09`, [acumulativo 45455272441](https://github.com/c2melendez/precision-lab-plus/actions/runs/45455272441), job backend 138662901260; `backend/tests/test_trig_it_d_batch_audit.py`, HTTP y derivación numérica en puntos interiores; no acredita entrada literal ni dominio completo.

| Caso | Resultado acotado ejecutado |
|---|---|
| IT-D-01 | PASS parcial |
| IT-D-02 | PASS parcial |
| IT-D-03 | PASS parcial |
| IT-D-04 | PASS parcial |
| IT-D-05 | PASS parcial |
| IT-D-06 | PASS parcial |
| IT-D-07 | PASS parcial |
| IT-D-08 | XFAIL |
| IT-D-09 | PASS parcial |
| IT-D-10 | XFAIL |
| IT-D-11 | PASS parcial |
| IT-D-12 | PASS parcial |
| IT-D-13 | PASS parcial |
| IT-D-14 | XFAIL |
| IT-D-15 | PASS parcial |
| IT-D-16 | PASS parcial |
| IT-D-17 | PASS parcial |
| IT-D-18 | PASS parcial |
| IT-H-01 | PASS parcial |
| IT-H-02 | PASS parcial |
| IT-H-03 | PASS parcial |
| IT-H-04 | XFAIL |
| IT-H-05 | PASS parcial |
| IT-H-06 | PASS parcial |
| IT-H-07 | PASS parcial |
| IT-H-08 | XFAIL |
| IT-H-09 | PASS parcial |
| IT-H-10 | PASS parcial |
| IT-H-11 | PASS parcial |
| IT-H-12 | PASS parcial |
| IT-H-13 | XFAIL |
| IT-H-14 | PASS parcial |
| IT-H-15 | PASS parcial |
| IT-H-16 | PASS parcial |
| IT-I-01 | PASS parcial |
| IT-I-02 | PASS parcial |
| IT-I-03 | PASS parcial |
| IT-I-04 | XFAIL |
| IT-I-05 | XFAIL |
| IT-I-06 | XFAIL |
| IT-I-07 | PASS parcial |
| IT-I-08 | PASS parcial |
| IT-I-09 | PASS parcial |
| IT-I-10 | PASS parcial |
| IT-I-11 | PASS parcial |
| IT-HI-01 | PASS parcial |
| IT-HI-02 | PASS parcial |
| IT-HI-03 | PASS parcial |
| IT-HI-04 | XFAIL |

XFAIL permanece FAIL o pendiente de resolución; PASS parcial no es cierre. S25, SG28/DIST y EV-D-01 permanecen abiertos.

## TR324 IT-H: implementación Lite en verificación

SHA Lite `f2caf06a985770703493e9cdb6d07438ac63feb5`; [acumulativo 45522841583](https://github.com/c2melendez/precision-lab-lite/actions/runs/45522841583) en curso. Cada resultado listado es local y acotado a las formas de `tests/trigonometryItHBatch.audit.test.ts` y puntos interiores; falta CI, canal literal, dominios y UI. No es PASS contractual.

| Caso | Estado Lite local |
|---|---|
| IT-H-01 | Resultado parcial: derivada en puntos interiores |
| IT-H-02 | Resultado parcial: derivada en puntos interiores |
| IT-H-03 | Resultado parcial: derivada en puntos interiores |
| IT-H-04 | XFAIL: integral sin resolver |
| IT-H-05 | Resultado parcial: derivada en puntos interiores |
| IT-H-06 | Resultado parcial: derivada en puntos interiores |
| IT-H-07 | Resultado parcial: derivada en puntos interiores |
| IT-H-08 | XFAIL: integral sin resolver |
| IT-H-09 | Resultado parcial: derivada en puntos interiores |
| IT-H-10 | Resultado parcial: derivada en puntos interiores |
| IT-H-11 | Resultado parcial: derivada en puntos interiores |
| IT-H-12 | Resultado parcial: derivada en puntos interiores |
| IT-H-13 | Resultado parcial: derivada en puntos interiores |
| IT-H-14 | Resultado parcial: derivada en puntos interiores |
| IT-H-15 | Resultado parcial: derivada en puntos interiores |
| IT-H-16 | Resultado parcial: derivada en puntos interiores |

## IT-H-06 y IT-H-10 — dominio Lite en verificación

El SHA `c4bedba0b8ee6bcf73ea37ed552884f2b94cc1a1` incorpora `tests/trigonometryItHDefiniteDomain.audit.test.ts`: rechaza intervalos que incluyen el polo en cero y verifica intervalos positivos en x/y. Evidencia local y [CI en curso 45530232061](https://github.com/c2melendez/precision-lab-lite/actions/runs/45530232061). Ambas filas siguen EN_CURSO: formas equivalentes, demás dominios, canal literal y UI pendientes; no es PASS contractual.

## TR324 IT-I-01..11 — auditoría Lite

SHA Lite `b94a96b56ec0746fcd8d7b7335ce07359a6ffa19`; prueba `tests/trigonometryItIBatch.audit.test.ts`, [acumulativo 45537278744](https://github.com/c2melendez/precision-lab-lite/actions/runs/45537278744) en curso. Resultados locales en puntos interiores, anclaje de ID, no entrada literal; no son PASS contractual.

| Caso | Resultado local Lite |
|---|---|
| IT-I-01 | Resultado parcial: derivada numérica interior |
| IT-I-02 | Resultado parcial: derivada numérica interior |
| IT-I-03 | Resultado parcial: derivada numérica interior |
| IT-I-04 | Resultado parcial: derivada numérica interior |
| IT-I-05 | XFAIL: integral sin resolver |
| IT-I-06 | XFAIL: integral sin resolver |
| IT-I-07 | Resultado parcial: derivada numérica interior |
| IT-I-08 | Resultado parcial: derivada numérica interior |
| IT-I-09 | Resultado parcial: derivada numérica interior |
| IT-I-10 | Resultado parcial: derivada numérica interior |
| IT-I-11 | XFAIL: derivada sin resolver |

## TR324 IT-HI: auditoría Lite en verificación

SHA `17f66fcb7f6f61d58c35e93095de408cf537f80e`; `tests/trigonometryItHIBatch.audit.test.ts`; [CI 45543566207](https://github.com/c2melendez/precision-lab-lite/actions/runs/45543566207) en curso. La verificación de error es guarda, no cálculo aprobado; 07–09 solo prueban puntos interiores. IDs 05–10 fuera del lote original.

| Caso | Resultado local Lite |
|---|---|
| IT-HI-01 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |
| IT-HI-02 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |
| IT-HI-03 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |
| IT-HI-04 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |
| IT-HI-05 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |
| IT-HI-06 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |
| IT-HI-07 | Resultado parcial interior |
| IT-HI-08 | Resultado parcial interior |
| IT-HI-09 | Resultado parcial interior |
| IT-HI-10 | BLOCKED: integral no implementada; UNSUPPORTED_OPERATION |

## TR324 IT-HI-01/10: estabilidad de asinh en Plus y paridad con Lite

SHA técnico Plus `f3ac7f29efb6907d51e2c16fdd083fafbc145020`: fija la estabilidad de primitivas de `asinh(x)` y `x*asinh(x)` frente a cancelaciones en argumentos grandes (`±1e6` y `±1e8`) en `test_trig_it_d_batch_audit.py`. [Acumulativo 45731223450](https://github.com/c2melendez/precision-lab-plus/actions/runs/45731223450) completó SUCCESS (backend job 139613416223: 3580 passed, 1 skipped, 35 xfailed, 1 warning; frontend job 139613416651: SUCCESS). Lite emparejó estabilidad y resolvió ramas complejas en `8b130c1ed3abc2935dbf4d910649c006b0d1c445` (CI acumulativo 45737280683 SUCCESS: 3056 PASS). Ambas implementaciones conservan PASS_SCOPED. S25, SG28/DIST y EV-D-01 permanecen BLOCKED; certificación global OPEN.

## TR324 IT-HI-01/03/10: Lite en verificación

Las tres filas tienen primitivas para formas específicas en `94e8ac22e7608ee79ba6ad0d4bfdc93496b1c320`, comprobadas localmente con derivada y diferencias finitas en puntos interiores; [CI 45550227135](https://github.com/c2melendez/precision-lab-lite/actions/runs/45550227135) en curso. IT-HI-10 es adicional al lote. No son PASS contractual: faltan ramas, dominios, literalidad y UI.

## IT-HI-02 y estabilidad de IT-HI-01 — Lite

IT-HI-02: primitiva de acosh en `39b1cd185716b4f4e50eda0c99447d25340b3bd5`, resultado interior local; [CI 45557928390](https://github.com/c2melendez/precision-lab-lite/actions/runs/45557928390) en curso. IT-HI-01: evaluación numérica de la primitiva en x=-100000000 produce Infinity.0 por cancelación; FAIL de estabilidad y corrección pendiente. No son cierres contractuales.

## IT-HI-01/10: estabilidad de primitivas Lite

SHA `721cad1b3935fc14289c5675cedad26c33eb32b2`: regresión local para x=+1e8 aprobada y x=-1e8 XFAIL por Infinity.0 en ambas primitivas; [CI 45565408211](https://github.com/c2melendez/precision-lab-lite/actions/runs/45565408211) en curso. IT-HI-10 es extra al lote original. Ambas filas sin cierre; pendiente corrección que preserve ramas y dominios.

## IT-D-08/14: dominios definidos Lite en verificación

SHA `0000dbfcb0006e26d198f979fd2ee393bba41f1e`, `tests/trigonometryItDDefinitePoles.audit.test.ts`: 12 pruebas locales cubren polos periódicos, intervalos seguros y literales; [CI 45572462518](https://github.com/c2melendez/precision-lab-lite/actions/runs/45572462518) en curso. Guarda limitada a formas específicas; paridad, UI y dominios generales pendientes. No es cierre contractual.

## IT-D-08/14: respuestas no finitas Plus

SHA Plus `c2d66e7124ce7f2bbc652009e610293f30044ab4`: pruebas HTTP locales de cot y sec³ que retornaban nan/oo ahora devuelven DOMAIN_ERROR; intervalos finitos conservan success. [CI 45582006410](https://github.com/c2melendez/precision-lab-plus/actions/runs/45582006410) completó SUCCESS (backend job 139094132064: 3554 passed, 1 skipped, 35 xfailed; frontend job 139094131945: 1055 passed, 28 todo). Quedan pendientes singularidades que produzcan resultados finitos, formas equivalentes y canales completos; no hay PASS contractual.


## Reconciliación de evidencia HTTP Plus del lote original (25-11-2026)

Se cotejaron los 80 IDs originales con el log del job backend [139094132064](https://github.com/c2melendez/precision-lab-plus/actions/runs/45582006410/job/139094132064), corrida 45582006410 exitosa sobre SHA técnico `c2d66e7124ce7f2bbc652009e610293f30044ab4`. Resultado por prueba HTTP: 70 PASSED y 10 XFAIL. La tabla refleja el resultado de esa prueba, no la certificación integral del caso: no acredita por sí sola dominio completo, entrada literal de matriz, UI, oráculo independiente ni paridad Lite. XFAIL conserva el bloqueo y no es PASS. No se ejecutó una corrida nueva para esta reconciliación. Las seis filas IT-HI-05..10 agregadas fuera de los 80 originales se excluyen del cómputo. Las filas y evidencias anteriores conservan su alcance histórico.

| ID | Resultado HTTP en CI | Prueba parametrizada |
|---|---|---|
| DV-I-04 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i04_i06.py::test_http_derivative_endpoint` |
| DV-I-05 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i04_i06.py::test_http_derivative_endpoint` |
| DV-I-06 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i04_i06.py::test_http_derivative_endpoint` |
| DV-I-07 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i07_i12.py::test_http_derivative_endpoint` |
| DV-I-08 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i07_i12.py::test_http_derivative_endpoint` |
| DV-I-09 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i07_i12.py::test_http_derivative_endpoint` |
| DV-I-10 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i07_i12.py::test_http_derivative_endpoint` |
| DV-I-11 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i07_i12.py::test_http_derivative_endpoint` |
| DV-I-12 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_i07_i12.py::test_http_derivative_endpoint` |
| DV-H-01 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-02 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-03 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-04 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-05 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-06 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-07 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-08 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-09 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-10 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-11 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-H-12 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-01 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-02 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-03 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-04 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-05 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-06 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-07 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-08 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-09 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| DV-HI-10 | PASSED (parcial) | `backend/tests/test_trigonometry_dv_h_hi_batch.py::test_http` |
| IT-D-01 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-02 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-03 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-04 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-05 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-06 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-07 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-08 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-09 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-10 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-11 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-12 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-13 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-14 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-15 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-16 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-17 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-D-18 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-I-01 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-02 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-03 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-04 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-05 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-06 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-07 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-08 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-09 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-10 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-I-11 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-H-01 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-02 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-03 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-04 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-05 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-06 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-07 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-08 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-09 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-10 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-11 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-12 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-13 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-14 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-15 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-H-16 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_integral_http_numeric` |
| IT-HI-01 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-HI-02 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-HI-03 | PASSED (parcial) | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
| IT-HI-04 | XFAIL | `backend/tests/test_trig_it_d_batch_audit.py::test_inverse_integral_http_numeric` |
