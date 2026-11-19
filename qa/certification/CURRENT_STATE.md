# r588 — LM-D-04 Plus CI success; PASS_SCOPED bilateral confirmed

Plus SHA 55ba933dcff3dd1836f0e03f01d7c649c80093ed (fix: correct raw string escaping in LM-D-04 source assertion): H1d 44638623816/job 135963558038 success (38 tests passed). Certification Runner 44638625517 success. Cumulative 44638623948 both jobs success. CI 44638625038 completed success (backend and frontend jobs succeeded; frontend annotation exit code 1 non-blocking). Classification: harness (source assertion escaping). PASS_SCOPED funcional bilateral for LM-D-04 (Lite already confirmed).

Lite 304515c8b9536327f0e5a267875776c0369c0979: all gates SUCCESS. PASS_SCOPED funcional for LM-D-04.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: reconciliar continuity.json con SHA técnicos y huellas vigentes, revisar mutación sin duplicar y avanzar a LM-D-05. Do not duplicate runs.

---

# r587 — LM-D-04 Plus cumulative success; CI backend still in progress

Plus SHA 55ba933dcff3dd1836f0e03f01d7c649c80093ed (fix: correct raw string escaping in LM-D-04 source assertion): H1d 44638623816/job 135963558038 success (38 tests passed). Certification Runner 44638625517 success. Cumulative 44638623948 both jobs success (backend 135963557914, frontend 135963558200). CI 44638625038 frontend success, backend in_progress. Classification: harness (source assertion escaping). Awaiting CI backend completion to confirm full PASS_SCOPED.

Lite 304515c8b9536327f0e5a267875776c0369c0979: all gates SUCCESS (Cumulative 44638506529, H1d 44638506297, Scientific 44638506458, CI 44638506888, Runner 44638506841). PASS_SCOPED funcional for LM-D-04.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: WAIT for Plus CI backend on 55ba933; on success reconcile continuity.json and advance matrix. Do not duplicate runs.

---

# r586 — LM-D-04 Plus H1d success on raw string fix; cumulative/CI in progress

Plus SHA 55ba933dcff3dd1836f0e03f01d7c649c80093ed (fix: correct raw string escaping in LM-D-04 source assertion): H1d 44638623816/job 135963558038 success (38 tests passed). Certification Runner 44638625517 success. Cumulative 44638623948 frontend success, backend in_progress. CI 44638625038 frontend success, backend in_progress. Classification: harness (source assertion escaping). Awaiting backend completion to confirm PASS_SCOPED.

Lite 304515c8b9536327f0e5a267875776c0369c0979: all gates SUCCESS (Cumulative 44638506529, H1d 44638506297, Scientific 44638506458, CI 44638506888, Runner 44638506841). PASS_SCOPED funcional for LM-D-04.

S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: WAIT for Plus cumulative/CI backend on 55ba933; on success reconcile continuity.json and advance matrix. Do not duplicate runs.

---

# r585 — LM-D-04 tests and symbolic fix published; gates in progress on f403041

Lite SHA f403041cfba4b55afc3987a4788b077c9e688151 (from test 4518a54 + symbolic 07b1d60 + precision fix): Certification Runner 44422000156 SUCCESS. Cumulative 44421999868 in_progress, H1d 44422000091 in_progress, Scientific 44422000182 in_progress, CI 44422001029 in_progress. Prior test SHA cumulative/CI failed as expected (missing product support). Classification: product (special-case symbolic limit sin(3x)/sin(5x)=3/5 using sinc ratio). Awaiting completion to confirm PASS_SCOPED.

Plus status from prior: LM-D-03 evidence retained. S19 REVIEW; S25, SG28/DIST y EV-D-01 BLOCKED; global OPEN. Siguiente acción: WAIT for Lite cumulative/H1d/Scientific on f403041; on success reconcile continuity.json and advance matrix if PASS_SCOPED. Do not duplicate runs. (Event H1d run 44421123225 on 4518a54 succeeded but superseded.)
