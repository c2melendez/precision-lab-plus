import copy
import unittest

from shard_mutmut import SHARDS, aggregate, owners, parse_results

NAMES = {
    "parsing": "app.services.parsing.x_parse__mutmut_1",
    "ast-responses": "app.services.ast_validator.x_validate__mutmut_1",
    "evaluate": "app.routers.evaluate.x__evaluate_impl__mutmut_1",
    "solve-a-g": "app.services.solve_service.x__absolute_value_steps__mutmut_1",
    "solve-h": "app.services.solve_service.x__hyperbolic_sine_one_real_result__mutmut_2",
    "solve-other-private": "app.services.solve_service.x__rational_domain_result__mutmut_1",
    "solve-public": "app.services.solve_service.x_solve_equation__mutmut_1",
}
SHA = "a" * 40

def records():
    return [{"schema": 1, "shard": s, "identity": {"checkout": SHA, "mutmut": "3.8.0", "config_sha256": "b"*64},
             "exit_code": 0, "patterns": list(SHARDS[s]),
             "inventory": {v: ("survived" if s == "parsing" else "killed") if s == k else "not checked" for k,v in NAMES.items()}}
            for s in SHARDS]

class ShardTests(unittest.TestCase):
    def test_partition_and_complete_union(self):
        for k, v in NAMES.items():
            self.assertEqual(owners(v), [k])
        self.assertEqual(owners("app.services.solve_service.x_Class__method__mutmut_1"), ["solve-public"])
        report = aggregate(records(), SHA)
        self.assertEqual(owners("app.schemas.responses.x_Result__method__mutmut_1"), ["ast-responses"])
        self.assertEqual(report["total"], 7)
        self.assertEqual(report["counts"]["killed"], 6)
        self.assertAlmostEqual(report["score_killed_percent"], 600/7)
        self.assertEqual(report["acceptance"], "REVIEW_REQUIRED")

    def test_bad_input_rejected(self):
        for mutate in [
            lambda rows: rows.pop(),
            lambda rows: rows[0].update(exit_code=124),
            lambda rows: rows[0]["identity"].update(checkout="c"*40),
            lambda rows: rows[0]["inventory"].pop(NAMES["ast-responses"]),
            lambda rows: rows[0]["inventory"].update({NAMES["parsing"]: "not checked"}),
            lambda rows: rows[0]["inventory"].update({NAMES["ast-responses"]: "killed"}),
            lambda rows: rows[0]["inventory"].update({NAMES["parsing"]: "suspicious"}),
            lambda rows: rows[0].update(patterns=["*"]),
            lambda rows: rows[0].update(shard="ast-responses"),
        ]:
            rows = records()
            mutate(rows)
            with self.assertRaises(ValueError):
                aggregate(rows, SHA)

    def test_complete_results_including_killed_and_unchecked(self):
        raw = f"    {NAMES['parsing']}: killed\n    {NAMES['ast-responses']}: not checked\n"
        self.assertEqual(parse_results(raw), {NAMES["parsing"]: "killed", NAMES["ast-responses"]: "not checked"})
        for bad in [raw + raw, "bad", "", raw + "app.other.x_a__mutmut_1: killed\n"]:
            with self.assertRaises(ValueError):
                parse_results(bad)

if __name__ == "__main__":
    unittest.main()
