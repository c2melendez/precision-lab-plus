# IN625 H2 — extracto de la fuente primaria (seguridad y límites)

Este extracto preserva los vectores normativos EN-SG-01..32 de la sección H.2 de la matriz completa de 625 filas. Se publica como insumo contractual versionado para que la certificación no dependa de una copia externa o del contexto de una sesión.

**Procedencia:** archivo \`legacy_sources/matriz_entrada_sintaxis_calculadora(2).md\` dentro de \`Precision_Lab_Certification_HANDOFF_ACTIVE_v0_3_CONTINUED_14_2026-10-07_CORRECTED.zip\`, recuperado de la biblioteca el 2026-10-26.
**SHA-256 del archivo completo recuperado:** \`58fbc0ed04aef158148981fc28074d470e45ec07a67604f89b3847b55c625528\`.
**Fuente completa:** la copia recuperada contiene 625 filas en 26 secciones. Este archivo es un extracto fiel de la sección H.2, no una sustitución de la matriz completa.

Nada de estos casos debe ejecutar código, abrir archivos, insertar HTML, bloquear la interfaz ni dejar el servidor sin responder. Los cálculos potencialmente costosos deben probarse solo en CI aislado, nunca contra producción.

| ID | Nivel | Entrada literal o generador | Resultado esperado |
|---|---|---|---|
| EN-SG-01 | N1 | <script>alert(1)</script> | Entrada inválida; error escapado; no se ejecuta |
| EN-SG-02 | N1 | <img src=x onerror=alert(1)> | Igual |
| EN-SG-03 | N2 | x^{2}\text{<b>hola</b>} | Texto literal, sin negrita ni etiquetas |
| EN-SG-04 | N2 | \href{javascript:alert(1)}{x} | Sin enlace ejecutable; error claro o texto plano |
| EN-SG-05 | N2 | \url{http://example.com}, \includegraphics{x.png}, \htmlClass{a}{x}, \htmlStyle{color:red}{x} | Bloqueados con error claro |
| EN-SG-06 | N2 | \def\a{\a}\a | Recursión cortada con error claro; el navegador no se congela |
| EN-SG-07 | N2 | \newcommand{\a}{\a}\a, \let\a\b, \catcode | Bloqueados con error claro |
| EN-SG-08 | N2 | \input{/etc/passwd}, \include{x}, \write18{ls}, \openin1=x | No soportados; no se lee ningún archivo; error claro |
| EN-SG-09 | N3 | __import__('os').system('ls') | Rechazado sin evaluar; nunca texto crudo a sympify/eval |
| EN-SG-10 | N3 | open('/etc/passwd').read() | Rechazado sin evaluar |
| EN-SG-11 | N3 | ().__class__.__bases__[0].__subclasses__() | Rechazado sin evaluar |
| EN-SG-12 | N3 | (lambda x: x)(1) | Rechazado sin evaluar |
| EN-SG-13 | N3 | exec("print(1)") y eval("1+1") | Rechazados sin evaluar |
| EN-SG-14 | N3 | import os y os.system("ls") | Rechazados sin evaluar |
| EN-SG-15 | N3 | x.__class__ y x.__dict__ | Rechazados |
| EN-SG-16 | N3 | Symbol('x'), Integer(2), Function('f') | Rechazados o tratados como texto |
| EN-SG-17 | N2 | a=7 y luego a+1 | La asignación no persiste entre cálculos |
| EN-SG-18 | N3 | clearall, draw, run, last, lambda, S, N | Variables o error claro; nunca órdenes del motor |
| EN-SG-19 | N2 | Generar "(" * 50 + "1" + ")" * 50 | Resultado 1 |
| EN-SG-20 | N3 | Generar "(" * 1000 + "1" + ")" * 1000 | Error claro de profundidad, sin RangeError/RecursionError/500 |
| EN-SG-21 | N3 | Generar "+".join(["1"] * 10000) | 10000 en tiempo razonable (< 2 s) |
| EN-SG-22 | N3 | Generar "x+" * 50000 + "x" (aprox. 100 000 caracteres) | Procesa sin congelar la interfaz, o rechazo claro por longitud |
| EN-SG-23 | N3 | 10^{10^{10}} | Simbólico o error claro de tamaño; nunca bloqueo |
| EN-SG-24 | N3 | 9^{9^{9}} | Igual |
| EN-SG-25 | N3 | 1000000! | Límite o timeout con mensaje claro y posibilidad de cancelar |
| EN-SG-26 | N3 | Expandir (x+1)^{10000} | Límite o timeout con mensaje claro |
| EN-SG-27 | N3 | 2^{2^{2^{2^{2}}}} | 2^{65536} (19 729 dígitos) o límite claro |
| EN-SG-28 | N3 | Botón Detener durante un cálculo largo | UI responde, cálculo se cancela y el siguiente cálculo funciona |
| EN-SG-29 | N3 | 20 evaluaciones seguidas o pegar mientras calcula | Resultado visible corresponde a la última entrada |
| EN-SG-30 | N3 | Comillas dobles/simples, barra inversa, NUL (U+0000), CR/LF | API recibe JSON válido, sin 400/500 |
| EN-SG-31 | N3 | Cuerpo de 5 MB | Rechazo limpio (413) |
| EN-SG-32 | N3 | Ráfaga de solicitudes (si hay límite de frecuencia) | Mensaje claro; no se pierde la entrada |

## Generadores normativos de las entradas largas

~~~python
print("(" * 50 + "1" + ")" * 50)          # EN-SG-19
print("(" * 1000 + "1" + ")" * 1000)      # EN-SG-20
print("+".join(["1"] * 10000))             # EN-SG-21
print("x+" * 50000 + "x")                  # EN-SG-22
~~~

**Regla de aceptación:** un test de rechazo controlado puede demostrar que el sistema falla de forma segura, pero no convierte automáticamente en PASS un criterio que exige calcular y mostrar un resultado. EN-SG-21 se mantiene bloqueado contractualmente mientras se resuelve la incompatibilidad entre 10 000 términos y el límite actual de 500 caracteres por expresión. EN-SG-32 solo aplica si existe una política de limitación de frecuencia configurada.
