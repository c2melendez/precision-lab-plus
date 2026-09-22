# QA fast CI diagnostic — Plus

- npm_ci: 0
- typecheck: 0
- unit: 1
- build: 0

## npm-ci
~~~text
npm warn deprecated inflight@1.0.6: This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.
npm warn deprecated @humanwhocodes/config-array@0.13.0: Use @eslint/config-array instead
npm warn deprecated rimraf@3.0.2: Rimraf versions prior to v4 are no longer supported
npm warn deprecated whatwg-encoding@3.1.1: Use @exodus/bytes instead for a more spec-conformant and faster implementation
npm warn deprecated glob@7.2.3: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated @humanwhocodes/object-schema@2.0.3: Use @eslint/object-schema instead
npm warn deprecated glob@11.1.0: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated eslint@8.57.1: This version is no longer supported. Please see https://eslint.org/version-support for other options.

added 640 packages, and audited 641 packages in 6s

171 packages are looking for funding
  run `npm fund` for details

8 vulnerabilities (3 moderate, 4 high, 1 critical)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
~~~

## typecheck
~~~text

> precision-lab-frontend@0.1.0 typecheck
> tsc --noEmit

~~~

## unit
~~~text

> precision-lab-frontend@0.1.0 test
> vitest run


[1m[7m[36m RUN [39m[27m[22m [36mv2.1.9 [39m[90m/home/runner/work/precision-lab-plus/precision-lab-plus/frontend[39m

 [32m✓[39m src/__tests__/ResultPanel.test.tsx [2m([22m[2m19 tests[22m[2m)[22m[33m 544[2mms[22m[39m
 [32m✓[39m src/__tests__/BasicMode.test.tsx [2m([22m[2m16 tests[22m[2m)[22m[33m 1070[2mms[22m[39m
   [33m[2m✓[22m[39m BasicMode[2m > [22marma el payload correcto contra /evaluate [33m315[2mms[22m[39m
 [32m✓[39m src/__tests__/GraphMode.test.tsx [2m([22m[2m7 tests[22m[2m)[22m[33m 1381[2mms[22m[39m
   [33m[2m✓[22m[39m GraphMode[2m > [22marma el payload correcto contra /graph/2d con una sola expresión [33m314[2mms[22m[39m
   [33m[2m✓[22m[39m GraphMode[2m > [22marma el payload correcto con dos expresiones y dominio explícito [33m327[2mms[22m[39m
 [32m✓[39m src/__tests__/calculusIntent.test.ts [2m([22m[2m20 tests[22m[2m)[22m[90m 256[2mms[22m[39m
 [31m❯[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts [2m([22m[2m24 tests[22m[2m | [22m[31m4 failed[39m[2m)[22m[90m 63[2mms[22m[39m
[31m   [31m×[31m Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22minventario: etiquetas y tooltips semánticos[90m 23[2mms[22m[31m[39m
[31m     → expected [ 'porcentaje' ] to deeply equal [][39m
[31m   [31m×[31m Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización hiperbólica inversa: csch inversa[90m 3[2mms[22m[31m[39m
[31m     → expected '^(-1)(2)' to be 'acsch(2)' // Object.is equality[39m
[31m   [31m×[31m Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización hiperbólica inversa: sech inversa[90m 1[2mms[22m[31m[39m
[31m     → expected '^(-1)(0.5)' to be 'asech(0.5)' // Object.is equality[39m
[31m   [31m×[31m Suite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización mathrm: Log complejo[90m 2[2mms[22m[31m[39m
[31m     → expected 'l o g(-1)' to be 'log(-1)' // Object.is equality[39m
 [32m✓[39m src/__tests__/MatrixMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 626[2mms[22m[39m
   [33m[2m✓[22m[39m MatrixMode[2m > [22marma el payload correcto contra /matrix/operations con una matriz 2x2 completa [33m321[2mms[22m[39m
 [32m✓[39m src/__tests__/e2e.test.tsx [2m([22m[2m1 test[22m[2m)[22m[33m 832[2mms[22m[39m
   [33m[2m✓[22m[39m E2E mínimo — Derivada (sección 15)[2m > [22mx**2 en Derivada -> MathResponse real -> steps renderizados -> historial -> reuseEntry reejecuta [33m821[2mms[22m[39m
 [32m✓[39m src/__tests__/historyStore.test.ts [2m([22m[2m8 tests[22m[2m)[22m[90m 23[2mms[22m[39m
 [32m✓[39m src/__tests__/IntegralMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 831[2mms[22m[39m
 [32m✓[39m src/__tests__/SystemMode.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 865[2mms[22m[39m
 [32m✓[39m src/__tests__/useRecentKeysStore.test.ts [2m([22m[2m9 tests[22m[2m)[22m[90m 14[2mms[22m[39m
 [32m✓[39m src/__tests__/unitConversion.test.ts [2m([22m[2m22 tests[22m[2m)[22m[90m 16[2mms[22m[39m
 [32m✓[39m src/__tests__/EquationMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 732[2mms[22m[39m
 [32m✓[39m src/__tests__/LimitMode.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 887[2mms[22m[39m
   [33m[2m✓[22m[39m LimitMode[2m > [22marma el payload correcto contra /limit con un punto finito [33m322[2mms[22m[39m
 [32m✓[39m src/__tests__/KeyboardBasicPanelV5.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[33m 646[2mms[22m[39m
   [33m[2m✓[22m[39m KeyboardBasicPanel V5[2m > [22mmantiene el inventario básico acordado y usa Enter en doble columna [33m378[2mms[22m[39m
 [32m✓[39m src/__tests__/NaturalMathField.test.ts [2m([22m[2m13 tests[22m[2m)[22m[90m 41[2mms[22m[39m
 [32m✓[39m src/__tests__/contract.test.ts [2m([22m[2m4 tests[22m[2m)[22m[90m 5[2mms[22m[39m
[90mstderr[2m | src/__tests__/GraphViewer.test.tsx[2m > [22m[2mGraphViewer[2m > [22m[2mel botón 'Descargar PNG' llama a Plotly.toImage
[22m[39mError: Not implemented: navigation (except hash changes)
    at module.exports (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/browser/not-implemented.js:9:17)
    at navigateFetch (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js:77:3)
    at exports.navigate (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js:55:3)
    at Timeout._onTimeout (/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHyperlinkElementUtils-impl.js:81:7)
    at listOnTimeout (node:internal/timers:585:17)
    at processTimers (node:internal/timers:521:7) [90mundefined[39m

 [32m✓[39m src/__tests__/GraphViewer.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 353[2mms[22m[39m
 [32m✓[39m src/__tests__/DerivativeMode.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 656[2mms[22m[39m
   [33m[2m✓[22m[39m DerivativeMode[2m > [22marma el payload correcto contra /derivative [33m350[2mms[22m[39m
 [32m✓[39m src/__tests__/client.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 9[2mms[22m[39m
 [32m✓[39m src/__tests__/History.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[90m 193[2mms[22m[39m
 [32m✓[39m src/__tests__/MathKeyboard.test.tsx [2m([22m[2m4 tests[22m[2m)[22m[33m 471[2mms[22m[39m
 [31m❯[39m src/__tests__/KeyboardParityV5.test.ts [2m([22m[2m5 tests[22m[2m | [22m[31m1 failed[39m[2m)[22m[90m 12[2mms[22m[39m
[31m   [31m×[31m paridad de especificación del teclado V5 de Plus[2m > [22mmantiene la paridad Plus: ∂/∂x activa y Π como pendiente real[90m 6[2mms[22m[31m[39m
[31m     → expected false to be true // Object.is equality[39m
 [31m❯[39m src/__tests__/exhaustive-module10-keyboard-inventory.test.ts [2m([22m[2m5 tests[22m[2m | [22m[31m1 failed[39m[2m)[22m[90m 36[2mms[22m[39m
[31m   [31m×[31m Suite exhaustiva original — Módulo 10: inventario teclado Plus[2m > [22mPlus conserva como única KeyDef unavailable a Productoria[90m 11[2mms[22m[31m[39m
[31m     → expected [] to deeply equal [ 'productoria' ][39m
 [31m❯[39m src/__tests__/KeyboardInventoryV5.test.ts [2m([22m[2m6 tests[22m[2m | [22m[31m1 failed[39m[2m)[22m[90m 33[2mms[22m[39m
[31m   [31m×[31m inventario estructural del teclado V5 de Plus[2m > [22mmantiene productoria pendiente sin degradar la derivada parcial de Plus[90m 8[2mms[22m[31m[39m
[31m     → expected [] to include 'productoria'[39m
 [32m✓[39m src/exhaustive-module08-units.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 9[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module14-branding-natural-text.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 258[2mms[22m[39m
 [32m✓[39m src/__tests__/BrandingV521.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 124[2mms[22m[39m
 [32m✓[39m src/__tests__/MathRenderer.test.tsx [2m([22m[2m3 tests[22m[2m)[22m[90m 64[2mms[22m[39m
 [32m✓[39m src/__tests__/fractionDisplay.test.ts [2m([22m[2m9 tests[22m[2m)[22m[90m 22[2mms[22m[39m
 [32m✓[39m src/__tests__/systemSplit.test.ts [2m([22m[2m6 tests[22m[2m)[22m[90m 14[2mms[22m[39m
 [32m✓[39m src/__tests__/exhaustive-module11-layout-responsive.test.ts [2m([22m[2m2 tests[22m[2m)[22m[90m 10[2mms[22m[39m
 [32m✓[39m src/__tests__/LayoutDefaultV521.test.ts [2m([22m[2m2 tests[22m[2m)[22m[90m 7[2mms[22m[39m

[31m⎯⎯⎯⎯⎯⎯⎯[1m[7m Failed Tests 7 [27m[22m⎯⎯⎯⎯⎯⎯⎯[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/KeyboardInventoryV5.test.ts[2m > [22minventario estructural del teclado V5 de Plus[2m > [22mmantiene productoria pendiente sin degradar la derivada parcial de Plus
[31m[1mAssertionError[22m: expected [] to include 'productoria'[39m
[36m [2m❯[22m src/__tests__/KeyboardInventoryV5.test.ts:[2m75:31[22m[39m
    [90m 73| [39m      [33m.[39m[34mmap[39m((key) [33m=>[39m key[33m.[39mariaLabel)[33m;[39m
    [90m 74| [39m
    [90m 75| [39m    [34mexpect[39m(unavailableLabels)[33m.[39m[34mtoContain[39m([32m"productoria"[39m)[33m;[39m
    [90m   | [39m                              [31m^[39m
    [90m 76| [39m    [34mexpect[39m(unavailableLabels)[33m.[39mnot[33m.[39m[34mtoContain[39m([32m"derivada parcial"[39m)[33m;[39m
    [90m 77| [39m  })[33m;[39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/7]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/KeyboardParityV5.test.ts[2m > [22mparidad de especificación del teclado V5 de Plus[2m > [22mmantiene la paridad Plus: ∂/∂x activa y Π como pendiente real
[31m[1mAssertionError[22m: expected false to be true // Object.is equality[39m

[32m- Expected[39m
[31m+ Received[39m

[32m- true[39m
[31m+ false[39m

[36m [2m❯[22m src/__tests__/KeyboardParityV5.test.ts:[2m48:34[22m[39m
    [90m 46| [39m    [34mexpect[39m(partial[33m?.[39munavailable)[33m.[39m[34mtoBeFalsy[39m()[33m;[39m
    [90m 47| [39m    [34mexpect[39m(partial[33m?.[39minsertLatex)[33m.[39m[34mtoBe[39m([32m"\\frac{\\partial}{\\partial x}\[39m…
    [90m 48| [39m    [34mexpect[39m(product[33m?.[39munavailable)[33m.[39m[34mtoBe[39m([35mtrue[39m)[33m;[39m
    [90m   | [39m                                 [31m^[39m
    [90m 49| [39m    [34mexpect[39m(product[33m?.[39minsertLatex)[33m.[39m[34mtoBe[39m([32m""[39m)[33m;[39m
    [90m 50| [39m  })[33m;[39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[2/7]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-inventory.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: inventario teclado Plus[2m > [22mPlus conserva como única KeyDef unavailable a Productoria
[31m[1mAssertionError[22m: expected [] to deeply equal [ 'productoria' ][39m

[32m- Expected[39m
[31m+ Received[39m

[32m- Array [[39m
[32m-   "productoria",[39m
[32m- ][39m
[31m+ Array [][39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-inventory.test.ts:[2m56:25[22m[39m
    [90m 54| [39m  [34mit[39m([32m"Plus conserva como única KeyDef unavailable a Productoria"[39m[33m,[39m () [33m=[39m…
    [90m 55| [39m    [35mconst[39m unavailable [33m=[39m [[33m...[39m[35mnew[39m [33mSet[39m(allKeys[33m.[39m[34mfilter[39m(k [33m=>[39m k[33m.[39munavailable)…
    [90m 56| [39m    [34mexpect[39m(unavailable)[33m.[39m[34mtoEqual[39m([[32m"productoria"[39m])[33m;[39m
    [90m   | [39m                        [31m^[39m
    [90m 57| [39m  })[33m;[39m
    [90m 58| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[3/7]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22minventario: etiquetas y tooltips semánticos
[31m[1mAssertionError[22m: expected [ 'porcentaje' ] to deeply equal [][39m

[32m- Expected[39m
[31m+ Received[39m

[32m- Array [][39m
[31m+ Array [[39m
[31m+   "porcentaje",[39m
[31m+ ][39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m35:21[22m[39m
    [90m 33| [39m      [35mif[39m ([33m![39mstructuralLabels[33m.[39m[34mhas[39m(key[33m.[39mariaLabel) [33m&&[39m [33m![39mkey[33m.[39mdescription[33m?.[39m[34mtr[39m…
    [90m 34| [39m    }
    [90m 35| [39m    [34mexpect[39m(missing)[33m.[39m[34mtoEqual[39m([])[33m;[39m
    [90m   | [39m                    [31m^[39m
    [90m 36| [39m  })[33m;[39m
    [90m 37| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[4/7]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización hiperbólica inversa: csch inversa
[31m[1mAssertionError[22m: expected '^(-1)(2)' to be 'acsch(2)' // Object.is equality[39m

Expected: [32m"[7macsch[27m(2)"[39m
Received: [31m"[7m^(-1)[27m(2)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m77:41[22m[39m
    [90m 75| [39m    [[32m"coth inversa"[39m[33m,[39m [32m"\\coth^{-1}\\left(2\\right)"[39m[33m,[39m [32m"acoth(2)"[39m][33m,[39m
    [90m 76| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización hiperbólica inversa: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m…
    [90m 77| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 78| [39m  })[33m;[39m
    [90m 79| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[5/7]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización hiperbólica inversa: sech inversa
[31m[1mAssertionError[22m: expected '^(-1)(0.5)' to be 'asech(0.5)' // Object.is equality[39m

Expected: [32m"[7masech[27m(0.5)"[39m
Received: [31m"[7m^(-1)[27m(0.5)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m77:41[22m[39m
    [90m 75| [39m    [[32m"coth inversa"[39m[33m,[39m [32m"\\coth^{-1}\\left(2\\right)"[39m[33m,[39m [32m"acoth(2)"[39m][33m,[39m
    [90m 76| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización hiperbólica inversa: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m…
    [90m 77| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 78| [39m  })[33m;[39m
    [90m 79| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[6/7]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización mathrm: Log complejo
[31m[1mAssertionError[22m: expected 'l o g(-1)' to be 'log(-1)' // Object.is equality[39m

Expected: [32m"l[7mo[27mg(-1)"[39m
Received: [31m"l[7m o [27mg(-1)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m91:41[22m[39m
    [90m 89| [39m    [[32m"Log complejo"[39m[33m,[39m [32m"\\mathrm{log}\\left(-1\\right)"[39m[33m,[39m [32m"log(-1)"[39m][33m,[39m
    [90m 90| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización mathrm: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected) [33m=>[39m…
    [90m 91| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 92| [39m  })[33m;[39m
    [90m 93| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[7/7]⎯[22m[39m

[2m Test Files [22m [1m[31m4 failed[39m[22m[2m | [22m[1m[32m29 passed[39m[22m[90m (33)[39m
[2m      Tests [22m [1m[31m7 failed[39m[22m[2m | [22m[1m[32m232 passed[39m[22m[90m (239)[39m
[2m   Start at [22m 04:57:22
[2m   Duration [22m 18.31s[2m (transform 1.21s, setup 7.61s, collect 2.79s, tests 11.10s, environment 21.12s, prepare 3.99s)[22m


::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/KeyboardInventoryV5.test.ts,title=src/__tests__/KeyboardInventoryV5.test.ts > inventario estructural del teclado V5 de Plus > mantiene productoria pendiente sin degradar la derivada parcial de Plus,line=75,column=31::AssertionError: expected [] to include 'productoria'%0A ❯ src/__tests__/KeyboardInventoryV5.test.ts:75:31%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/KeyboardParityV5.test.ts,title=src/__tests__/KeyboardParityV5.test.ts > paridad de especificación del teclado V5 de Plus > mantiene la paridad Plus%3A ∂/∂x activa y Π como pendiente real,line=48,column=34::AssertionError: expected false to be true // Object.is equality%0A%0A- Expected%0A+ Received%0A%0A- true%0A+ false%0A%0A ❯ src/__tests__/KeyboardParityV5.test.ts:48:34%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-inventory.test.ts,title=src/__tests__/exhaustive-module10-keyboard-inventory.test.ts > Suite exhaustiva original — Módulo 10%3A inventario teclado Plus > Plus conserva como única KeyDef unavailable a Productoria,line=56,column=25::AssertionError: expected [] to deeply equal [ 'productoria' ]%0A%0A- Expected%0A+ Received%0A%0A- Array [%0A-   "productoria",%0A- ]%0A+ Array []%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-inventory.test.ts:56:25%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > inventario%3A etiquetas y tooltips semánticos,line=35,column=21::AssertionError: expected [ 'porcentaje' ] to deeply equal []%0A%0A- Expected%0A+ Received%0A%0A- Array []%0A+ Array [%0A+   "porcentaje",%0A+ ]%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:35:21%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización hiperbólica inversa%3A csch inversa,line=77,column=41::AssertionError: expected '^(-1)(2)' to be 'acsch(2)' // Object.is equality%0A%0AExpected: "acsch(2)"%0AReceived: "^(-1)(2)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:77:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización hiperbólica inversa%3A sech inversa,line=77,column=41::AssertionError: expected '^(-1)(0.5)' to be 'asech(0.5)' // Object.is equality%0A%0AExpected: "asech(0.5)"%0AReceived: "^(-1)(0.5)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:77:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización mathrm%3A Log complejo,line=91,column=41::AssertionError: expected 'l o g(-1)' to be 'log(-1)' // Object.is equality%0A%0AExpected: "log(-1)"%0AReceived: "l o g(-1)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:91:41%0A%0A
~~~

## build
~~~text

> precision-lab-frontend@0.1.0 build
> tsc --noEmit && vite build

[36mvite v5.4.21 [32mbuilding for production...[36m[39m
transforming...
[32m✓[39m 103 modules transformed.
rendering chunks...
computing gzip size...
[2mdist/[22m[32mmanifest.webmanifest                             [39m[1m[2m    0.46 kB[22m[1m[22m
[2mdist/[22m[32mindex.html                                       [39m[1m[2m    1.15 kB[22m[1m[22m[2m │ gzip:     0.54 kB[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size3-Regular-CTq5MqoE.woff         [39m[1m[2m    4.42 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size4-Regular-Dl5lxZxV.woff2        [39m[1m[2m    4.93 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size2-Regular-Dy4dx90m.woff2        [39m[1m[2m    5.21 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size1-Regular-mCD8mA8B.woff2        [39m[1m[2m    5.47 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size4-Regular-BF-4gkZK.woff         [39m[1m[2m    5.98 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size2-Regular-oD1tc_U0.woff         [39m[1m[2m    6.19 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size1-Regular-C195tn64.woff         [39m[1m[2m    6.50 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Regular-Di6jR-x-.woff2  [39m[1m[2m    6.91 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Bold-Dq_IR9rO.woff2     [39m[1m[2m    6.91 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size3-Regular-DgpXs0kz.ttf          [39m[1m[2m    7.59 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Regular-CTRA-rTL.woff   [39m[1m[2m    7.66 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Bold-BEiXGLvX.woff      [39m[1m[2m    7.72 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Script-Regular-D3wIWfF6.woff2       [39m[1m[2m    9.64 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Regular-DDBCnlJ7.woff2    [39m[1m[2m   10.34 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size4-Regular-DWFBv043.ttf          [39m[1m[2m   10.36 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Script-Regular-D5yQViql.woff        [39m[1m[2m   10.59 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Regular-CTYiF6lA.woff2      [39m[1m[2m   11.32 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Bold-CL6g_b3V.woff2         [39m[1m[2m   11.35 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size2-Regular-B7gKUWhC.ttf          [39m[1m[2m   11.51 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Italic-C3H0VqGB.woff2     [39m[1m[2m   12.03 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Bold-D1sUS0GD.woff2       [39m[1m[2m   12.22 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Size1-Regular-Dbsnue_I.ttf          [39m[1m[2m   12.23 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Regular-CS6fqUqJ.woff     [39m[1m[2m   12.32 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Regular-wX97UBjC.ttf    [39m[1m[2m   12.34 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Caligraphic-Bold-ATXxdsX0.ttf       [39m[1m[2m   12.37 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Regular-Dxdc4cR9.woff       [39m[1m[2m   13.21 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Bold-BsDP51OF.woff          [39m[1m[2m   13.30 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Typewriter-Regular-CO6r4hn1.woff2   [39m[1m[2m   13.57 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Italic-DN2j7dab.woff      [39m[1m[2m   14.11 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Bold-DbIhKOiC.woff        [39m[1m[2m   14.41 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Typewriter-Regular-C0xS9mPB.woff    [39m[1m[2m   16.03 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-BoldItalic-CZnvNsCZ.woff2      [39m[1m[2m   16.40 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-Italic-t53AETM-.woff2          [39m[1m[2m   16.44 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Script-Regular-C5JkGWo-.ttf         [39m[1m[2m   16.65 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-BoldItalic-DxDJ3AOS.woff2      [39m[1m[2m   16.78 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Italic-NWA7e6Wa.woff2          [39m[1m[2m   16.99 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-BoldItalic-iY-2wyZ7.woff       [39m[1m[2m   18.67 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-Italic-DA0__PXp.woff           [39m[1m[2m   18.75 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-BoldItalic-SpSLRI95.woff       [39m[1m[2m   19.41 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Regular-BNo7hRIc.ttf      [39m[1m[2m   19.44 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Regular-CB_wures.ttf        [39m[1m[2m   19.57 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Fraktur-Bold-BdnERNNW.ttf           [39m[1m[2m   19.58 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Italic-BMLOBm91.woff           [39m[1m[2m   19.68 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Italic-YYjJ1zSn.ttf       [39m[1m[2m   22.36 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_SansSerif-Bold-CFMepnvq.ttf         [39m[1m[2m   24.50 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Bold-Cx986IdX.woff2            [39m[1m[2m   25.32 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Regular-B22Nviop.woff2         [39m[1m[2m   26.27 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Typewriter-Regular-D3Ib7_Hf.ttf     [39m[1m[2m   27.56 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_AMS-Regular-BQhdFMY1.woff2          [39m[1m[2m   28.08 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Bold-Jm3AIy58.woff             [39m[1m[2m   29.91 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Regular-Dr94JaBh.woff          [39m[1m[2m   30.77 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-BoldItalic-B3XSjfu4.ttf        [39m[1m[2m   31.20 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Math-Italic-flOr_0UB.ttf            [39m[1m[2m   31.31 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-BoldItalic-DzxPMmG6.ttf        [39m[1m[2m   32.97 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_AMS-Regular-DMm9YOAa.woff           [39m[1m[2m   33.52 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Italic-3WenGoN9.ttf            [39m[1m[2m   33.58 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Bold-waoOVXN0.ttf              [39m[1m[2m   51.34 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_Main-Regular-ypZvNtVU.ttf           [39m[1m[2m   53.58 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[32mKaTeX_AMS-Regular-DRggAlZN.ttf            [39m[1m[2m   63.63 kB[22m[1m[22m
[2mdist/[22m[2massets/[22m[35mindex-CB_OEzbf.css                        [39m[1m[2m   66.01 kB[22m[1m[22m[2m │ gzip:    15.78 kB[22m
[2mdist/[22m[2massets/[22m[36mGraphViewer-DfD6gFqK.js                   [39m[1m[2m    2.57 kB[22m[1m[22m[2m │ gzip:     1.24 kB[22m
[2mdist/[22m[2massets/[22m[36mworkbox-window.prod.es5-BqEJf4Xk.js       [39m[1m[2m    5.71 kB[22m[1m[22m[2m │ gzip:     2.34 kB[22m
[2mdist/[22m[2massets/[22m[36mindex-Ceayy3r2.js                         [39m[1m[33m2,808.22 kB[39m[22m[2m │ gzip:   783.71 kB[22m
[2mdist/[22m[2massets/[22m[36mplotly.min-D1ncG283.js                    [39m[1m[33m4,840.47 kB[39m[22m[2m │ gzip: 1,468.44 kB[22m
[33m
(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking: https://rollupjs.org/configuration-options/#output-manualchunks
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.[39m
[32m✓ built in 22.31s[39m

[36mPWA v1.3.0[39m
mode      [35mgenerateSW[39m
precache  [32m10 entries[39m [2m(7554.33 KiB)[22m
files generated
  [2mdist/sw.js[22m
  [2mdist/workbox-9c191d2f.js[22m
~~~
