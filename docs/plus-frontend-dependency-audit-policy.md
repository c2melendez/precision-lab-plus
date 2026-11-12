# Plus frontend dependency audit policy

**Status:** temporary, evidence-backed development-tooling exception  
**Reviewed:** 2026-11-06  
**Scope:** frontend build/test toolchain on the M2 feature branch

## CI enforcement

The frontend CI performs two separate audits:

1. `npm audit --json` produces a full npm v2 report. Its output is checked by `frontend/check-npm-audit-exceptions.mjs`; any incomplete report, new advisory, package, version, severity, lockfile location, or dependency edge fails CI.
2. `npm audit --omit=dev --package-lock-only` is a blocking production dependency audit. Any finding in the production dependency graph fails the frontend job.

The full report is uploaded as `plus-npm-audit` for 14 days, including when validation fails.

## Current exception

The retained report from 2026-11-06 HEAD `2960cee7a8cf633f61bc48dfd68a06105d0f3397` reports 11 affected package records: 2 LOW and 9 MODERATE. All affected lockfile entries are marked `dev: true`.

The findings collapse to three upstream advisories:

- [GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4): `deepmerge@4.3.1`, via `@rollup/plugin-node-resolve@16.0.3` → `workbox-build@7.4.1` → `vite-plugin-pwa@1.3.0`. The advisory identifies no patched deepmerge release as of this review.
- [GHSA-3g3m-2fjr-6pw4](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4): `glob@11.1.0` nested under Workbox. The advisory's patched version is `14.0.2`, outside the current Workbox `^11.0.1` range.
- [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249): `minimatch@10.2.6` under `@typescript-eslint/typescript-estree@8.67.0`. The advisory's patched version is `11.0.1`, outside the current `^10.2.2` range.

The other eight vulnerable-package records are transitive effects of these three advisory roots in the lockfile. The checker pins the exact 11 package names, versions, severity counts, lockfile nodes and transitive `via` relationships. This does not declare the development toolchain vulnerability-free: the packages execute during install/build/test workflows, and this exception must be revisited.

## Remediation deliberately not applied

Do not run `npm audit fix --force` blindly. npm proposes SemVer-major downgrades to `vite-plugin-pwa@1.1.0` and `@typescript-eslint/parser@6.15.0`. The affected ranges for `glob` and `minimatch` also require compatible parent-toolchain upgrades or tested dependency overrides. No package lockfile, PWA plugin, or TypeScript-ESLint versions were changed in this PR.

## Closure evidence

- Full audit report no longer contains the three advisories, or an upstream-compatible dependency upgrade removes the affected packages.
- The blocking production audit remains clean.
- Typecheck, unit/parity, production build, PWA offline and cross-browser tests pass after dependency changes.
