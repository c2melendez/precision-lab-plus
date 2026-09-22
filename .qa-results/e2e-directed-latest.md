# QA directed E2E diagnostic — Plus

- exit_code: 0

~~~text
[1A[2K[WebServer] INFO:     Started server process [3336]

[1A[2K[WebServer] INFO:     Waiting for application startup.
[WebServer] INFO:     Application startup complete.

[1A[2K[WebServer] INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Running 48 tests using 2 workers

[1A[2K[1/48] [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[2/48] [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[3/48] [desktop-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[4/48] [desktop-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[5/48] [desktop-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[6/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[7/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[8/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[9/48] [desktop-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[10/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[11/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[12/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[13/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[14/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[15/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[16/48] [desktop-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[17/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[18/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[19/48] [tablet-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[20/48] [tablet-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[21/48] [tablet-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[22/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[23/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[24/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[25/48] [tablet-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[26/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[27/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[28/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[29/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[30/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[31/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[32/48] [tablet-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K[33/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:20:1 › suite original módulo 3: inventario de Cálculo refleja capacidades actuales
[1A[2K[34/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:43:1 › suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI
[1A[2K[35/48] [mobile-chromium] › e2e/exhaustive-module03-calculus.spec.ts:55:1 › suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI
[1A[2K[36/48] [mobile-chromium] › e2e/exhaustive-module09-graphing.spec.ts:12:1 › suite original módulo 9: modos gráficos están activos y 2D renderiza
[1A[2K[37/48] [mobile-chromium] › e2e/exhaustive-module09-graphing.spec.ts:25:1 › suite original módulo 9: múltiples curvas 2D se renderizan juntas
[1A[2K[38/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:15:1 › módulo 10: la tecla % calcula porcentaje real (50% = 0.5)
[1A[2K[39/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:30:1 › módulo 10: ±(5) produce dos ramas matemáticas distintas
[1A[2K[40/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:46:1 › módulo 10: Productoria Π ya no aparece como pendiente
[1A[2K[41/48] [mobile-chromium] › e2e/exhaustive-module10-keyboard.spec.ts:55:1 › módulo 10: acciones no aritméticas de Álgebra exponen tooltip
[1A[2K[42/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:21:1 › M12: preferencias visuales se aplican y persisten tras recarga
[1A[2K[43/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:79:1 › M12: tema Automático sigue prefers-color-scheme
[1A[2K[44/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:91:1 › M12: Ajustes expone estado y cierra con Escape
[1A[2K[45/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:100:1 › M12: teclado propio tiene diálogo nombrado y cierra con Escape
[1A[2K[46/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:110:1 › M12: campo matemático principal tiene nombre accesible
[1A[2K[47/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:118:1 › M12: resultado calculado queda dentro de una región anunciable
[1A[2K[48/48] [mobile-chromium] › e2e/exhaustive-module12-personalization-a11y.spec.ts:145:1 › M12: vibración y sonido guardan preferencia y sobreviven recarga
[1A[2K  48 passed (54.6s)
~~~
