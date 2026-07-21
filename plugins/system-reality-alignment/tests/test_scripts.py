from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "align-system"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new_artifact = load_module("new_artifact", SKILL_ROOT / "scripts" / "new_artifact.py")
validate_artifact = load_module("validate_artifact", SKILL_ROOT / "scripts" / "validate_artifact.py")
summarize_evaluations = load_module(
    "summarize_evaluations", SKILL_ROOT / "scripts" / "summarize_evaluations.py"
)


def evaluation_record(
    task_id: str,
    assignment: str,
    value: float | None,
    *,
    direction: str = "higher_is_better",
    mature: bool = True,
    violations: list[str] | None = None,
) -> dict[str, object]:
    return {
        "evaluation_id": "eval-review-v1.1.0",
        "task_id": task_id,
        "eligible": True,
        "assignment": assignment,
        "activated": assignment == "treatment",
        "intervention_version": "1.1.0",
        "mode": "review",
        "model_version": "example-model",
        "complexity": "medium",
        "risk_tier": "medium",
        "started_at": "2026-07-21T10:00:00Z",
        "completed_at": "2026-07-21T10:30:00Z",
        "primary_metric": "confirmed-findings-per-hour",
        "metric_direction": direction,
        "metric_value": value,
        "outcome_mature": mature,
        "hard_guardrail_violations": violations or [],
        "outcome_source": "blinded-reviewer",
    }


class ScriptTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(new_artifact.slugify("Payment Reconciliation"), "payment-reconciliation")
        self.assertEqual(new_artifact.slugify("  "), "system")

    def test_all_templates_exist(self):
        template_dir = SKILL_ROOT / "assets" / "templates"
        for filename in new_artifact.MODES.values():
            self.assertTrue((template_dir / filename).is_file(), filename)

    def test_templates_pass_non_strict_validation_after_base_replacement(self):
        template_dir = SKILL_ROOT / "assets" / "templates"
        with tempfile.TemporaryDirectory() as temp_dir:
            for mode, filename in new_artifact.MODES.items():
                text = (template_dir / filename).read_text(encoding="utf-8")
                text = text.replace("{{SYSTEM_NAME}}", "Example System").replace("{{DATE}}", "2026-07-21")
                path = Path(temp_dir) / filename
                path.write_text(text, encoding="utf-8")
                result = validate_artifact.validate(mode, path, strict=False)
                self.assertTrue(result["valid"], f"{mode}: {result}")

    def test_missing_heading_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.md"
            path.write_text("# Example\n\n## Executive Assessment\n\nSome content.\n", encoding="utf-8")
            result = validate_artifact.validate("review", path, strict=False)
            self.assertFalse(result["valid"])
            self.assertTrue(result["errors"])

    def test_unresolved_placeholder_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.md"
            path.write_text("# {{SYSTEM_NAME}}\n", encoding="utf-8")
            result = validate_artifact.validate("review", path, strict=False)
            self.assertFalse(result["valid"])
            self.assertTrue(any("placeholder" in error for error in result["errors"]))

    def test_review_without_full_revision_warns_and_strict_fails(self):
        template = SKILL_ROOT / "assets" / "templates" / "review.md"
        text = template.read_text(encoding="utf-8")
        text = text.replace("{{SYSTEM_NAME}}", "Example").replace("{{DATE}}", "2026-07-21")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "review.md"
            path.write_text(text, encoding="utf-8")
            non_strict = validate_artifact.validate("review", path, strict=False)
            strict = validate_artifact.validate("review", path, strict=True)
            self.assertTrue(any("40-character revision" in item for item in non_strict["warnings"]))
            self.assertTrue(any("40-character revision" in item for item in strict["errors"]))

    def test_evaluation_template_declares_unknown(self):
        template = SKILL_ROOT / "assets" / "templates" / "evaluation.md"
        text = template.read_text(encoding="utf-8")
        self.assertRegex(text, validate_artifact.EVALUATION_CLASSIFICATION_RE)

    def test_evaluation_schema_is_valid_json_and_requires_assignment(self):
        schema = json.loads(
            (SKILL_ROOT / "schemas" / "evaluation-run.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["type"], "object")
        self.assertIn("evaluation_id", schema["required"])
        self.assertIn("assignment", schema["required"])
        self.assertEqual(schema["properties"]["assignment"]["enum"], ["control", "treatment"])

    def test_summarizer_classifies_useful(self):
        records = [
            evaluation_record("c1", "control", 0.0),
            evaluation_record("c2", "control", 0.0),
            evaluation_record("t1", "treatment", 1.0),
            evaluation_record("t2", "treatment", 1.0),
        ]
        result = summarize_evaluations.summarize(records, 0.2, minimum_samples=2)
        self.assertEqual(result[0]["classification"], "USEFUL")
        self.assertEqual(result[0]["normalized_effect"], 1.0)

    def test_summarizer_normalizes_lower_is_better(self):
        records = [
            evaluation_record("c1", "control", 10.0, direction="lower_is_better"),
            evaluation_record("c2", "control", 10.0, direction="lower_is_better"),
            evaluation_record("t1", "treatment", 8.0, direction="lower_is_better"),
            evaluation_record("t2", "treatment", 8.0, direction="lower_is_better"),
        ]
        result = summarize_evaluations.summarize(records, 0.5, minimum_samples=2)
        self.assertEqual(result[0]["classification"], "USEFUL")
        self.assertEqual(result[0]["normalized_effect"], 2.0)

    def test_summarizer_classifies_neutral(self):
        records = [
            evaluation_record("c1", "control", 1.0),
            evaluation_record("c2", "control", 1.0),
            evaluation_record("t1", "treatment", 1.0),
            evaluation_record("t2", "treatment", 1.0),
        ]
        result = summarize_evaluations.summarize(records, 0.1, minimum_samples=2)
        self.assertEqual(result[0]["classification"], "NEUTRAL")

    def test_summarizer_guardrail_overrides_metric(self):
        records = [
            evaluation_record("c1", "control", 0.0),
            evaluation_record("c2", "control", 0.0),
            evaluation_record("t1", "treatment", 10.0, violations=["fabricated evidence"]),
            evaluation_record("t2", "treatment", 10.0),
        ]
        result = summarize_evaluations.summarize(records, 0.2, minimum_samples=2)
        self.assertEqual(result[0]["classification"], "HARMFUL")
        self.assertEqual(result[0]["hard_guardrail_violations"], 1)

    def test_summarizer_returns_unknown_for_insufficient_mature_data(self):
        records = [
            evaluation_record("c1", "control", 0.0),
            evaluation_record("t1", "treatment", 1.0),
        ]
        result = summarize_evaluations.summarize(records, 0.2, minimum_samples=2)
        self.assertEqual(result[0]["classification"], "UNKNOWN")

    def test_load_records_rejects_missing_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "runs.jsonl"
            path.write_text('{"task_id": "x"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing fields"):
                summarize_evaluations.load_records(path)

    def test_load_records_rejects_duplicate_task_in_evaluation(self):
        record = evaluation_record("same", "control", 1.0)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "runs.jsonl"
            path.write_text(
                json.dumps(record) + "\n" + json.dumps(record) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate task_id"):
                summarize_evaluations.load_records(path)

    def test_mature_outcome_requires_source(self):
        record = evaluation_record("x", "control", 1.0)
        record["outcome_source"] = None
        with self.assertRaisesRegex(ValueError, "mature outcomes require"):
            summarize_evaluations.validate_record(record, 1)


if __name__ == "__main__":
    unittest.main()
