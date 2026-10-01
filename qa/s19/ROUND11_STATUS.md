# B7 round 11 — 2026-10-01

## Verified preceding head

Head `0e931f40ebc8d586a53d4d0f85f1b3d7c09a125c`: all ten workflows passed, including S19, S21 and E2E. CI run 36906973590 passed 532 backend tests and 457 frontend tests; backend coverage rounded to 77% (unchanged 75% gate).

Matrix 36906966436: **312 RESULT / 11 ERROR / 1 SKIP_CONTEXT**, 324 rows. EC-HI-06 output is exactly 0. EC-HI-07 reports no real solution. Both are recertified through the actual keyboard/parser/API chain. The wording “El sistema no tiene solución” for this single equation is a presentation item for the remaining audit.

## Remaining two known mathematical corrections submitted

### EC-I-05 — affine two-atan sum

Use tangent addition only when both arguments are real affine expressions in the solved variable and the target is a known real angle strictly inside (-pi/2,pi/2). The algebraic reduction is accompanied by the exact condition `1-u*v>0`, placing the original atan sum in the same injective tangent branch. This excludes the negative quadratic root of `atan(x)+atan(2*x)=pi/4`; the accepted root is `(sqrt(17)-3)/4`.

Unresolved branch signs produce a controlled unsupported result, rather than silently discarding an uncertain root. Other atan forms/target ranges and complex requests retain the generic path. Original equation metadata is preserved, and incomplete algebraic-only steps are suppressed.

Thirteen service cases passed: operand/term order, negative and zero targets, translated arguments, rejection of the extraneous root, closed/open and disjoint requested bounds, scope rejection and degree-mode preservation. One API regression is committed.

### ID-D-12 — convergent log-sine definite integral

The actual matrix input is **ln(sin(x))**, with natural logarithm. Calculator `log` is base 10 and must not be confused with it.

For I=int_0^(pi/2) ln(sin(x)) dx, sin(x)/x -> 1 proves integrability at zero. Reflection x -> pi/2-x identifies the log-cosine integral with I; the double-angle substitution gives 2I=I-(pi/2)ln(2), hence I=-(pi/2)ln(2).

Apply this exact identity only to the specified bounds (including reversal) and finite real constant multiples of the log-sine integrand. Other intervals continue through existing convergence/domain checks. Linearity correctly evaluates the calculator's base-10 log using its factor 1/ln(10).

A definite value can be known without an elementary primitive. The service's antiderivative is optional for this result, and the API emits null primitive metadata instead of a fabricated or unevaluated expression. Existing indefinite calculations retain their primitives and +C. The response schema already allows null primitive fields. Definite preview retains the original curve and bounded area.

Nine service cases passed, including exact endpoints, variable names, reversal, native fraction bounds, independent 40-digit quadrature (error below 1e-38), log-base distinction, linearity and retained divergence rejection for reciprocal sine. Two API regressions are committed.

Combined local run of the four latest regression files: **48 service cases passed**, six guarded API cases deferred to Actions due to local AF_UNIX restrictions. No isolation bypass was added.

## Next required evidence

Confirm EC-I-05 and ID-D-12 at the new head in CI and the full diagnostic matrix. Only after that can all five previously known defects be considered recertified. RESULT counts alone do not complete the independent mathematical audit or visual recertification of Plus/Lite. B7 remains open. No production merge or deployment.
