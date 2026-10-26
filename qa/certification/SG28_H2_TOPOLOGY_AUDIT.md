# SG28 / H2 — Deployment topology and global admission audit

Date: 2026-10-10
Repository: c2melendez/precision-lab-plus
Branch: qa/syntax-audit-in625-a1
Status: OPEN — observational audit, no production rollout authorized.

## Latest certified local concurrency baseline

- Technical SHA: `4654cd937b68b15e30c0047f4b75a6674bafba0b`.
- SG28 CI run 38074280892: 68 passed, 1 warning.
- Cumulative CI run 38074280914: 630 backend passed, 1 warning, 85.69% coverage; frontend job successful.
- H1d CI run 38074280878: 5 passed.
- In-process ASGI regression: `test_outer_tracker_disconnect_holds_reserved_slot_until_cleanup` passed.
- These results do not validate a physical network disconnect, multi-worker shared admission, or fleet-level quota.

## Source-level findings

Reviewed `backend/app/services/request_cancellation.py` from the working branch:
- `_MAX_ISOLATED_REQUESTS = max(1, min(int(os.getenv("SG28_MAX_ISOLATED_REQUESTS", "2")), 16))`.
- `_ADMISSION = threading.BoundedSemaphore(_MAX_ISOLATED_REQUESTS)` is allocated at module import time.
- `request_admission_lease()` fails closed when the *process-local* semaphore has no available permit.
- On cancellation, `run_for_request()` awaits coordinator cleanup before capacity is released or attaches a completion callback.

**Implication:** If N independent Python worker processes each initialize the module with capacity K, there can be up to N*K local admissions without a global quota; this is a theoretical upper bound under independent process admission, not a measured deployed configuration. Replicas add more independent admission pools. No deployment worker/replica counts have been established.

## Deployment verification boundary

Probed these repository paths on the active branch: `render.yaml`, `Dockerfile`, `backend/Dockerfile`, `Procfile`, `backend/Procfile`. All returned NOT_FOUND. This is *not* evidence that Render lacks configuration; service settings may be managed in its dashboard or another path.

Attempted to query connected Render services; API declined the request because no Render workspace had been selected. Per connector contract, workspace selection needs explicit user confirmation. **Do not assume a workspace, instance count, process count, start command or deployment environment variables.**

## Acceptance gates before H2 global certification

1. Read confirmed Render service topology: workspace/service ID, branch and deployment SHA, running instances, start command, Gunicorn/Uvicorn worker count, region, plan, autoscaling, concurrency config.
2. Verify `SG28_EVALUATE_ISOLATION` remains disabled in production; never toggle it in this audit.
3. Document whether fleet-wide admission is required. If yes, choose and test a central, lease-based admission coordinator that recovers permits after worker termination, timeouts and network partitions; add separate contention tests across processes.
4. Run external HTTP transport cancellation tests against a disposable local/staging target with isolation explicitly opted in, not production. Verify disconnect, K=1 rejection while cleanup is active, slot recovery, bounded process count and no leaked workers.
5. Record load-testing results and failure behavior per worker and replica. Do not substitute in-process ASGI tests for real socket evidence.
6. Re-run SG28, cumulative backend/frontend and H1d gates after code changes, linking exact SHA and run IDs.

## Safe next action

Resolve Render workspace through user-confirmed selection, perform read-only topology inspection, and then design a topology-matched test. If workspace access is not available, proceed with locally reproducible multiprocess tests but retain the deployment evidence as BLOCKED. Production isolation remains OFF; SG28/H2 stays OPEN.


## 2026-10-10 — Updated certified SG28/H2 evidence

- Plus cumulative run `38080591813`: backend 635 passed / 1 warning / 85.69% coverage; frontend 751 passed / 28 TODO. CI demonstrated loopback TCP disconnect + local K=1 lease held until mocked coordinator cleanup completes.
- Prior Plus run `38078685565`: distinct spawned Python processes independently hold their own local K=1 permits; that is evidence of **no global quota**.
- New Plus technical commit `c36608ab11e5264ed759af510721d67d0532b2c1`: added real spawned SymPy child cancellation under caller-held K=1 lease and subsequent reuse. **CI verification pending**.
- The pending test is ASGI-request-level (FakeRequest), not a physical TCP disconnect. No claim of integrated real socket + real isolated child cancellation yet.
- Global admission and actual Render deployment topology remain unverified. Experimental production isolation stays disabled; H2 remains OPEN.


## 2026-10-10 — H2 global quota design decision gate (NOT implemented)

Current latest verified Plus technical SHA `08f70c1b7aa6f894f5595b95afcd2a13a9001725`:
- Cumulative run `38084223803`: 637 backend passed, 1 warning, coverage 85.69%; frontend 751 passed, 28 TODO.
- Real TCP socket close + spawned SymPy computation + local K=1 cancellation/recovery PASSED.
- The process-local semaphore cannot be claimed as a fleet-wide capacity bound.

Proposed distributed admission contract, conditional on confirmed Render topology:
1. Separate `local_capacity` from `global_capacity`. Global quota applies across every process and replica; local semaphore remains a secondary safety ceiling.
2. Define a central atomic grant with an opaque lease token, owner identifier, bounded expiration, and fencing generation. Grant MUST fail closed when central coordination is unavailable, unless an explicitly approved degraded mode is specified.
3. A lease renews while its computation is active. The lease MUST NOT be released while the child coordinator is still running or being reaped. Expiration requires an explicit orphan-cleanup/fencing policy so a stale worker cannot continue alongside a newly admitted worker.
4. Releasing or renewing someone else's token MUST fail. Duplicate release is idempotent; cross-worker retry must not create a second reservation.
5. Counters and audit events include attempted/admitted/denied, active leases, expired leases, failed renewals, reaped worker outcomes, and lease ownership. Do not log credentials or computation input.
6. Acceptance tests: two separate interpreters and two independent service replicas competing at K=1; load at K and K+1; crash and expired lease recovery; renewal and network partition; stale-token fencing; double-release; restart; real TCP disconnect with an actual child.
7. Production guard: leave `SG28_EVALUATE_ISOLATION` disabled until design, failure modes, CI, staging and verified Render deployment topology are approved. This is NOT authorization to deploy a new coordinator.

A concurrent shared-semaphore characterization test was drafted but its repository publication was blocked by tool safety controls. Therefore there is **no new global-quota test commit or green CI evidence** from this design step. H2 remains OPEN.
