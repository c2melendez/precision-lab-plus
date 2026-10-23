# EDCX-B6 — borrador de contrato por fila (r268)

**Estado: REVIEW / NO EJECUTAR.** Este archivo es una hoja de trabajo de contrato; no certifica soporte ni constituye una aceptación de endpoint. Derivado literalmente de las 53 filas `VC-FE-01..53` de `edcx_ejecutables.jsonl`. El campo `canal` se deja intacto y vacío, tal como está en la fuente.

## Reglas comunes

- Ruta técnica candidata para casos escalares compatibles: `POST /api/v1/evaluate`; todavía no confirmada por fila. Verificar schema/payload real y respuesta en código vigente antes de implementar.
- Nunca usar la salida del producto como oráculo. Calcular expected independientemente (SymPy u otro cálculo independiente), con convención de rama explícita y tolerancia derivada de la precisión de la fuente.
- Mantener separada la semántica del campo de matriz `canal` (transformación entre representaciones) del endpoint técnico del harness.
- `Log` denota logaritmo complejo principal en el teclado; `log` sin base es decimal en el producto; `ln` es natural. No reescribir notación sin un adaptador documentado.
- Las identidades simbólicas requieren supuestos (por ejemplo variables reales) o sustituciones de prueba declaradas. No pasar una identidad simbólica como prueba numérica sin fijar el contrato.
- Los casos multivaluados, de rama/corte y de singularidad no pueden recibir PASS por coincidir solo con una raíz principal o por devolver cualquier error.

## Inventario de 53 filas

