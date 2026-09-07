"""Tests for experimental integrity; no model or network calls."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("compare_memory", ROOT / "scripts/compare_memory.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bundle = self.root / "bundle"
        self.output = self.root / "run"
        self.prep = Namespace(suite=ROOT / "evaluation/example/suite.json", out=self.bundle,
                              seed=17, repeats=2, max_context_bytes=24000)

    def prepare(self):
        m.prepare(self.prep)
        return m.load_bundle(self.bundle)

    def run_args(self, reader="smoke"):
        return Namespace(bundle=self.bundle, out=self.output, reader=reader,
                         model="test-model", environment_note="mock test environment",
                         timeout=1, effort="medium")

    def grade(self):
        grades = m.read_json(self.output / "grading.json")
        for g in grades:
            g["score"] = int(g["question_id"] == "missing-budget" and g["status"] == "ok")
            g["rationale"] = "Abstention meets the missing-budget rubric only."
        m.write_json(self.output / "grading.json", grades)
        return Namespace(run=self.output, grades=self.output / "grading.json")

    def test_pairing_no_rubric_leak_and_immutability(self):
        bundle = self.prepare()
        for q in bundle["questions"]:
            jobs = [j for j in bundle["jobs"] if j["question_id"] == q["id"]]
            self.assertEqual([j["arm"] for j in jobs[:2]],
                             [j["arm"] for j in jobs[2:]][::-1])
            for j in jobs:
                self.assertEqual(set(json.loads(j["prompt"])), {"question", "memory_evidence"})
                self.assertNotIn(q["rubric"], j["prompt"])
        with self.assertRaises(FileExistsError):
            m.prepare(self.prep)
        with (self.bundle / "bundle.json").open("a") as f:
            f.write(" ")
        with self.assertRaisesRegex(ValueError, "changed"):
            m.load_bundle(self.bundle)

    def test_no_silent_truncation(self):
        self.prep.max_context_bytes = 1
        with self.assertRaisesRegex(ValueError, "exceeds byte cap"):
            m.prepare(self.prep)
        self.assertFalse(self.bundle.exists())

    def test_offline_end_to_end_and_grading_completeness(self):
        self.prepare()
        m.run(self.run_args())
        args = Namespace(run=self.output, grades=self.output / "grading.json")
        with self.assertRaisesRegex(ValueError, "integer score"):
            m.report(args)
        args = self.grade()
        grades = m.read_json(args.grades)
        m.write_json(args.grades, grades[:-1])
        with self.assertRaisesRegex(ValueError, "every answer"):
            m.report(args)
        m.write_json(args.grades, grades)
        m.report(args)
        text = (self.output / "report.md").read_text()
        self.assertIn("File: 2/4; Lambo: 2/4", text)
        self.assertIn("NOT EMPIRICAL EVIDENCE", text)
        with self.assertRaises(FileExistsError):
            m.report(args)

    def test_timeout_and_process_errors_retained(self):
        self.prepare()
        failure = subprocess.CompletedProcess([], 1, "", "mock failure")
        with patch.object(m.shutil, "which", return_value="/mock/claude"), \
             patch.object(m.subprocess, "check_output", return_value="mock version"), \
             patch.object(m.subprocess, "run", side_effect=[subprocess.TimeoutExpired([], 1), failure] * 4):
            m.run(self.run_args("claude"))
        results = m.read_json(self.output / "results.json")
        self.assertEqual(len(results), 8)
        self.assertEqual({r["status"] for r in results}, {"timeout", "process_error"})
        args = self.grade()
        grades = m.read_json(args.grades)
        grades[0]["score"] = 1
        m.write_json(args.grades, grades)
        with self.assertRaisesRegex(ValueError, "must score zero"):
            m.report(args)

    def test_harness_change_between_prepare_and_run_rejected(self):
        self.prepare()
        m.run(self.run_args())
        args = self.grade()
        metadata = m.read_json(self.output / "run.json")
        metadata["harness_sha256"] = "0" * 64
        m.write_json(self.output / "run.json", metadata)
        with self.assertRaisesRegex(ValueError, "harness changed"):
            m.report(args)

    def test_missing_arm_reported_by_name(self):
        suite = m.read_json(self.prep.suite)
        del suite["questions"][0]["contexts"]["lambo"]
        self.prep.suite = self.root / "partial-suite.json"
        m.write_json(self.prep.suite, suite)
        with self.assertRaisesRegex(ValueError, "current-decision: contexts must define both arms"):
            m.prepare(self.prep)

    def test_answer_edits_rejected(self):
        self.prepare()
        m.run(self.run_args())
        args = self.grade()
        grades = m.read_json(args.grades)
        grades[0]["answer"] = "Rewritten after grading"
        m.write_json(args.grades, grades)
        with self.assertRaisesRegex(ValueError, "only scores and rationales"):
            m.report(args)


if __name__ == "__main__":
    unittest.main()
