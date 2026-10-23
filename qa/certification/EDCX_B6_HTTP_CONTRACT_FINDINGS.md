# EDCX-B6 — hallazgos del contrato HTTP y del motor (r270)

Estado: REVIEW; esta revisión es estática del código fuente en la rama, no ejecución de casos B6 ni confirmación empírica del comportamiento en runtime.

## Contrato HTTP confirmado en fuente

- Router: `backend/app/routers/evaluate.py`, registrado en `backend/app/main.py` con prefijo `/api/v1`. La ruta es `POST /api/v1/evaluate`.
- Payload Pydantic `EvaluateRequest` en `backend/app/schemas/requests.py`: `expression` obligatoria de 1 a 500 caracteres; `angle_unit` es `rad` o `deg` y por defecto `rad`; `substitutions` opcional es un diccionario de strings.
- Respuesta `MathResponse` en `backend/app/schemas/responses.py`: `success`, `result_text`, `result_latex`, `result_approx: Optional[float]`, `result_data`, `error_code` y `error_message`, entre otros campos.
- Importante: `evaluate_service.evaluate` solo asigna `approx_value` cuando `numeric_value.is_real`. Para resultados complejos no debe esperarse un número complejo serializado en `result_approx`; el contrato candidato debe comparar la representación exacta/canónica en `result_text` o `result_latex`, además de evaluar numéricamente un parseo independiente cuando corresponda. No aceptar por coincidencia de texto únicamente si el caso requiere comparación numérica.
- El router traduce `DomainErrorResult`, `ZeroDivisionError`, `ValueError`, `AttributeError` y otros errores de dominio a `DOMAIN_ERROR` en rutas previstas. La salida concreta de `Log(0)` aún debe verificarse con test de contrato; el código fuente por sí solo no es resultado de ejecución.
- La suite `backend/tests/test_evaluate.py` existente cubre muchas funciones escalares, pero en el tramo revisado no se encontraron pruebas dedicadas que certifiquen las 53 filas B6, el conjunto multivaluado de B6-11 o todas las convenciones de rama.

## Semántica de notación observada

- `ALLOWED_FUNCTIONS` en `backend/app/services/parsing.py` registra `Log` como `_complex_log` (logaritmo complejo principal), `log` como logaritmo de base 10 cuando solo tiene un argumento y `ln` como logaritmo natural.
- El contrato B6 debe traducir explícitamente `\operatorname{Log}` a la tecla/función `Log` sin alterar la capitalización, y `\ln` a `ln`. No traducir `\log` multivaluado a la función de calculadora `log` sin base, porque el producto le asigna semántica decimal.
- El caso B6-11 (`\log(1)`, todos los valores `2πik)) no queda cubierto por la salida de una función de logaritmo principal. Con el contrato actual de `/evaluate` (resultado escalar), debe marcarse como brecha de capacidad o definirse un adaptador/representación de conjunto separado. No aprobarlo con un solo valor principal.
- Las identidades con variables libres se pueden devolver simbólicamente, pero el contrato debe precisar supuestos y comparar expresiones equivalentes; el `result_approx` puede ser `null`.

## Clasificación operativa revisada

1. **Candidatos razonables para prueba HTTP escalar en Plus:** B6-01..03, 05..10, 13, 16..19, 23..31, 37..41, 43..47, 50..52, sujeto a validar traducción de entrada, forma de salida y ramas.
2. **Requieren contrato específico antes de aceptar:** B6-04 y 32..36 (identidades/supuestos simbólicos); B6-11 y el componente multivaluado de B6-15 (conjunto de valores); B6-12 (dos resultados y comparación); B6-14 y 48 (error de dominio concreto); B6-20..22 (comparaciones emparejadas sensibles a rama); B6-42 (expresión compuesta y sustitución); B6-45, 49 y 53 (convención de rama/corte).
3. Esta clasificación no declara PASS ni FAIL. Cualquier caso no soportado por la interfaz escalar debe quedar BLOCKED por capacidad con evidencia, no forzarse a un endpoint incompatible.

## Próximo paso seguro

Crear tests de contrato aislados y no-dispatch para los primeros candidatos escalares con oráculo independiente. Antes de hacerlo, validar con la suite local existente el payload/response y el parseo de literales complejos (`i`, `e`, `π`, exponentes y argumentos), y confirmar el mapeo de salida. Añadir casos multivaluados/branch como tests negativos de capacidad solo cuando sus criterios estén escritos. No modificar código de producto ni ejecutar gates globales en esta fase de revisión.

## Límites de evidencia

No se ejecutó código ni test en este paso. Los hallazgos son lectura estática de archivos en `qa/syntax-audit-in625-a1`; requieren pruebas locales antes de convertirse en afirmaciones de comportamiento observado. Lite sigue `NO_EJECUTADO`; B5 `BLOCKED` en Plus; certificación global `OPEN`.