| ID | Expresión de fuente | Esperado de fuente | Clase preliminar | Contrato pendiente antes del harness |
|---|---|---|---|---|
| VC-FE-01 | `e^{i\pi/2}` | `i` | EXPONENTIAL_COMPLEX_SCALAR | candidate /evaluate; verify numeric complex serialization; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-02 | `e^{-i\pi/4}` | `\frac{\sqrt{2}}{2}(1-i)` | EXPONENTIAL_COMPLEX_SCALAR | candidate /evaluate; verify numeric complex serialization; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-03 | `e^{\ln2+i\pi/3}` | `1+i\sqrt{3}` | EXPONENTIAL_COMPLEX_SCALAR | candidate /evaluate; verify numeric complex serialization; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-04 | `\lvert e^{z}\rvert`, `z=x+iy` | `e^{x}` | SYMBOLIC_IDENTITY_REAL_ASSUMPTIONS | requires x,y real; not a plain numeric test; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-05 | `\operatorname{Log}(-1)` | `i\pi` | PRINCIPAL_COMPLEX_LOG | verify Log adapter, branch and exact complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-06 | `\operatorname{Log}(i)` | `\frac{i\pi}{2}` | PRINCIPAL_COMPLEX_LOG | verify Log adapter, branch and exact complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-07 | `\operatorname{Log}(1+i)` | `\frac{1}{2}\ln2+\frac{i\pi}{4}` | PRINCIPAL_COMPLEX_LOG | verify Log adapter, branch and exact complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-08 | `\operatorname{Log}(-1-i)` | `\frac{1}{2}\ln2-\frac{3\pi i}{4}` | PRINCIPAL_COMPLEX_LOG | verify Log adapter, branch and exact complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-09 | `\operatorname{Log}(3-3i)` | `\frac{1}{2}\ln18-\frac{i\pi}{4}\approx1.445186-0.785398i` | PRINCIPAL_COMPLEX_LOG | verify Log adapter, branch and exact complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-10 | `\operatorname{Log}(-e)` | `1+i\pi` | PRINCIPAL_COMPLEX_LOG | verify Log adapter, branch and exact complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-11 | ``\log(1)` (multivaluado)` | `2\pi ik` | MULTIVALUED_LOG | single principal result insufficient; explicit set contract required; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-12 | `\operatorname{Log}((-1)(-1))` frente a `\operatorname{Log}(-1)+\operatorname{Log}(-1)` | ``0` frente a `2\pi i` (no es aditivo)` | PRINCIPAL_LOG_NONADDITIVITY | two evaluations; compare Log(ab) against Log(a)+Log(b); especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-13 | `\operatorname{Log}\left(e^{3\pi i}\right)` | ``i\pi` (no `3\pi i`)` | PRINCIPAL_LOG_EXP | branch wrapping required; expected iπ, not 3πi; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-14 | `\operatorname{Log}(0)` | `indefinido (error claro)` | DOMAIN_ERROR | must define observable controlled error for Log(0); especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-15 | ``i^{i}` (valor principal)` | `e^{-\pi/2}\approx0.207879576`; todos los valores `e^{-\pi/2-2\pi k}` | COMPLEX_POWER_PRINCIPAL_AND_MULTIVALUED | principal candidate plus separate all-values contract; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-16 | `(-1)^{i}` | `e^{-\pi}\approx0.043213918` | COMPLEX_POWER_PRINCIPAL | verify principal branch and numerical complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-17 | `2^{i}` | `\cos(\ln2)+i\sin(\ln2)\approx0.769239+0.638961i` | COMPLEX_POWER_PRINCIPAL | verify principal branch and numerical complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-18 | `(1+i)^{i}` | `e^{-\pi/4}\left(\cos\frac{\ln2}{2}+i\sin\frac{\ln2}{2}\right)\approx0.4288+0.1549i` | COMPLEX_POWER_PRINCIPAL | verify principal branch and numerical complex output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-19 | ``(-1)^{1/3}` (valor principal)` | `\frac{1}{2}+\frac{\sqrt{3}}{2}i` | COMPLEX_FRACTIONAL_POWER_PRINCIPAL | verify branch convention for (-1)^(1/3); especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-20 | `\sqrt{z^{2}}` en `z=-i` | ``i` (no `-i`)` | PRINCIPAL_SQUARE_ROOT_IDENTITIES | separate paired expressions; branch-sensitive comparisons; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-21 | `\sqrt{-1}\cdot\sqrt{-1}` frente a `\sqrt{(-1)(-1)}` | `-1` frente a `1` | PRINCIPAL_SQUARE_ROOT_IDENTITIES | separate paired expressions; branch-sensitive comparisons; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-22 | `\sqrt{\frac{1}{z}}` frente a `\frac{1}{\sqrt{z}}` en `z=-1` | `i` frente a `-i` | PRINCIPAL_SQUARE_ROOT_IDENTITIES | separate paired expressions; branch-sensitive comparisons; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-23 | `\sin(i)` | `i\sinh1\approx1.175201194i` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-24 | `\cos(i)` | `\cosh1\approx1.543080635` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-25 | `\tan(i)` | `i\tanh1\approx0.761594156i` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-26 | `\cot(i)` | `-i\coth1\approx-1.313035285i` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-27 | `\sin(1+i)` | `\sin1\cosh1+i\cos1\sinh1\approx1.298457581+0.634963915i` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-28 | `\cos(1+i)` | `\cos1\cosh1-i\sin1\sinh1\approx0.833730025-0.988897706i` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-29 | `\sin\left(\frac{\pi}{2}+i\right)` | `\cosh1` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-30 | `\cos(\pi+i)` | `-\cosh1` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-31 | `\sin(2i)` | `i\sinh2\approx3.626860408i` | COMPLEX_TRIG_SCALAR | verify complex input parsing and numeric output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-32 | `\left\lvert\sin(x+iy)\right\rvert^{2}` | `\sin^{2}x+\sinh^{2}y` | SYMBOLIC_COMPLEX_TRIG_IDENTITY | needs symbolic equality or declared substitutions; not numeric-only; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-33 | `\left\lvert\cos(x+iy)\right\rvert^{2}` | `\cos^{2}x+\sinh^{2}y` | SYMBOLIC_COMPLEX_TRIG_IDENTITY | needs symbolic equality or declared substitutions; not numeric-only; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-34 | `\frac{e^{iz}+e^{-iz}}{2}` | `\cos z` | SYMBOLIC_COMPLEX_TRIG_IDENTITY | needs symbolic equality or declared substitutions; not numeric-only; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-35 | `\frac{e^{iz}-e^{-iz}}{2i}` | `\sin z` | SYMBOLIC_COMPLEX_TRIG_IDENTITY | needs symbolic equality or declared substitutions; not numeric-only; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-36 | `\sin^{2}z+\cos^{2}z` | `1` | SYMBOLIC_COMPLEX_TRIG_IDENTITY | needs symbolic equality or declared substitutions; not numeric-only; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-37 | `\sinh(i\pi)` y `\cosh(i\pi)` | `0` y `-1` | COMPLEX_HYPERBOLIC_SCALAR | verify imaginary arguments and branch-aware output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-38 | `\sinh\left(\frac{i\pi}{2}\right)` | `i` | COMPLEX_HYPERBOLIC_SCALAR | verify imaginary arguments and branch-aware output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-39 | `\tanh\left(\frac{i\pi}{4}\right)` | `i` | COMPLEX_HYPERBOLIC_SCALAR | verify imaginary arguments and branch-aware output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-40 | `\cosh(1+i\pi)` | `-\cosh1` | COMPLEX_HYPERBOLIC_SCALAR | verify imaginary arguments and branch-aware output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-41 | `\sinh\left(1+\frac{i\pi}{2}\right)` | `i\cosh1` | COMPLEX_HYPERBOLIC_SCALAR | verify imaginary arguments and branch-aware output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-42 | `-i\ln\left(iz+\sqrt{1-z^{2}}\right)` en `z=\frac{1}{2}` | `\frac{\pi}{6}` | INVERSE_SINE_FORMULA_REAL_POINT | adapter for formula and explicit substitution z=1/2; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-43 | `\arcsin(i)` | `i\ln\left(1+\sqrt{2}\right)\approx0.881373587i` | INVERSE_COMPLEX_TRIG_PRINCIPAL | verify principal branch convention and output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-44 | `\arccos(i)` | `\frac{\pi}{2}-i\ln\left(1+\sqrt{2}\right)` | INVERSE_COMPLEX_TRIG_PRINCIPAL | verify principal branch convention and output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-45 | `\arcsin(2)` | ``\frac{\pi}{2}\mp i\ln\left(2+\sqrt{3}\right)` (el signo depende de la convención sobre el corte; debe declararse)` | INVERSE_COMPLEX_TRIG_PRINCIPAL | verify principal branch convention and output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-46 | `\arctan(1+i)` | `\frac{1}{2}(\pi-\arctan2)+\frac{i}{4}\ln5\approx1.017222+0.402359i` | INVERSE_COMPLEX_TRIG_PRINCIPAL | verify principal branch convention and output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-47 | `\frac{1}{2i}\ln\frac{1+iz}{1-iz}` en `z=1` | `\frac{\pi}{4}` | INVERSE_COMPLEX_TRIG_PRINCIPAL | verify principal branch convention and output; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-48 | `\arctan(i)` | `indefinido (singularidad)` | SINGULARITY_ERROR | define expected controlled error at arctan(i); especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-49 | `\arctan(2i)` | ``\frac{\pi}{2}+\frac{i}{2}\ln3` (convención estándar; debe declararse)` | INVERSE_COMPLEX_TRIG_BRANCH | declare convention for arctan(2i); especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-50 | `\operatorname{arsinh}(i)` | `\frac{i\pi}{2}` | INVERSE_HYPERBOLIC_PRINCIPAL | verify naming aliases and principal branch; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-51 | `\operatorname{arcosh}(0)` | `\frac{i\pi}{2}` | INVERSE_HYPERBOLIC_PRINCIPAL | verify naming aliases and principal branch; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-52 | `\operatorname{arcosh}(-1)` | `i\pi` | INVERSE_HYPERBOLIC_PRINCIPAL | verify naming aliases and principal branch; especificar adaptación, oracle, aceptación y tolerancia. |
| VC-FE-53 | `\operatorname{artanh}(2)` | ``\frac{1}{2}\ln3\pm\frac{i\pi}{2}` (debe declararse la convención)` | INVERSE_HYPERBOLIC_BRANCH | declare convention for artanh(2), including sign on cut; especificar adaptación, oracle, aceptación y tolerancia. |

## Criterio de salida de REVIEW

Por cada fila, registrar explícitamente: (1) entrada API y payload confirmados desde el código; (2) notación/alias sin ambigüedad; (3) clase de resultado (exacto, aproximado, conjunto multivaluado, identidad simbólica o error); (4) rama/corte y supuestos; (5) oráculo independiente reproducible; (6) tolerancia, si aplica, basada en redondeo de la fuente; (7) condición de aceptación y evidencia que se guardará. Si un caso no está implementado, marcar BLOCKED por capacidad, no FAIL ni PASS. Si no hay contrato verificable, mantener REVIEW.

## Estado

No se modificó producto ni JSONL. No se ejecutaron pruebas ni se despachó CI. Lite continúa `NO_EJECUTADO`; B5 sigue `BLOCKED` en Plus; certificación global `OPEN`.
