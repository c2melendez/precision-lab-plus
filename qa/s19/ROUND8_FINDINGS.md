# B7 round 8 — mutation harness correction, 2026-10-01

QA changes only; B7 remains open. Global mutation threshold stays 15.3 and all eight original source files remain in scope.

## Verified findings

- Frontend suite: 457 tests passed locally; TypeScript passed.
- Added actual store reload contracts for persisted histories and recent keys, malformed storage, storage failures, caps and endpoint reuse. Removed an older corrupt-storage assertion that did not reload the store. Added fraction and system boundary contracts.
- S21 run 36900166944 at commit 0516c12: Plus 4/4 and certified Lite 4/4 passed on Firefox/WebKit. Logs confirm package downloads from `https://archive.ubuntu.com/ubuntu`. The mirror repair now handles legacy sources, deb822 sources and mirror-list indirection, with HTTP and HTTPS inputs.
- Stryker 10.0.0 reconstructs nested test names with spaces. Vitest 5 uses its native `fullTestName` with ` > ` separators for test filtering. Consequently, per-test mutation runs could report survivors with `testsCompleted: 0`. The prior global 13.59% score is not a trustworthy measure of test strength.
- The compatibility patch uses native `fullTestName` in both coverage setup and runner result helpers, retains the legacy fallback, requires the reviewed runner version and verifies exact installed source before changing it. It modifies only installed QA tooling. Lite versions before Vitest 5 are left unchanged.
- The aggregate gate now rejects a survivor explicitly reporting zero executed tests. Such a survivor cannot count as a completed mutation evaluation.
- Seven harness tests passed, including helper name matching, idempotence, unknown-version rejection and zero-test survivor rejection.

## Local controlled mutation experiment

Same 32 persistence contract tests, same 165 mutants, same two production source files. This experiment does not substitute for the full eight-file global gate.

| Runner | Detected | Survived | Local score |
|---|---:|---:|---:|
| Unpatched Stryker 10 / Vitest 5 | 10 | 155 | 6.06% |
| Native-name compatibility patch | 142 | 23 | 86.06% |

With the patch: History 52/65 detected (80%); RecentKeys 90/100 (90%). No survivor reports zero tests. No timeout or runtime/compile error was counted in this experiment.

## Pending

Re-run the complete global mutation baseline with the patch; do not declare S19 passed from the local two-file score. Five known mathematical cases, full result audit and visual recertification remain pending. No production merge or deployment was performed.
