#!/usr/bin/env python3
"""Read-only, per-job campaign selection. Never dispatches or cancels runs.

Security is freshly executed when selected. Mutation WAIT/REVIEW/DIAGNOSE do
not produce PASS; REUSE requires an explicit log review and real job steps.
PR/main workflows retain their full default selection outside this QA router.
"""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from ci_guard import GitHub

PROFILES = {
    "security_frontend": ("s25-security.yml", "frontend-audit", ["frontend/package*.json", "frontend/.npmrc"], ["Block high/critical npm vulnerabilities"]),
    "security_backend": ("s25-security.yml", "backend-security", ["backend/*"], ["pip-audit runtime dependencies", "Bandit medium/high gate", "Security and CORS regressions"]),
    "mutation_frontend": ("s19-mutation.yml", "plus-frontend-stryker", ["frontend/*", "qa/certification/*.jsonl"], ["Run Plus frontend mutation baseline"]),
    "mutation_backend": ("s19-mutation.yml", "plus-backend-mutmut", ["backend/*", "qa/certification/*.jsonl"], ["Verify mutation-specific backend tests", "Run mutation baseline on critical backend surfaces"]),
    # The job contract contains the immutable external repo/ref and pinned tools.
    # Local Lite HEAD and Plus backend files are not inputs to that reference job.
    "mutation_lite": ("s19-mutation.yml", "lite-frontend-stryker", ["qa/s19/stryker-lite.config.json"], ["Run Lite frontend mutation baseline"]),
}


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def job_contract(workflow, job):
    match = re.search(r"^  " + re.escape(job) + r":\n(.*?)(?=^  [A-Za-z0-9_-]+:|\Z)", workflow, re.M | re.S)
    if not match:
        raise ValueError("Missing job contract: " + job)
    # Ignore only the top-level routing/needs added by this change. Every step,
    # tool version, checkout ref, command, environment and timeout stays hashed.
    return "\n".join(line for line in match[0].splitlines()
                     if not line.startswith(("    if:", "    needs:"))) .strip()


def fingerprint(sha, profile):
    workflow, job, patterns, steps = PROFILES[profile]
    contract = job_contract(git("show", f"{sha}:.github/workflows/{workflow}"), job)
    entries = []
    for entry in subprocess.check_output(["git", "ls-tree", "-rz", sha], text=True).split("\0"):
        if entry:
            meta, path = entry.split("\t", 1)
            if matches(path, patterns):
                entries.append([path, meta])
    data = {"version": 1, "profile": profile, "scope": patterns, "steps": steps, "contract": contract, "inputs": sorted(entries)}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def affected(paths, profile):
    workflow, _, patterns, _ = PROFILES[profile]
    # E2E/report artifacts are not read by the frontend mutation test runner.
    return any(matches(path, patterns) and not path.startswith(("frontend/e2e/", "frontend/e2e-cross-browser/", "frontend/reports/"))
               for path in paths)


def mutation_decision(candidates, reviews, profile, current_fingerprint):
    """Candidates must already match the input fingerprint; newest wins."""
    _, job_name, _, required = PROFILES[profile]
    candidates = sorted(candidates, key=lambda r: (r["created_at"], r.get("run_attempt", 1), r["id"]), reverse=True)
    for run in candidates:
        jobs = [job for job in run["jobs"] if job["name"].split(" / ")[-1] == job_name]
        if len(jobs) != 1:
            if run.get("status") != "completed":
                return "WAIT", run["id"], None
            if len(jobs) > 1:
                return "REVIEW", run["id"], None
            continue
        job = jobs[0]
        if job.get("conclusion") == "skipped":
            continue
        if job["status"] != "completed":
            return "WAIT", run["id"], job["id"]
        if job["conclusion"] != "success":
            return "DIAGNOSE", run["id"], job["id"]
        steps = [[step for step in job.get("steps", []) if step["name"] == name] for name in required]
        if not all(len(matches) == 1 and matches[0].get("status") == "completed" and matches[0].get("conclusion") == "success" for matches in steps):
            continue  # A successful no-op is not evidence; resolve its origin.
        reviewed = any(review.get("profile") == profile and review.get("run_id") == run["id"]
                       and review.get("job_id") == job["id"] and review.get("input_fingerprint") == current_fingerprint
                       and review.get("logs_reviewed") is True and review.get("mutations_executed") is True
                       for review in reviews)
        return ("REUSE" if reviewed else "REVIEW"), run["id"], job["id"]
    return "RUN", None, None


