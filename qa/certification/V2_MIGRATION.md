# Adopción v2.0 — checkpoint de implementación

Cambio técnico publicado: 45bd3fb24233f17dba16ee5382f125e03352a89b. Rama canónica: qa/syntax-audit-in625-a1. Producto: plus.

Se incorpora SYSTEM_V2.md, batch_v2.py, test_batch_v2.py y workflow certification-batch-v2. El piloto MV153 reutiliza las nueve suites existentes; verifica las nueve fuentes, 153 IDs y genera observaciones JUnit/JSON sin declarar PASS. No se han alterado motores, fixtures, oráculos ni gates históricos. No se ha reconciliado el inventario completo ni cerrado matrices. La certificación global permanece OPEN. No modificar los estados técnicos anteriores por este checkpoint documental.

Siguiente acción: verificar los runs push del SHA técnico y jobs/logs/artefactos; aceptar únicamente alcance demostrado, corregir mapeos faltantes. En paralelo continuar reparación de regresiones activas Lite y deuda compleja TR324. Ampliar el ejecutor a TR324 y demás matrices por familias. Mantener S25, SG28/DIST y EV-D-01 abiertos hasta condiciones de salida. No repetir gate en curso ni cambiar los filtros CI sin demostrar equivalencia.

## Piloto ejecutado — evidencia de infraestructura

SHA técnico corregido: 3294b348b7bfd7b3338a1e18f72241cd78c89996. [Run 45765169933](https://github.com/c2melendez/precision-lab-plus/actions/runs/45765169933), job 139724255183, SUCCESS; logs revisados. Dos pruebas del guard aprobadas, nueve fuentes verificadas y fixture de 153 IDs. JSON/JUnit: 148 REVIEW_TEST_OK, 5 REVIEW_NO_MAPPED_TEST, 0 PASS de certificación asignados por el piloto. No inferir que un ID no mapeado carezca de toda evidencia histórica. Gates acumulativos/CI siguen sujetos a verificación del SHA correspondiente; no cerrar matriz ni bloqueos. Siguiente: resolver mapeos y extender a TR324, preservando revisión independiente, regresiones activas y condiciones de salida.

## TR324 — reconciliación de observaciones y reparación real (2026-11-27 UTC)

Lite SHA aa89238d114f42f12b648ca420c8c29f253cf5c6, run 45920446553/job 140249641103: 135 REVIEW_TEST_OK, 119 REVIEW_CONTEXT_ONLY, 70 sin mapeo. Plus SHA f78fc86d3c9baa4c736ed3db0e6eb6d31be2e3c7, run 45920455889/job 140249671215: 155 REVIEW_TEST_OK, 70 REVIEW_CONTEXT_ONLY, 13 REVIEW_SKIPPED, 86 sin mapeo; 685 tests passed, 25 xfailed. Todos los estados son observaciones, no cierre. En este cambio se reparan las primitivas reales IT-D-08/10/14 e IT-H-04/08/13, se mantienen los oráculos numéricos existentes de servicio y HTTP y se añaden pruebas de variable y ramas. Pendiente CI del nuevo SHA; no declarar PASS ni paridad compleja. EV-D-01, S25 y SG28/DIST siguen bloqueados.
