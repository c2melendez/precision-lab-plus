import copy
import json
from pathlib import Path
import subprocess
import unittest
from unittest import mock
import tempfile
import os

import campaign_scope as scope

ROOT = Path(__file__).resolve().parents[2]


class RoutingTests(unittest.TestCase):
    def test_backend_validation_change_does_not_select_frontend_or_pinned_lite(self):
        result = scope.select(["backend/app/core/exception_handlers.py"], "push")
        self.assertEqual(result["security_backend"], "CHECK")
        self.assertEqual(result["mutation_backend"], "CHECK")
        for name in ("security_frontend", "mutation_frontend", "mutation_lite"):
            self.assertEqual(result[name], "NOT_SELECTED")

    def test_frontend_dependencies_select_only_frontend(self):
        result = scope.select(["frontend/package-lock.json"], "push")
        self.assertEqual(result["security_frontend"], "CHECK")
        self.assertEqual(result["mutation_frontend"], "CHECK")
        self.assertEqual(result["mutation_lite"], "NOT_SELECTED")
        self.assertEqual(result["security_backend"], "NOT_SELECTED")

    def test_reference_harness_change_selects_lite(self):
        result = scope.select(["qa/s19/stryker-lite.config.json"], "push")
        self.assertEqual([name for name, value in result.items() if value == "CHECK"], ["mutation_lite"])

    def test_orchestration_and_docs_do_not_launch_a_campaign(self):
        paths = ["scripts/certification/campaign_scope.py", ".github/workflows/s19-mutation.yml",
                 ".github/workflows/s25-security.yml", ".github/workflows/certification-dependency-gates.yml",
                 "qa/certification/continuity.json", "qa/certification/CURRENT_STATE.md"]
        self.assertEqual(set(scope.select(paths, "push").values()), {"NOT_SELECTED"})

    def test_e2e_only_does_not_select_mutation(self):
        self.assertFalse(scope.affected(["frontend/e2e/in625-syntax-native.spec.ts"], "mutation_frontend"))

    def test_manual_always_revalidates_every_component_with_reason(self):
        self.assertEqual(set(scope.select([], "workflow_dispatch", "fresh review").values()), {"RUN"})
        with self.assertRaises(ValueError):
            scope.select([], "workflow_dispatch", "  ")

    def test_actual_job_contract_preserves_all_evidence_commands_and_pinned_source(self):
        for profile, (workflow, job, _, steps) in scope.PROFILES.items():
            current = (ROOT / ".github/workflows" / workflow).read_text()
            old = subprocess.check_output(["git", "show", f"HEAD:.github/workflows/{workflow}"], cwd=ROOT, text=True)
            self.assertEqual(scope.job_contract(current, job), scope.job_contract(old, job), profile)
            for step in steps:
                self.assertIn(step, scope.job_contract(current, job))
        lite = scope.job_contract((ROOT / ".github/workflows/s19-mutation.yml").read_text(), "lite-frontend-stryker")
        self.assertIn("6cbec7645b73ad18875d4472182c704eb35228b0", lite)
        self.assertIn("@stryker-mutator/core@10.0.0", lite)

    def test_source_ref_or_command_change_is_not_discarded_as_routing(self):
        value = "jobs:\n  sample:\n    if: inputs.run\n    needs: validate-request\n    steps:\n      - run: original\n"
        self.assertNotEqual(scope.job_contract(value, "sample"), scope.job_contract(value.replace("original", "changed"), "sample"))
        self.assertEqual(scope.job_contract(value, "sample"), scope.job_contract(value.replace("if: inputs.run", "if: false"), "sample"))

    def test_pr_and_main_triggers_and_default_full_selection_remain(self):
        security = (ROOT / ".github/workflows/s25-security.yml").read_text()
        mutation = (ROOT / ".github/workflows/s19-mutation.yml").read_text()
        for text in (security, mutation):
            self.assertIn("  pull_request:", text)
            self.assertIn("default: true", text)
            self.assertIn("github.event_name == 'pull_request'", text)
            self.assertIn("github.event_name == 'workflow_dispatch'", text)
        self.assertIn("branches: [main, master]", security)
        self.assertIn("github.ref == 'refs/heads/main'", security)
        self.assertIn("github.ref == 'refs/heads/master'", security)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.profile, self.fp = "mutation_lite", "input-hash"
        self.job = {"name": "mutation / lite-frontend-stryker", "id": 7,
                    "status": "completed", "conclusion": "success", "steps": [
                        {"name": "Run Lite frontend mutation baseline", "status": "completed", "conclusion": "success"}]}
        self.run = {"id": 2, "created_at": "2026-10-16T00:00:00Z", "run_attempt": 1,
                    "status": "completed", "conclusion": "failure", "jobs": [self.job]}
        self.review = {"profile": self.profile, "run_id": 2, "job_id": 7,
                       "input_fingerprint": self.fp, "logs_reviewed": True, "mutations_executed": True}

    def decide(self, runs=None, reviews=None):
        return scope.mutation_decision(runs or [self.run], reviews if reviews is not None else [self.review], self.profile, self.fp)

    def test_reviewed_real_job_can_be_reused_despite_unrelated_parent_security_failure(self):
        self.assertEqual(self.decide(), ("REUSE", 2, 7))

    def test_color_without_explicit_log_and_mutation_review_is_not_reuse(self):
        self.assertEqual(self.decide(reviews=[])[0], "REVIEW")
        for key in ("logs_reviewed", "mutations_executed"):
            review = {**self.review, key: False}
            self.assertEqual(self.decide(reviews=[review])[0], "REVIEW")

    def test_changed_fingerprint_or_acceptance_inputs_invalidate_review(self):
        review = {**self.review, "input_fingerprint": "other"}
        self.assertEqual(self.decide(reviews=[review])[0], "REVIEW")

    def test_running_equivalent_waits_without_starting_another_campaign(self):
        self.job.update(status="in_progress", conclusion=None)
        self.assertEqual(self.decide()[0], "WAIT")

    def test_not_yet_created_job_in_running_workflow_also_waits(self):
        self.run.update(status="queued", jobs=[])
        self.assertEqual(self.decide()[0], "WAIT")

    def test_new_failure_or_cancellation_supersedes_old_green(self):
        newer = copy.deepcopy(self.run)
        newer.update(id=3, created_at="2026-10-17T00:00:00Z")
        for status in ("failure", "cancelled", "timed_out"):
            newer["jobs"][0]["conclusion"] = status
            self.assertEqual(self.decide([self.run, newer])[0], "DIAGNOSE")

    def test_skipped_success_is_not_fabricated_evidence(self):
        self.job["steps"][0]["conclusion"] = "skipped"
        self.assertEqual(self.decide()[0], "RUN")
        self.job["conclusion"] = "skipped"
        self.assertEqual(self.decide()[0], "RUN")

    def test_skip_chain_can_resolve_reviewed_origin_but_cannot_cross_failure(self):
        newer = copy.deepcopy(self.run)
        newer.update(id=3, created_at="2026-10-17T00:00:00Z")
        newer["jobs"][0]["conclusion"] = "skipped"
        self.assertEqual(self.decide([self.run, newer])[0], "REUSE")

    def test_duplicate_jobs_are_review_not_pass(self):
        self.run["jobs"] *= 2
        self.assertEqual(self.decide()[0], "REVIEW")

    def test_duplicate_required_steps_are_not_evidence(self):
        self.job["steps"] *= 2
        self.assertEqual(self.decide()[0], "RUN")


