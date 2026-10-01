# B7 round 9 — 2026-10-01

## Verified certification of round 8

Plus QA head `365d3530da68c9eb6f4e5cacfe773bfc5ddd2c72`:

- S19 run **36901107460**: PASS. Global score **55.96026490066225%**, unchanged threshold **15.3%**, all **eight original files** present. Counts: Killed 1172, Timeout 11, Survived 637, NoCoverage 294, RuntimeError 1. Valid denominator 2114. The runtime error remains in inventory and does not count as a detected mutant. The aggregate rejects survivors with zero executed tests.
- S19 backend mutmut and certified Lite mutation jobs: PASS.
- CI, S17 API fuzzing, S18 differential properties, S20 performance, S21 compatibility, S23 accessibility, S25 security and Playwright E2E: PASS on that exact head.
- The old 13.59% measurement is superseded: test filtering with Stryker 10 and Vitest 5 used incompatible nested names. It must not be compared as a direct code-quality improvement against this corrected measurement.

## Mathematical correction submitted in round 9

IN-I-05 (`asin(x)<acos(x)`) is reduced using the exact real principal-branch identity `asin(u)+acos(u)=pi/2` for comparisons with the same argument. Keeping `asin(u)` in the reduced relation allows the solver to enforce its real domain. Strictness, operand order and user domain clipping remain in the generic solver.

Twelve direct service regression cases passed under pinned SymPy 1.13.3: all four comparison operators, swapped operands, scaled/reflected arguments, constant true/false relations, open domain clipping and disjoint domain. Expected IN-I-05 set is exactly `[-1,sqrt(2)/2)`. A further API regression is committed for Actions validation; the local environment cannot run the guarded API process boundary because AF_UNIX sockets are forbidden.

Do not mark IN-I-05 recertified until the API gate and trig matrix confirm the new head. The remaining previously known mathematical cases are EC-I-05, EC-HI-06, EC-HI-07 and ID-D-12. Full mathematical-result audit and visual recertification remain outstanding. B7 is open; no production merge/deployment was performed.
