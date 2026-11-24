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
| IT-D-01 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-02 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-03 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-04 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-05 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-06 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-07 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-08 | FAIL | Plus: prueba numérica local servicio XFAIL estricto por rama logarítmica real; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-09 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-10 | FAIL | Plus: prueba numérica local servicio XFAIL estricto por rama logarítmica real; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-11 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-12 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-13 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-14 | FAIL | Plus: prueba numérica local servicio XFAIL estricto por rama logarítmica real; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-15 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-16 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-17 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-D-18 | EN_CURSO | Plus: prueba numérica local servicio PASS parcial en cuatro puntos; SHA `1d1fefef05d5f590db97d472b838393543356057`; CI, canal literal, Lite y aceptación integral pendientes. |
| IT-I-01 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-02 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-03 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-04 | REVIEW | Plus: XFAIL diferencia de rama; revisar contrato; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-05 | BLOCKED | Plus: XFAIL integral no resuelta; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-06 | BLOCKED | Plus: XFAIL integral no resuelta; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-07 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-08 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-09 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-10 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-I-11 | EN_CURSO | Plus: PASS local numérico parcial; prueba `backend/tests/test_trig_it_d_batch_audit.py`, SHA `4d5b586920fd8886613d2fcb68314457fd138760`; CI, Lite, entrada literal y HTTP pendientes. |
| IT-H-01 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-02 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-03 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-04 | REVIEW | Plus: XFAIL rama real requiere revisión; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-05 | EN_CURSO | Plus: primitiva implementada, prueba numérica local y polo de csch² comprobado; SHA `aa448cf689082cde391f548ec823c776f37616a7`; CI, Lite y canales pendientes. |
| IT-H-06 | EN_CURSO | Plus: primitiva implementada, prueba numérica local y polo de csch² comprobado; SHA `aa448cf689082cde391f548ec823c776f37616a7`; CI, Lite y canales pendientes. |
| IT-H-07 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-08 | REVIEW | Plus: XFAIL rama real requiere revisión; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-09 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-10 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-11 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-12 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-13 | REVIEW | Plus: XFAIL rama real requiere revisión; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-14 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-15 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-H-16 | EN_CURSO | Plus: PASS local numérico parcial; SHA `60bc9c506f374f15cead746b9034b04d39633e60`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-HI-01 | EN_CURSO | Plus: PASS parcial local en puntos interiores; SHA `56524b2c5b48c592c9f4b41c13474f99e46c2575`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-HI-02 | EN_CURSO | Plus: extremo x=1 probado localmente; SHA `83a393597da753e1a3119e2a95d1cc265bd94e86`; CI, Lite, canales y dominio completo pendientes. |
| IT-HI-03 | EN_CURSO | Plus: PASS parcial local en puntos interiores; SHA `56524b2c5b48c592c9f4b41c13474f99e46c2575`; CI, Lite, fuente literal y HTTP pendientes. |
| IT-HI-04 | REVIEW | Plus: XFAIL rama real negativa; SHA `56524b2c5b48c592c9f4b41c13474f99e46c2575`; CI, Lite, fuente literal y HTTP pendientes. |
