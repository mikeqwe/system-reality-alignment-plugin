from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
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


def fill_short_sections(text: str) -> str:
    matches = list(re.finditer(r"^##\s+.+?$", text, re.MULTILINE))
    for index in range(len(matches) - 1, -1, -1):
        match = matches[index]
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if len(text[start:end].strip()) < 20:
            text = text[:start] + "\n\nEvidence-based section content for strict validation.\n" + text[end:]
    return text


def replace_label(text: str, label: str, value: str) -> str:
    return re.sub(
        rf"(?m)^([ \t]*-[ \t]*\*\*{re.escape(label)}:\*\*)[ \t]*.*$",
        rf"\1 {value}",
        text,
        count=1,
    )


def prepared_artifact(mode: str) -> str:
    path = SKILL_ROOT / "assets" / "templates" / new_artifact.MODES[mode]
    text = path.read_text(encoding="utf-8")
    text = text.replace("{{SYSTEM_NAME}}", "Example System").replace("{{DATE}}", "2026-07-21")
    text = fill_short_sections(text)
    if mode == "review":
        for label, value in {
            "Repository or source": "example/repository",
            "Repository revision": "a" * 40,
            "Actual paths inspected": "src/main.py and config/app.yaml",
        }.items():
            text = replace_label(text, label, value)
        for field in validate_artifact.REVIEW_FINDING_FIELDS:
            value = "CONFIRMED" if field == "Reachability status" else f"documented {field.lower()}"
            text = replace_label(text, field, value)
    elif mode == "repair":
        for label, value in {
            "Repository or source": "example/repository",
            "Repository revision": "b" * 40,
            "Actual paths inspected": "src/repair.py and db/schema.sql",
        }.items():
            text = replace_label(text, label, value)
        text = re.sub(
            r"(?m)^\*\*Applicability:\*\*.*$",
            "**Applicability:** NOT APPLICABLE — no replay or reprocessing is proposed",
            text,
        )
    elif mode == "implementation":
        for label, value in {
            "Repository or source": "example/repository",
            "Base revision": "c" * 40,
            "Actual paths inspected": "src/service.py and build.gradle",
        }.items():
            text = replace_label(text, label, value)
        text = re.sub(
            r"(?m)^\*\*Applicability:\*\*.*$",
            "**Applicability:** NOT APPLICABLE — the change adds no retry or replay path",
            text,
        )
    return text


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
        text = prepared_artifact("review").replace("a" * 40, "short-sha", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "review.md"
            path.write_text(text, encoding="utf-8")
            non_strict = validate_artifact.validate("review", path, strict=False)
            strict = validate_artifact.validate("review", path, strict=True)
            self.assertTrue(any("40-character revision" in item for item in non_strict["warnings"]))
            self.assertTrue(any("40-character revision" in item for item in strict["errors"]))

    def test_review_validates_required_fields_per_finding(self):
        text = prepared_artifact("review")
        second = """
### Finding SRA-002 — Incomplete finding

- **Severity:** High
- **Confidence:** High
- **Priority:** P1
- **Status:** Open
- **Affected decision or outcome:** registration
- **Mechanism ID:** REG-1
- **Reachability status:** CONFIRMED
- **Evidence snapshot and real paths:** src/registration.py
- **Evidence coverage:** EXHAUSTIVE
- **Mechanism:** synchronous registration
- **Failure scenario:** downstream failure
- **Impact:** inconsistent state
- **Recommendation:** fix compensation
- **Prerequisites and safety gates:** none
- **Verification:** integration test
- **Owner:** identity
- **Dependencies:** none
- **Residual risk:** low
"""
        text = text.replace("\n## Maturity Assessment", second + "\n## Maturity Assessment")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "review.md"
            path.write_text(text, encoding="utf-8")
            result = validate_artifact.validate("review", path, strict=True)
            self.assertFalse(result["valid"])
            self.assertTrue(
                any("Finding SRA-002" in error and "Counterevidence checked" in error for error in result["errors"]),
                result,
            )

    def test_repair_strict_requires_reproducibility_revision(self):
        text = prepared_artifact("repair").replace("b" * 40, "", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair.md"
            path.write_text(text, encoding="utf-8")
            result = validate_artifact.validate("repair", path, strict=True)
            self.assertFalse(result["valid"])
            self.assertTrue(any("repair reproducibility snapshot" in error for error in result["errors"]))

    def test_implementation_strict_requires_reproducibility_revision(self):
        text = prepared_artifact("implementation").replace("c" * 40, "short", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "implementation.md"
            path.write_text(text, encoding="utf-8")
            result = validate_artifact.validate("implementation", path, strict=True)
            self.assertFalse(result["valid"])
            self.assertTrue(any("implementation reproducibility snapshot" in error for error in result["errors"]))

    def test_repair_strict_accepts_explicit_non_applicable_replay_gate(self):
        text = prepared_artifact("repair")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair.md"
            path.write_text(text, encoding="utf-8")
            result = validate_artifact.validate("repair", path, strict=True)
            self.assertFalse(
                any("retry/replay safety" in error for error in result["errors"]),
                result,
            )

    def test_implementation_applicable_replay_gate_requires_handler_row(self):
        text = prepared_artifact("implementation")
        text = text.replace(
            "**Applicability:** NOT APPLICABLE — the change adds no retry or replay path",
            "**Applicability:** APPLICABLE",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "implementation.md"
            path.write_text(text, encoding="utf-8")
            result = validate_artifact.validate("implementation", path, strict=True)
            self.assertTrue(any("has no handler data row" in error for error in result["errors"]), result)

    def test_evaluation_template_defaults_to_unknown(self):
        template = SKILL_ROOT / "assets" / "templates" / "evaluation.md"
        match = validate_artifact.EVALUATION_CLASSIFICATION_RE.search(template.read_text(encoding="utf-8"))
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "UNKNOWN")

    def test_evaluation_schema_and_consumer_share_contract_fields(self):
        schema = json.loads(
            (SKILL_ROOT / "schemas" / "evaluation-run.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(summarize_evaluations.REQUIRED_FIELDS))
        self.assertEqual(set(schema["properties"]), set(summarize_evaluations.ALLOWED_FIELDS))
        self.assertIn("allOf", schema)

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

    def test_treatment_guardrail_overrides_metric(self):
        records = [
            evaluation_record("c1", "control", 0.0),
            evaluation_record("c2", "control", 0.0),
            evaluation_record("t1", "treatment", 10.0, violations=["fabricated evidence"]),
            evaluation_record("t2", "treatment", 10.0),
        ]
        result = summarize_evaluations.summarize(records, 0.2, minimum_samples=2)
        self.assertEqual(result[0]["classification"], "HARMFUL")
        self.assertEqual(result[0]["treatment_hard_guardrail_violations"], 1)
        self.assertEqual(result[0]["classification_guardrail_scope"], "treatment arm")

    def test_control_guardrail_is_reported_without_intervention_harm_override(self):
        records = [
            evaluation_record("c1", "control", 1.0, violations=["baseline incident"]),
            evaluation_record("c2", "control", 1.0),
            evaluation_record("t1", "treatment", 1.0),
            evaluation_record("t2", "treatment", 1.0),
        ]
        result = summarize_evaluations.summarize(records, 0.1, minimum_samples=2)[0]
        self.assertEqual(result["classification"], "NEUTRAL")
        self.assertEqual(result["control_hard_guardrail_violations"], 1)
        self.assertEqual(result["treatment_hard_guardrail_violations"], 0)
        self.assertIn("baseline risk", result["comparison_validity_note"])

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

    def test_load_records_rejects_unexpected_fields(self):
        record = evaluation_record("x", "control", 1.0)
        record["undeclared"] = True
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            summarize_evaluations.validate_record(record, 1)

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

    def test_timestamps_require_timezone(self):
        record = evaluation_record("x", "control", 1.0)
        record["started_at"] = "2026-07-21T10:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            summarize_evaluations.validate_record(record, 1)

    def test_grouping_cannot_drop_comparability_fields(self):
        records = [
            evaluation_record("c1", "control", 1.0),
            evaluation_record("t1", "treatment", 1.0),
        ]
        with self.assertRaisesRegex(ValueError, "preserve comparability fields"):
            summarize_evaluations.summarize(
                records,
                0.1,
                group_by=("evaluation_id", "primary_metric"),
                minimum_samples=2,
            )


if __name__ == "__main__":
    unittest.main()
