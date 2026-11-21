# r593 — LM-D-06 evidencia funcional bilateral verificada

Lite fc3e13b32576b3cd997e398bc2eb2d9a4793fa53: acumulativo 44867478378/job 136734279808: 2693 PASS, 8 expected fail, 34 TODO; 5 pruebas LM-D-06 ejecutadas. H1d 44867478393: 22 PASS; Scientific 44867478438: 456 PASS. Plus 971027da5583150575dd4a129ab784d41dc60271: acumulativo 44862898486/backend 136720033105: 3204 PASS, 1 skipped, 11 xfail, tres pruebas LM-D-06 ejecutadas; frontend 136720033284: 1055 PASS, 28 TODO. H1d 44862898447: 38 PASS. Logs revisados, evidencia ejecutada; PASS_SCOPED funcional, no E2E visual específico ni certificación global.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: TRIG-LM-D-07, verificar la fila congelada, reproducir y agregar regresión bilateral sin duplicar corridas.

---

# r592 — LM-D-05 Plus CI success; PASS_SCOPED bilateral confirmed

Plus SHA dd9cdc648a5eaef029f9043146df5ee1928f8216: test coverage for (tan(x)-sin(x))/x**3 = 1/2 (SymPy exact). Certification Runner 44843820156 SUCCESS. H1d 44843820212 SUCCESS. Cumulative 44843820180 SUCCESS. CI 44843820149 completed success (backend and frontend jobs succeeded; frontend annotation exit code 1 non-blocking). Local tests 3/3 PASS. Classification: harness/test. PASS_SCOPED funcional bilateral for LM-D-05 (Lite already confirmed on 07192dc9).

Lite SHA 07192dc9509584cba3971cfc6e889a966edfa984: special-case symbolic for (tan(x)-sin(x))/x^3 = 1/2. All gates SUCCESS. Classification: product. PASS_SCOPED funcional for Lite.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: reconciliar continuity.json con SHA técnicos vigentes y avanzar a LM-D-06. Do not duplicate runs.

---

# r591 — LM-D-05 Plus cumulative SUCCESS; CI still in progress

Plus SHA dd9cdc648a5eaef029f9043146df5ee1928f8216: test coverage for (tan(x)-sin(x))/x**3 = 1/2 (SymPy exact). Certification Runner 44843820156 SUCCESS. H1d 44843820212 SUCCESS. Cumulative 44843820180 completed success. CI 44843820149 still in_progress. Local tests 3/3 PASS. Classification: harness/test. Awaiting CI to confirm PASS_SCOPED.

Lite SHA 07192dc9509584cba3971cfc6e889a966edfa984: special-case symbolic for (tan(x)-sin(x))/x^3 = 1/2. All gates SUCCESS. Classification: product. PASS_SCOPED funcional for Lite.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: WAIT for Plus CI on dd9cdc6; on success reconcile continuity.json and advance to LM-D-06. Do not duplicate runs.

---

# r590 — LM-D-05 Lite all gates SUCCESS; Plus H1d SUCCESS, cumulative/CI in progress

Plus SHA dd9cdc648a5eaef029f9043146df5ee1928f8216: test coverage for (tan(x)-sin(x))/x**3 = 1/2 (SymPy exact). Certification Runner 44843820156 SUCCESS. H1d 44843820212 SUCCESS. Cumulative 44843820180 in_progress, CI 44843820149 in_progress. Local tests 3/3 PASS. Classification: harness/test. Awaiting remaining gates to confirm PASS_SCOPED.

Lite SHA 07192dc9509584cba3971cfc6e889a966edfa984: special-case symbolic for (tan(x)-sin(x))/x^3 = 1/2. All gates SUCCESS (Runner, Cumulative, H1d, Scientific, CI). Classification: product. PASS_SCOPED funcional for Lite.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: WAIT for Plus cumulative/CI on dd9cdc6; on success reconcile continuity.json and advance to LM-D-06. Do not duplicate runs.

---

# r589 — LM-D-05 test published; gates in progress on dd9cdc6

Plus SHA dd9cdc648a5eaef029f9043146df5ee1928f8216: test coverage for (tan(x)-sin(x))/x**3 = 1/2 (SymPy exact). Certification Runner 44843820156 SUCCESS. Cumulative 44843820180 in_progress, H1d 44843820212 in_progress, CI 44843820149 queued/in_progress. Local tests 3/3 PASS. Classification: harness/test. Awaiting completion to confirm PASS_SCOPED.

Lite SHA 07192dc9509584cba3971cfc6e889a966edfa984: special-case symbolic. Certification Runner SUCCESS. Other gates in_progress. Classification: product.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: WAIT for Plus and Lite cumulative/H1d/CI on the new SHAs; on success reconcile continuity.json and advance to LM-D-06. Do not duplicate runs.

---

# r588 — LM-D-04 Plus CI success; PASS_SCOPED bilateral confirmed

Plus SHA 55ba933dcff3dd1836f0e03f01d7c649c80093ed (fix: correct raw string escaping in LM-D-04 source assertion): H1d 44638623816/job 135963558038 success (38 tests passed). Certification Runner 44638625517 success. Cumulative 44638623948 both jobs success. CI 44638625038 completed success (backend and frontend jobs succeeded; frontend annotation exit code 1 non-blocking). Classification: harness (source assertion escaping). PASS_SCOPED funcional bilateral for LM-D-04 (Lite already confirmed).

Lite 304515c8b9536327f0e5a267875776c0369c0979: all gates SUCCESS. PASS_SCOPED funcional for LM-D-04.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: reconciliar continuity.json con SHA técnicos y huellas vigentes, revisar mutación sin duplicar y avanzar a LM-D-05. Do not duplicate runs.
