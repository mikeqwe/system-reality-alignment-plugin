"""Black-box contract checks for case-b. Run only on a trusted disposable solution.

Usage: python3 evals/check_projection.py /path/to/case-b/projection.py
This imports candidate Python code; it is NOT a sandbox. No model is invoked.
"""
import copy
import importlib.util
import itertools
from pathlib import Path
import sys
import unittest


def load(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_projection", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def suite(apply):
    class Contract(unittest.TestCase):
        def test_order_and_correction(self):
            events = [{"subject": "a", "revision": r, "status": s} for r, s in ((1, "pending"), (2, "active"), (3, "pending"))]
            for order in itertools.permutations(events):
                state = {}
                for event in order:
                    apply(state, event)
                self.assertEqual(state, {"a": {"revision": 3, "status": "pending"}})

        def test_repetition_and_subjects(self):
            state = {}
            for subject in ("a", "b", "a", "b"):
                apply(state, {"subject": subject, "revision": 1, "status": "failed"})
            self.assertEqual(state, {s: {"revision": 1, "status": "failed"} for s in ("a", "b")})
            self.assertNotIn("unseen", state)

        def test_conflict_is_nonmutating(self):
            state = {"a": {"revision": 2, "status": "active"}}
            before = copy.deepcopy(state)
            with self.assertRaises(ValueError):
                apply(state, {"subject": "a", "revision": 2, "status": "failed"})
            self.assertEqual(before, state)

        def test_invalid_is_nonmutating(self):
            valid = {"subject": "a", "revision": 2, "status": "active"}
            invalid = [None, [], {}, {**valid, "extra": 1}]
            invalid += [{**valid, "revision": r} for r in (True, False, 0, -1, 1.5, "2", None)]
            invalid += [{**valid, "subject": s} for s in ("", None, 7, [])]
            invalid += [{**valid, "status": s} for s in ("done", None, [], 3)]
            for event in invalid:
                with self.subTest(event=event):
                    state = {"a": {"revision": 3, "status": "pending"}}
                    before = copy.deepcopy(state)
                    with self.assertRaises(ValueError):
                        apply(state, event)
                    self.assertEqual(before, state)

        def test_input_not_aliased(self):
            event = {"subject": "a", "revision": 1, "status": "active"}
            before = copy.deepcopy(event)
            state = {}
            apply(state, event)
            self.assertEqual(before, event)
            event["status"] = "failed"
            self.assertEqual(state["a"], {"revision": 1, "status": "active"})

    return unittest.defaultTestLoader.loadTestsFromTestCase(Contract)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    result = unittest.TextTestRunner(verbosity=2).run(suite(load(Path(sys.argv[1])).apply))
    raise SystemExit(not result.wasSuccessful())
