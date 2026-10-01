# B7 round 10 — 2026-10-01

## Verified preceding head

Head `380115d91ee6d2655dcf247e90f6afe85e63e2e9`: all ten workflows passed (CI, S17, S18, S19, S20, S21, S23, S25, Playwright E2E and trig diagnostic matrix).

- CI run 36904307085: 516 backend tests and 457 frontend tests passed; backend coverage rounded to 77%, above unchanged 75%.
- Matrix run 36904298421: 324 rows, **310 RESULT / 13 ERROR / 1 SKIP_CONTEXT**.
- IN-I-05 is now recertified through the full keyboard/parser/API path. Its actual output is exactly `[-1,sqrt(2)/2)`, matching the independent expected interval.

## Real inverse hyperbolic correction submitted

Same-argument principal real identities:

- `atanh(u)=asinh(u)` is equivalent to `u=0`. Their difference is odd and has positive derivative for nonzero u in (-1,1), with equality at zero only.
- `acosh(u)=asinh(u)` has no real solution. In the common real domain u>=1, the logarithmic expression for asinh is strictly larger than that for acosh.

The reduction applies in either operand order, only with identical arguments and real-domain requests. Generic algebraic solving and requested domain restrictions remain responsible for finding/filtering roots of u=0. Original equation metadata is preserved; algebraic steps that omit the inverse-function reduction are not exposed.

Fourteen service cases passed under SymPy 1.13.3: principal equations, reversed operands, affine and polynomial arguments, impossible real arguments, open/closed bounds and rejection of symbolic bounds. Two API regressions are included for Actions. The local AF_UNIX restriction still prevents guarded API tests; product process isolation is unchanged.

EC-HI-06 and EC-HI-07 remain pending recertification at the new head until CI and the matrix confirm them. The other two known mathematical cases are EC-I-05 (atan addition branch) and ID-D-12 (convergent log-sine integral). Full result audit and visual recertification remain pending; B7 is open. No production deployment or merge.
