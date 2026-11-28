"""S19 split execution; same five module filters and pinned mutmut, no new score floor."""
import argparse
import fnmatch
import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
from pathlib import Path

MODULES = ("app.services.parsing", "app.services.ast_validator", "app.services.solve_service",
           "app.routers.evaluate", "app.schemas.responses")
SOLVE = MODULES[2] + "."
SHARDS = {
    "parsing": (MODULES[0] + "*",),
    "ast": (MODULES[1] + "*",),
    "evaluate": (MODULES[3] + "*",),
    "responses": (MODULES[4] + "*",),
    "solve-a-g": (SOLVE + "x__[a-g]*",),
    "solve-h": (SOLVE + "x__h*",),
    "solve-other-private": (SOLVE + "x__[!a-h]*",),
    "solve-public": (SOLVE + "x_[!_]*", SOLVE + "[!x]*", SOLVE + "x[!_]*"),
}
STATUSES = {"killed", "survived", "no tests", "timeout", "not checked",
            "skipped", "suspicious", "check was interrupted by user", "segfault", "caught by type check"}
TERMINAL = {"killed", "survived", "no tests", "timeout", "caught by type check"}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def command(*args):
    return subprocess.check_output(args, text=True).strip()

def selected(shard, name):
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in SHARDS[shard])

def owners(name):
    return [s for s in SHARDS if selected(s, name)]

def parse_results(text):
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        m = re.fullmatch(r"\s*(\S+): ([a-z ]+)\s*", line)
        require(m is not None, "Unexpected results line: " + line)
        name, status = m.groups()
        require(name not in out and status in STATUSES, "Invalid or repeated mutant: " + name)
        require(any(fnmatch.fnmatchcase(name, p + "*") for p in MODULES), "Outside original full scope: " + name)
        require(len(owners(name)) == 1, "Partition gap or overlap: " + name)
        out[name] = status
    require(bool(out), "No mutant inventory")
    return out

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def identity():
    return {"checkout": command("git", "rev-parse", "HEAD"),
            "python": platform.python_version(), "mutmut": importlib.metadata.version("mutmut"),
            "config_sha256": sha("pyproject.toml"),
            "requirements_sha256": sha("requirements.txt"),
            "qa_requirements_sha256": sha("requirements-qa.txt"),
            "environment_sha256": hashlib.sha256("\n".join(sorted(command("python", "-m", "pip", "freeze").splitlines())).encode()).hexdigest()}

def run_shard(shard, output):
    output.mkdir(parents=True, exist_ok=True)
    require(not Path("mutants").exists(), "Fresh checkout required; no stale mutmut state")
    provenance = identity()
    require(provenance["mutmut"] == "3.8.0", "Tool version drift")
    patterns = SHARDS[shard]
    # Inner deadline reserves time for results and artifact upload even when interrupted.
    rc = subprocess.call(["timeout", "--signal=INT", "--kill-after=30s", "150m",
                          "mutmut", "run", *patterns])
    (output / "mutmut-exit-code.txt").write_text(str(rc) + "\n")
    raw = command("mutmut", "results", "--all")
    (output / "mutmut-results-all.txt").write_text(raw + "\n")
    inventory = parse_results(raw)
    mine = {k: v for k, v in inventory.items() if selected(shard, k)}
    require(bool(mine), "Empty shard")
    status = {"schema": 1, "shard": shard, "identity": provenance, "exit_code": rc,
              "inventory": inventory, "patterns": list(patterns)}
    (output / "shard.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print("S19_SHARD " + json.dumps({"shard": shard, "selected": len(mine), "exit_code": rc,
                                   "counts": {s: list(mine.values()).count(s) for s in sorted(STATUSES)}}))
    require(rc == 0 and set(mine.values()) <= TERMINAL, "Incomplete shard; retain evidence, do not pass")
    require(all(v == "not checked" for k, v in inventory.items() if k not in mine), "Unexpected out-of-shard execution")
    # Preserve the historical non-killed listing. Full per-mutant data is above.
    (output / "mutmut-results.txt").write_text("".join(f"{k}: {v}\n" for k, v in sorted(mine.items()) if v != "killed"))

def aggregate(records, checkout):
    require(len(records) == len(SHARDS), "Missing or extra shards")
    by_shard = {r["shard"]: r for r in records}
    require(set(by_shard) == set(SHARDS), "Duplicate or missing shard")
    first = records[0]
    identity = first["identity"]
    require(identity["checkout"] == checkout and identity["mutmut"] == "3.8.0", "Wrong checkout/tool")
    universe = set(first["inventory"])
    require(bool(universe), "Empty mutation universe")
    combined = {}
    for name, row in by_shard.items():
        require(row["schema"] == 1 and row["identity"] == identity and row["exit_code"] == 0, "Stale/incomplete shard: " + name)
        require(row["patterns"] == list(SHARDS[name]), "Wrong shard filters")
        inventory = row["inventory"]
        require(set(inventory) == universe, "Inventory drift between shards")
        require(all(v in STATUSES for v in inventory.values()), "Unknown status")
        own = {k: v for k, v in inventory.items() if selected(name, k)}
        require(bool(own) and set(own.values()) <= TERMINAL, "Empty or incomplete selected shard")
        require(all(v == "not checked" for k, v in inventory.items() if k not in own), "Out-of-shard execution")
        require(not set(combined).intersection(own), "Overlapping selected mutant")
        combined.update(own)
    require(set(combined) == universe, "Coverage gap")
    require(all(len(owners(k)) == 1 and any(fnmatch.fnmatchcase(k, p+"*") for p in MODULES) for k in universe), "Partition not exact")
    counts = {s: list(combined.values()).count(s) for s in sorted(STATUSES)}
    return {"schema": 1, "status": "EXECUTION_COMPLETE_NOT_ACCEPTANCE", "identity": identity,
            "total": len(combined), "counts": counts, "score_killed_percent": 100 * counts["killed"] / len(combined),
            "mutants": combined, "acceptance": "REVIEW_REQUIRED", "baseline_comparable": None}

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="action", required=True)
    a = sub.add_parser("run")
    a.add_argument("shard", choices=SHARDS)
    a.add_argument("output", type=Path)
    b = sub.add_parser("aggregate")
    b.add_argument("directory", type=Path)
    b.add_argument("output", type=Path)
    args = p.parse_args()
    if args.action == "run":
        run_shard(args.shard, args.output)
    else:
        rows = [json.loads(f.read_text()) for f in sorted(args.directory.rglob("shard.json"))]
        report = aggregate(rows, command("git", "rev-parse", "HEAD"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("S19_AGGREGATE " + json.dumps({k: v for k, v in report.items() if k != "mutants"}))

if __name__ == "__main__":
    main()
