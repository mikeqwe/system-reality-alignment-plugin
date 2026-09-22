"""Verify fixture/oracle consistency, NOT model behavior or plugin benefit."""
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
from check_projection import load, suite


def reference_apply(state, event):
    if not isinstance(event, dict) or set(event) != {"subject", "revision", "status"}:
        raise ValueError("shape")
    subject, revision, status = event["subject"], event["revision"], event["status"]
    if not isinstance(subject, str) or not subject or type(revision) is not int or revision < 1:
        raise ValueError("identity/version")
    if not isinstance(status, str) or status not in {"pending", "active", "failed"}:
        raise ValueError("status")
    old = state.get(subject)
    if old and old["revision"] == revision and old["status"] != status:
        raise ValueError("conflict")
    if old is None or revision > old["revision"]:
        state[subject] = {"revision": revision, "status": status}


class FixtureTests(unittest.TestCase):
    def test_external_commit_survives_timeout(self):
        m = load(ROOT / "evals/cases/case-a/checkout.py")
        provider, local = m.Provider(), {}
        with self.assertRaises(TimeoutError):
            m.checkout(provider, local, "purchase-1")
        self.assertEqual({}, local)
        self.assertEqual(1, len(provider.charges))

    def test_replay_duplicates_effect_and_reconciliation_misses_it(self):
        m = load(ROOT / "evals/cases/case-a/checkout.py")
        provider, local = m.Provider(), {}
        for _ in range(2):
            with self.assertRaises(TimeoutError):
                m.checkout(provider, local, "purchase-1")
        self.assertEqual(2, len(provider.charges))
        self.assertEqual({}, m.reconcile(provider, local))

    def test_projection_is_a_different_mechanism(self):
        m = load(ROOT / "evals/cases/case-a/checkout.py")
        seen = set()
        m.project_seen(seen, "e1"); m.project_seen(seen, "e1")
        self.assertEqual({"e1"}, seen)

    def test_broken_projection_fails_contract(self):
        m = load(ROOT / "evals/cases/case-b/projection.py")
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite(m.apply))
        self.assertFalse(result.wasSuccessful())

    def test_contract_accepts_reference(self):
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite(reference_apply))
        self.assertTrue(result.wasSuccessful())

    def test_arrival_order_mutation_is_caught(self):
        def arrival(state, event):
            state[event["subject"]] = {k: event[k] for k in ("revision", "status")}
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite(arrival))
        self.assertFalse(result.wasSuccessful())

    def test_status_rank_mutation_is_caught(self):
        def ranked(state, event):
            if event["status"] == "pending" and state.get(event["subject"], {}).get("status") == "active":
                return
            reference_apply(state, event)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite(ranked))
        self.assertFalse(result.wasSuccessful())

    def test_metrics_populations(self):
        data = json.loads((ROOT / "evals/cases/case-c/observations.json").read_text())
        self.assertEqual(data["eligible_jobs"], data["unmaterialized_jobs"] + data["materialized_jobs"])
        self.assertEqual(40, data["eligible_jobs"] - data["completed_jobs"])
        self.assertEqual(data["materialized_jobs"], data["pending_materialized_jobs"] + data["completed_jobs"])
        audit = data["independent_audit"]
        self.assertEqual(audit["audited"], audit["confirmed_success"] + audit["confirmed_failure"])
        self.assertLessEqual(audit["audited"], data["completed_jobs"])

    def test_safe_effect_stays_single_across_connections(self):
        m = load(ROOT / "evals/cases/case-e/projection.py")
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "effects.db")
            for _ in range(3):
                m.apply(db, "intent-1", "payload")
            with sqlite3.connect(db) as connection:
                self.assertEqual([("intent-1", "payload")], connection.execute("SELECT * FROM effects").fetchall())

    def test_rubric_case_inventory(self):
        rubric = json.loads((ROOT / "evals/rubric.json").read_text())
        cases = {p.name for p in (ROOT / "evals/cases").iterdir() if p.is_dir()}
        self.assertEqual(cases, set(rubric) - {"notice"})
        for case in cases:
            self.assertTrue(rubric[case]["checks"])
            self.assertTrue(rubric[case]["critical_failures"])
