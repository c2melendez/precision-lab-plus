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
    [90m 61| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[5/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización real: csc inversa
[31m[1mAssertionError[22m: expected 'csc ^(-1)(2)' to match /^(?:acsc|arccsc)\(2\)$/[39m

[32m- Expected:[39m 
/^(?:acsc|arccsc)\(2\)$/

[31m+ Received:[39m 
"csc ^(-1)(2)"

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m59:41[22m[39m
    [90m 57| [39m    [[32m"cot inversa"[39m[33m,[39m [32m"\\cot^{-1}\\left(1\\right)"[39m[33m,[39m [36m/^(?:acot|arccot)\(1[39m…
    [90m 58| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización real: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected) [33m=>[39m {
    [90m 59| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoMatch[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 60| [39m  })[33m;[39m
    [90m 61| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[6/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización real: sec inversa
[31m[1mAssertionError[22m: expected 'sec ^(-1)(2)' to match /^(?:asec|arcsec)\(2\)$/[39m

[32m- Expected:[39m 
/^(?:asec|arcsec)\(2\)$/

[31m+ Received:[39m 
"sec ^(-1)(2)"

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m59:41[22m[39m
    [90m 57| [39m    [[32m"cot inversa"[39m[33m,[39m [32m"\\cot^{-1}\\left(1\\right)"[39m[33m,[39m [36m/^(?:acot|arccot)\(1[39m…
    [90m 58| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización real: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected) [33m=>[39m {
    [90m 59| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoMatch[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 60| [39m  })[33m;[39m
    [90m 61| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[7/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización real: cot inversa
[31m[1mAssertionError[22m: expected 'cot ^(-1)(1)' to match /^(?:acot|arccot)\(1\)$/[39m

[32m- Expected:[39m 
/^(?:acot|arccot)\(1\)$/

[31m+ Received:[39m 
"cot ^(-1)(1)"

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m59:41[22m[39m
    [90m 57| [39m    [[32m"cot inversa"[39m[33m,[39m [32m"\\cot^{-1}\\left(1\\right)"[39m[33m,[39m [36m/^(?:acot|arccot)\(1[39m…
    [90m 58| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización real: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected) [33m=>[39m {
    [90m 59| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoMatch[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 60| [39m  })[33m;[39m
    [90m 61| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[8/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mlogaritmo con base real: log₂
[31m[1mAssertionError[22m: expected 'log _2(8)' to be 'log(8,2)' // Object.is equality[39m

Expected: [32m"log(8[7m,2[27m)"[39m
Received: [31m"log[7m _2[27m(8)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m66:41[22m[39m
    [90m 64| [39m    [[32m"log base editable"[39m[33m,[39m [32m"\\log_{3}\\left(81\\right)"[39m[33m,[39m [32m"log(81,3)"[39m][33m,[39m
    [90m 65| [39m  ] [35mas[39m [35mconst[39m)([32m"logaritmo con base real: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected)…
    [90m 66| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 67| [39m  })[33m;[39m
    [90m 68| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[9/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mlogaritmo con base real: log base editable
[31m[1mAssertionError[22m: expected 'log _3(81)' to be 'log(81,3)' // Object.is equality[39m

Expected: [32m"log(81[7m,3[27m)"[39m
Received: [31m"log[7m _3[27m(81)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m66:41[22m[39m
    [90m 64| [39m    [[32m"log base editable"[39m[33m,[39m [32m"\\log_{3}\\left(81\\right)"[39m[33m,[39m [32m"log(81,3)"[39m][33m,[39m
    [90m 65| [39m  ] [35mas[39m [35mconst[39m)([32m"logaritmo con base real: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected)…
    [90m 66| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 67| [39m  })[33m;[39m
    [90m 68| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[10/18]⎯[22m[39m

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

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[11/18]⎯[22m[39m

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

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[12/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización mathrm: sign
[31m[1mAssertionError[22m: expected 's i g n(-4)' to be 'sign(-4)' // Object.is equality[39m

Expected: [32m"s[7mig[27mn(-4)"[39m
Received: [31m"s[7m i g [27mn(-4)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m91:41[22m[39m
    [90m 89| [39m    [[32m"Log complejo"[39m[33m,[39m [32m"\\mathrm{log}\\left(-1\\right)"[39m[33m,[39m [32m"log(-1)"[39m][33m,[39m
    [90m 90| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización mathrm: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected) [33m=>[39m…
    [90m 91| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 92| [39m  })[33m;[39m
    [90m 93| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[13/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mnormalización mathrm: root complejo
[31m[1mAssertionError[22m: expected 'r o o t(27,3)' to be 'root(27,3)' // Object.is equality[39m

Expected: [32m"r[7moo[27mt(27,3)"[39m
Received: [31m"r[7m o o [27mt(27,3)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m91:41[22m[39m
    [90m 89| [39m    [[32m"Log complejo"[39m[33m,[39m [32m"\\mathrm{log}\\left(-1\\right)"[39m[33m,[39m [32m"log(-1)"[39m][33m,[39m
    [90m 90| [39m  ] [35mas[39m [35mconst[39m)([32m"normalización mathrm: %s"[39m[33m,[39m (_label[33m,[39m latex[33m,[39m expected) [33m=>[39m…
    [90m 91| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m(latex))[33m.[39m[34mtoBe[39m(expected)[33m;[39m
    [90m   | [39m                                        [31m^[39m
    [90m 92| [39m  })[33m;[39m
    [90m 93| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[14/18]⎯[22m[39m

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

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[15/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mporcentaje conserva semántica de porcentaje
[31m[1mAssertionError[22m: expected '50%' not to contain '%'[39m

Expected: [32m"%"[39m
Received: [31m"[7m50[27m%"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m96:28[22m[39m
    [90m 94| [39m  [34mit[39m([32m"porcentaje conserva semántica de porcentaje"[39m[33m,[39m () [33m=>[39m {
    [90m 95| [39m    [35mconst[39m normalized [33m=[39m [34mlatexToBackendSyntax[39m([32m"50\\%"[39m)[33m;[39m
    [90m 96| [39m    [34mexpect[39m(normalized)[33m.[39mnot[33m.[39m[34mtoContain[39m([32m"%"[39m)[33m;[39m
    [90m   | [39m                           [31m^[39m
    [90m 97| [39m    [34mexpect[39m(normalized)[33m.[39m[34mtoMatch[39m([36m/50.*100/[39m)[33m;[39m
    [90m 98| [39m  })[33m;[39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[16/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22m± se normaliza a pm()
[31m[1mAssertionError[22m: expected '+-(5)' to be 'pm(5)' // Object.is equality[39m

Expected: [32m"[7mpm[27m(5)"[39m
Received: [31m"[7m+-[27m(5)"[39m

[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m101:58[22m[39m
    [90m 99| [39m
    [90m100| [39m  [34mit[39m([32m"± se normaliza a pm()"[39m[33m,[39m () [33m=>[39m {
    [90m101| [39m    [34mexpect[39m([34mlatexToBackendSyntax[39m([32m"\\pm\\left(5\\right)"[39m))[33m.[39m[34mtoBe[39m([32m"pm(5)"[39m)[33m;[39m
    [90m   | [39m                                                         [31m^[39m
    [90m102| [39m  })[33m;[39m
    [90m103| [39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[17/18]⎯[22m[39m

[31m[1m[7m FAIL [27m[22m[39m src/__tests__/exhaustive-module10-keyboard-parity.test.ts[2m > [22mSuite exhaustiva original — Módulo 10: teclado ↔ motor (Plus frontend)[2m > [22mPlus mantiene activas parcial/Res/Sing y Productoria debe dejar de ser unavailable
[31m[1mAssertionError[22m: expected [ 'productoria' ] to not include 'productoria'[39m
[36m [2m❯[22m src/__tests__/exhaustive-module10-keyboard-parity.test.ts:[2m111:32[22m[39m
    [90m109| [39m      [32m"residuo en un polo (funciones racionales)"[39m[33m,[39m
    [90m110| [39m      [32m"singularidades (funciones racionales)"[39m[33m,[39m
    [90m111| [39m    ]) [34mexpect[39m(unavailable)[33m.[39mnot[33m.[39m[34mtoContain[39m(label)[33m;[39m
    [90m   | [39m                               [31m^[39m
    [90m112| [39m  })[33m;[39m
    [90m113| [39m})[33m;[39m

[31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[18/18]⎯[22m[39m

[2m Test Files [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m32 passed[39m[22m[90m (33)[39m
[2m      Tests [22m [1m[31m18 failed[39m[22m[2m | [22m[1m[32m221 passed[39m[22m[90m (239)[39m
[2m   Start at [22m 04:49:53
[2m   Duration [22m 17.57s[2m (transform 1.10s, setup 7.09s, collect 2.72s, tests 10.47s, environment 20.94s, prepare 3.84s)[22m


::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > inventario%3A etiquetas y tooltips semánticos,line=35,column=21::AssertionError: expected [ 'porcentaje', 'productoria' ] to deeply equal []%0A%0A- Expected%0A+ Received%0A%0A- Array []%0A+ Array [%0A+   "porcentaje",%0A+   "productoria",%0A+ ]%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:35:21%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > Productoria Π cumple el requisito actualizado,line=41,column=34::AssertionError: expected true to be falsy%0A%0A- Expected%0A+ Received%0A%0A- false%0A+ true%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:41:34%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización real%3A sin inversa,line=59,column=41::AssertionError: expected 'sin ^(-1)(0.5)' to match /^(?:asin|arcsin)\(0\.5\)$/%0A%0A- Expected: %0A/^(?:asin|arcsin)\(0\.5\)$/%0A%0A+ Received: %0A"sin ^(-1)(0.5)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:59:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización real%3A cos inversa,line=59,column=41::AssertionError: expected 'cos ^(-1)(0.5)' to match /^(?:acos|arccos)\(0\.5\)$/%0A%0A- Expected: %0A/^(?:acos|arccos)\(0\.5\)$/%0A%0A+ Received: %0A"cos ^(-1)(0.5)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:59:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización real%3A tan inversa,line=59,column=41::AssertionError: expected 'tan ^(-1)(1)' to match /^(?:atan|arctan)\(1\)$/%0A%0A- Expected: %0A/^(?:atan|arctan)\(1\)$/%0A%0A+ Received: %0A"tan ^(-1)(1)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:59:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización real%3A csc inversa,line=59,column=41::AssertionError: expected 'csc ^(-1)(2)' to match /^(?:acsc|arccsc)\(2\)$/%0A%0A- Expected: %0A/^(?:acsc|arccsc)\(2\)$/%0A%0A+ Received: %0A"csc ^(-1)(2)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:59:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización real%3A sec inversa,line=59,column=41::AssertionError: expected 'sec ^(-1)(2)' to match /^(?:asec|arcsec)\(2\)$/%0A%0A- Expected: %0A/^(?:asec|arcsec)\(2\)$/%0A%0A+ Received: %0A"sec ^(-1)(2)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:59:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización real%3A cot inversa,line=59,column=41::AssertionError: expected 'cot ^(-1)(1)' to match /^(?:acot|arccot)\(1\)$/%0A%0A- Expected: %0A/^(?:acot|arccot)\(1\)$/%0A%0A+ Received: %0A"cot ^(-1)(1)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:59:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > logaritmo con base real%3A log₂,line=66,column=41::AssertionError: expected 'log _2(8)' to be 'log(8,2)' // Object.is equality%0A%0AExpected: "log(8,2)"%0AReceived: "log _2(8)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:66:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > logaritmo con base real%3A log base editable,line=66,column=41::AssertionError: expected 'log _3(81)' to be 'log(81,3)' // Object.is equality%0A%0AExpected: "log(81,3)"%0AReceived: "log _3(81)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:66:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización hiperbólica inversa%3A csch inversa,line=77,column=41::AssertionError: expected '^(-1)(2)' to be 'acsch(2)' // Object.is equality%0A%0AExpected: "acsch(2)"%0AReceived: "^(-1)(2)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:77:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización hiperbólica inversa%3A sech inversa,line=77,column=41::AssertionError: expected '^(-1)(0.5)' to be 'asech(0.5)' // Object.is equality%0A%0AExpected: "asech(0.5)"%0AReceived: "^(-1)(0.5)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:77:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización mathrm%3A sign,line=91,column=41::AssertionError: expected 's i g n(-4)' to be 'sign(-4)' // Object.is equality%0A%0AExpected: "sign(-4)"%0AReceived: "s i g n(-4)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:91:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización mathrm%3A root complejo,line=91,column=41::AssertionError: expected 'r o o t(27,3)' to be 'root(27,3)' // Object.is equality%0A%0AExpected: "root(27,3)"%0AReceived: "r o o t(27,3)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:91:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > normalización mathrm%3A Log complejo,line=91,column=41::AssertionError: expected 'l o g(-1)' to be 'log(-1)' // Object.is equality%0A%0AExpected: "log(-1)"%0AReceived: "l o g(-1)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:91:41%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > porcentaje conserva semántica de porcentaje,line=96,column=28::AssertionError: expected '50%25' not to contain '%25'%0A%0AExpected: "%25"%0AReceived: "50%25"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:96:28%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > ± se normaliza a pm(),line=101,column=58::AssertionError: expected '+-(5)' to be 'pm(5)' // Object.is equality%0A%0AExpected: "pm(5)"%0AReceived: "+-(5)"%0A%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:101:58%0A%0A

::error file=/home/runner/work/precision-lab-plus/precision-lab-plus/frontend/src/__tests__/exhaustive-module10-keyboard-parity.test.ts,title=src/__tests__/exhaustive-module10-keyboard-parity.test.ts > Suite exhaustiva original — Módulo 10%3A teclado ↔ motor (Plus frontend) > Plus mantiene activas parcial/Res/Sing y Productoria debe dejar de ser unavailable,line=111,column=32::AssertionError: expected [ 'productoria' ] to not include 'productoria'%0A ❯ src/__tests__/exhaustive-module10-keyboard-parity.test.ts:111:32%0A%0A
(node:2378) MaxListenersExceededWarning: Possible EventEmitter memory leak detected. 11 unhandledRejection listeners added to [process]. MaxListeners is 10. Use emitter.setMaxListeners() to increase limit
(Use `node --trace-warnings ...` to show where the warning was created)
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
[2mdist/[22m[32mindex.html                                       [39m[1m[2m    1.15 kB[22m[1m[22m[2m │ gzip:     0.55 kB[22m
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
[2mdist/[22m[2massets/[22m[36mGraphViewer-DC9mZXSq.js                   [39m[1m[2m    2.51 kB[22m[1m[22m[2m │ gzip:     1.23 kB[22m
[2mdist/[22m[2massets/[22m[36mworkbox-window.prod.es5-BqEJf4Xk.js       [39m[1m[2m    5.71 kB[22m[1m[22m[2m │ gzip:     2.34 kB[22m
[2mdist/[22m[2massets/[22m[36mindex-fiLKh8hg.js                         [39m[1m[33m2,806.73 kB[39m[22m[2m │ gzip:   783.33 kB[22m
[2mdist/[22m[2massets/[22m[36mplotly.min-DyxsSTri.js                    [39m[1m[33m4,840.47 kB[39m[22m[2m │ gzip: 1,468.44 kB[22m
[33m
(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking: https://rollupjs.org/configuration-options/#output-manualchunks
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.[39m
[32m✓ built in 20.98s[39m

[36mPWA v1.3.0[39m
mode      [35mgenerateSW[39m
precache  [32m10 entries[39m [2m(7552.81 KiB)[22m
files generated
  [2mdist/sw.js[22m
  [2mdist/workbox-9c191d2f.js[22m
~~~
