# TR324 — lote 80-01: inventario inicial

Fuente congelada `qa/certification/legacy_sources/ejercicios_trigonometria.md.gz`; SHA-256 descomprimido `8d3904fd1c53f8af694caf66171b99caf821ca5d94dfbef8677d73b7a76054f7`. Snapshot del producto `b0a809798bcceccab221cde1ad29f1a4cc605b8f`. Los estados se refieren únicamente a este producto. La selección consta de 80 IDs consecutivos a partir de DV-I-04. REVIEW significa evidencia histórica aún no reconciliada; no presume ausencia de cobertura ni PASS. PASS_SCOPED no acredita UI específica ni cierre global.

> Acumulativo 45201649129 SUCCESS: backend job 137786433124, 3439 aprobadas, 1 omitida y 11 xfail; frontend job 137786432680 SUCCESS. DV-H-01..12 y DV-HI-01..10 con pruebas de servicio y HTTP; faltan extremos, dominio, paridad Lite y UI; no son cierres completos.

> Lite: DV-HI-01..10 bloqueados por derivadas inversas sin resolver; la protección del commit 649c068 evita reportar un resultado falso. Paridad bilateral pendiente.

> Lite: implementación para DV-HI-01..10 publicada en 7cbbed39; pruebas locales en puntos interiores, CI en curso y paridad completa pendiente.

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
| IT-D-01 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-02 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-03 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-04 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-05 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-06 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-07 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-08 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-09 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-10 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-11 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-12 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-13 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-14 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-15 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-16 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-17 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-D-18 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-01 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-02 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-03 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-04 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-05 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-06 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-07 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-08 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-09 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-10 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-I-11 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-01 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-02 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-03 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-04 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-05 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-06 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-07 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-08 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-09 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-10 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-11 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-12 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-13 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-14 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-15 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-H-16 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-HI-01 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-HI-02 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-HI-03 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
| IT-HI-04 | REVIEW | Reconciliar prueba, oráculo, canal y evidencia en GitHub. |