def select(paths, event, reason=""):
    if event == "workflow_dispatch":
        if not reason.strip():
            raise ValueError("Manual revalidation requires a nonempty reason")
        return {name: "RUN" for name in PROFILES}
    return {name: "CHECK" if affected(paths, name) else "NOT_SELECTED" for name in PROFILES}


def history(api, current_run):
    runs = []
    for page in range(1, 4):
        payload = api.get(f"/actions/workflows/certification-dependency-gates.yml/runs?branch=qa/syntax-audit-in625-a1&per_page=100&page={page}")
        chunk = payload["workflow_runs"]
        runs.extend(run for run in chunk if str(run["id"]) != str(current_run)
                    and run.get("event") in ("push", "workflow_dispatch"))
        if len(chunk) < 100:
            return runs
    raise ValueError("Incomplete campaign history")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", help="JSON array for offline routing inspection")
    parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_NAME", "push"))
    parser.add_argument("--reason", default=os.environ.get("REVALIDATION_REASON", ""))
    parser.add_argument("--fingerprint", choices=PROFILES)
    parser.add_argument("--sha", default="HEAD")
    args = parser.parse_args()
    if args.fingerprint:
        print(fingerprint(args.sha, args.fingerprint))
        return
    uncertain, before = False, None
    if args.paths:
        paths = json.loads(Path(args.paths).read_text())
    else:
        try:
            event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
            before = event["before"]
            if not re.fullmatch(r"[0-9a-f]{40}", before) or set(before) == {"0"}:
                raise ValueError("No complete push baseline")
            paths = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", before, "HEAD"], text=True).splitlines()
        except Exception:
            paths, uncertain = [], True
    decisions = select(paths, args.event, args.reason)
    if args.event == "workflow_dispatch":
        print(json.dumps({"revalidation_reason": args.reason}))
    if before and args.event != "workflow_dispatch":
        for profile, (workflow, job, _, _) in PROFILES.items():
            path = ".github/workflows/" + workflow
            if path in paths:
                try:
                    previous = job_contract(git("show", f"{before}:{path}"), job)
                    current = job_contract(Path(path).read_text(), job)
                    if previous != current:
                        decisions[profile] = "CHECK"
                except Exception:
                    decisions[profile] = "CHECK"
    if uncertain and args.event != "workflow_dispatch":
        decisions = {name: "CHECK" for name in PROFILES}  # Missing diff runs checks safely.
    result = {}
    api, runs = None, None
    reviews = json.loads(Path("qa/certification/continuity.json").read_text()).get("campaign_evidence_reviews", [])
    for profile, decision in decisions.items():
        item = {"decision": decision, "run": decision == "RUN", "input_fingerprint": fingerprint("HEAD", profile)}
        if decision == "CHECK":
            if profile.startswith("security_"):
                item.update(decision="RUN", run=True, reason="Fresh selected security checks; no advisory reuse")
            else:
                try:
                    if api is None:
                        api = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])
                        runs = history(api, os.environ.get("GITHUB_RUN_ID"))
                    candidates = []
                    for run in runs:
                        if fingerprint(run["head_sha"], profile) == item["input_fingerprint"]:
                            candidates.append({**run, "jobs": api.jobs(run["id"], run["run_attempt"])})
                    status, origin, job = mutation_decision(candidates, reviews, profile, item["input_fingerprint"])
                    item.update(decision=status, run=status == "RUN", evidence_run_id=origin, evidence_job_id=job)
                except Exception as exc:
                    item.update(decision="RUN", run=True, reason="Incomplete evidence lookup: " + type(exc).__name__)
        result[profile] = item
    print(json.dumps({"paths": paths, "profiles": result}, indent=2))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            for profile, item in result.items():
                output.write(f"{profile}={str(item['run']).lower()}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
            summary.write("\n## Per-job campaign selection\n\n|Profile|Decision|Evidence origin|\n|---|---|---|\n")
            for profile, item in result.items():
                origin = item.get("evidence_run_id")
                link = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{origin}" if origin else "—"
                summary.write(f"|{profile}|{item['decision']}|{link}|\n")
            summary.write("\nNOT_SELECTED/WAIT/REVIEW/DIAGNOSE and skipped jobs are not PASS. REUSE is prior evidence, not new execution. Required certification gates remain OPEN until their evidence is complete.\n")


if __name__ == "__main__":
    main()