class MainTests(unittest.TestCase):
    def execute(self, paths, event="push", reason=""):
        with tempfile.TemporaryDirectory() as directory:
            paths_file = Path(directory) / "paths.json"
            paths_file.write_text(json.dumps(paths))
            output_file = Path(directory) / "output"
            argv = ["campaign_scope.py", "--paths", str(paths_file), "--event", event, "--reason", reason]
            with mock.patch("sys.argv", argv), mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output_file), "GITHUB_REPOSITORY": "owner/repo"}), \
                    mock.patch.object(scope, "fingerprint", return_value="fp"), \
                    mock.patch.object(scope, "GitHub", side_effect=OSError("offline")), mock.patch("builtins.print"):
                scope.main()
            return output_file.read_text()

    def test_missing_evidence_lookup_runs_only_the_affected_component(self):
        output = self.execute(["backend/app/core/exception_handlers.py"])
        self.assertIn("security_backend=true", output)
        self.assertIn("mutation_backend=true", output)
        self.assertIn("mutation_lite=false", output)
        self.assertIn("mutation_frontend=false", output)

    def test_orchestration_commit_outputs_all_false_without_api_access(self):
        output = self.execute(["scripts/certification/campaign_scope.py"])
        self.assertEqual(output.count("=false"), 5)

    def test_manual_outputs_every_component_true(self):
        self.assertEqual(self.execute([], "workflow_dispatch", "explicit review").count("=true"), 5)


if __name__ == "__main__":
    unittest.main()
