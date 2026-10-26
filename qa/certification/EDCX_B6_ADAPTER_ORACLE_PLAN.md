# EDCX-B6 — plan de adaptador y oráculo independiente (r274)

Estado: diseño estático, NO EJECUTADO; no acepta filas ni certifica B6.

## Evidencia del código
- POST /api/v1/evaluate recibe expression (1–500 caracteres), angle_unit (rad/deg; por defecto rad) y substitutions opcional.
- El parser declara pi, e/E e i/I; admite exp, Log y ln. Log es logaritmo complejo principal; ln es natural y log es base 10 por defecto.
- MathResponse expone result_text y result_latex. result_approx es opcional y solo se asigna para resultados reales. No usarlo para aceptar estos resultados complejos.

## Entradas candidatas y oráculo
Estas expresiones son propuestas estáticas; confirmar el parser y la salida con una prueba dirigida antes de convertirlas en aserciones:
- VC-FE-01: exp(i*pi/2); esperado independiente: cmath.exp(1j*math.pi/2).
- VC-FE-02: exp(-i*pi/4); esperado: cmath.exp(-1j*math.pi/4).
- VC-FE-03: exp(ln(2)+i*pi/3); esperado: cmath.exp(math.log(2)+1j*math.pi/3).
- VC-FE-06: Log(i); esperado: cmath.log(1j).
- VC-FE-07: Log(1+i); esperado: cmath.log(1+1j).
- VC-FE-08: Log(-1-i); esperado: cmath.log(-1-1j).
- VC-FE-09: Log(3-3*i); esperado: cmath.log(3-3j).
- VC-FE-10: Log(-e); esperado: cmath.log(complex(-math.e, 0)).

## Criterio de prueba propuesto
1. Calcular los esperados con math/cmath de la biblioteca estándar, no con la salida del producto.
2. Decodificar result_text o result_latex con un adaptador explícito y restringido. Si no se puede decodificar sin ambigüedad, dejar REVIEW; no aprobar por inspección visual.
3. Comparar real e imaginaria por separado, inicialmente con rel_tol=1e-9 y abs_tol=1e-9. Son tolerancias propuestas, no confirmadas por la matriz.
4. Exigir success=true y ausencia de error_code; comprobar valor principal para Log.
5. Probar el adaptador con salidas reales antes de añadir aserciones finales.

## Exclusiones y CI
- VC-FE-04 requiere identidad simbólica y supuestos; queda fuera de este lote.
- La cobertura previa de VC-FE-05 sigue siendo parcial.
- VC-FE-11 requiere contrato multivaluado y sigue bloqueada.
- No cambiar producto ni JSONL. No despachar workflows hasta tener tests concretos y reconciliar eventos push y pull_request por SHA.
- B6 REVIEW; B5 BLOCKED en Plus; Lite NO_EJECUTADO; certificación global OPEN. Mantener SG28/DIST, S25 y capacidades no implementadas en sus estados actuales.
