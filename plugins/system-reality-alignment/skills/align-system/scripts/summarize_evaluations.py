#!/usr/bin/env python3
"""Summarize control/treatment evaluation runs from JSONL.

The interval is a transparent 95% normal approximation for a difference in
means. It is intended for reproducible operational diagnostics, not as a
substitute for experimental design or domain review.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import json
import math
from pathlib import Path
import re
from statistics import mean, variance
import sys
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = SCRIPT_DIR.parent / "schemas" / "evaluation-run.schema.json"


def load_contract() -> dict[str, Any]:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot load evaluation contract {SCHEMA_PATH}: {exc}") from exc
    if schema.get("type") != "object" or not isinstance(schema.get("properties"), dict):
        raise RuntimeError("evaluation contract must define an object with properties")
    return schema


CONTRACT = load_contract()
PROPERTIES: dict[str, Any] = CONTRACT["properties"]
REQUIRED_FIELDS = frozenset(CONTRACT.get("required", []))
ALLOWED_FIELDS = frozenset(PROPERTIES)
ASSIGNMENTS = frozenset(PROPERTIES["assignment"]["enum"])
DIRECTIONS = frozenset(PROPERTIES["metric_direction"]["enum"])
MODES = frozenset(PROPERTIES["mode"]["enum"])
TIMESTAMP_RE = re.compile(CONTRACT["$defs"]["timezoneDateTime"]["pattern"])
REVISION_RE = re.compile(PROPERTIES["repository_revision"]["pattern"])
COMPARABILITY_FIELDS = (
    "evaluation_id",
    "intervention_version",
    "model_version",
    "primary_metric",
    "metric_direction",
    "mode",
    "complexity",
    "risk_tier",
)
DEFAULT_GROUP_BY = COMPARABILITY_FIELDS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="JSONL file containing evaluation run records")
    parser.add_argument(
        "--minimum-effect",
        type=float,
        required=True,
        help="Absolute normalized effect required for practical significance",
    )
    parser.add_argument(
        "--minimum-samples",
        type=int,
        default=5,
        help="Minimum mature observations required in each assignment arm (default: 5)",
    )
    parser.add_argument(
        "--group-by",
        default=",".join(DEFAULT_GROUP_BY),
        help="Comma-separated record fields used to form comparable segments",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON instead of Markdown")
    return parser.parse_args()


def require_nonempty_string(record: dict[str, Any], field: str, line_number: int) -> None:
    if not isinstance(record[field], str) or not record[field].strip():
        raise ValueError(f"line {line_number}: {field} must be a non-empty string")


def validate_optional_number(record: dict[str, Any], field: str, line_number: int) -> None:
    if field not in record or record[field] is None:
        return
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"line {line_number}: {field} must be a finite number or null")
    if value < 0:
        raise ValueError(f"line {line_number}: {field} must be non-negative")


def validate_optional_string(record: dict[str, Any], field: str, line_number: int) -> None:
    if field not in record or record[field] is None:
        return
    if not isinstance(record[field], str):
        raise ValueError(f"line {line_number}: {field} must be a string or null")


def validate_record(record: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(f"line {line_number}: record must be a JSON object")

    fields = set(record)
    missing = sorted(REQUIRED_FIELDS - fields)
    if missing:
        raise ValueError(f"line {line_number}: missing fields: {', '.join(missing)}")
    unexpected = sorted(fields - ALLOWED_FIELDS)
    if unexpected:
        raise ValueError(f"line {line_number}: unexpected fields: {', '.join(unexpected)}")

    for field in (
        "evaluation_id",
        "task_id",
        "intervention_version",
        "model_version",
        "complexity",
        "risk_tier",
        "primary_metric",
    ):
        require_nonempty_string(record, field, line_number)

    if not isinstance(record["eligible"], bool):
        raise ValueError(f"line {line_number}: eligible must be boolean")
    if record["assignment"] not in ASSIGNMENTS:
        raise ValueError(f"line {line_number}: assignment must be control or treatment")
    if not isinstance(record["activated"], bool):
        raise ValueError(f"line {line_number}: activated must be boolean")
    if record["mode"] not in MODES:
        raise ValueError(f"line {line_number}: mode is not allowed by the evaluation contract")
    if record["metric_direction"] not in DIRECTIONS:
        raise ValueError(
            f"line {line_number}: metric_direction must be higher_is_better or lower_is_better"
        )

    metric_value = record["metric_value"]
    if metric_value is not None and (
        isinstance(metric_value, bool)
        or not isinstance(metric_value, (int, float))
        or not math.isfinite(float(metric_value))
    ):
        raise ValueError(f"line {line_number}: metric_value must be a finite number or null")

    if not isinstance(record["outcome_mature"], bool):
        raise ValueError(f"line {line_number}: outcome_mature must be boolean")
    if record["outcome_mature"] and (
        not isinstance(record["outcome_source"], str) or not record["outcome_source"].strip()
    ):
        raise ValueError(f"line {line_number}: mature outcomes require a non-empty outcome_source")
    validate_optional_string(record, "outcome_source", line_number)

    violations = record["hard_guardrail_violations"]
    if not isinstance(violations, list) or any(
        not isinstance(item, str) or not item.strip() for item in violations
    ):
        raise ValueError(f"line {line_number}: hard_guardrail_violations must be a list of non-empty strings")
    if len(set(violations)) != len(violations):
        raise ValueError(f"line {line_number}: hard_guardrail_violations must contain unique values")

    for field in ("started_at", "completed_at"):
        value = record[field]
        if not isinstance(value, str) or not TIMESTAMP_RE.fullmatch(value):
            raise ValueError(f"line {line_number}: {field} must be an ISO-8601 timestamp with a timezone")
    try:
        started = datetime.fromisoformat(record["started_at"].replace("Z", "+00:00"))
        completed = datetime.fromisoformat(record["completed_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"line {line_number}: started_at and completed_at must be valid ISO-8601 timestamps"
        ) from exc
    if completed < started:
        raise ValueError(f"line {line_number}: completed_at precedes started_at")

    if "tool_versions" in record:
        tools = record["tool_versions"]
        if not isinstance(tools, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in tools.items()
        ):
            raise ValueError(f"line {line_number}: tool_versions must be an object of string values")

    revision = record.get("repository_revision")
    if revision is not None and (
        not isinstance(revision, str) or not REVISION_RE.fullmatch(revision)
    ):
        raise ValueError(f"line {line_number}: repository_revision must be a full 40-character SHA or null")

    validate_optional_number(record, "human_review_minutes", line_number)
    validate_optional_number(record, "cost_units", line_number)
    if "reviewer_blinded" in record and record["reviewer_blinded"] is not None and not isinstance(
        record["reviewer_blinded"], bool
    ):
        raise ValueError(f"line {line_number}: reviewer_blinded must be boolean or null")
    validate_optional_string(record, "exclusion_reason", line_number)
    validate_optional_string(record, "notes", line_number)
    return record


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, raw in enumerate(stream, start=1):
            if not raw.strip():
                continue
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
            records.append(validate_record(parsed, line_number))
    if not records:
        raise ValueError("no evaluation records found")

    seen: set[tuple[str, str]] = set()
    for record in records:
        identity = (record["evaluation_id"], record["task_id"])
        if identity in seen:
            raise ValueError(
                f"duplicate task_id {record['task_id']!r} in evaluation {record['evaluation_id']!r}"
            )
        seen.add(identity)
    return records


def validate_group_by(group_by: tuple[str, ...]) -> None:
    if not group_by:
        raise ValueError("group-by must contain at least one field")
    unknown = sorted(set(group_by) - ALLOWED_FIELDS)
    if unknown:
        raise ValueError(f"group-by contains unknown fields: {', '.join(unknown)}")
    missing = [field for field in COMPARABILITY_FIELDS if field not in group_by]
    if missing:
        raise ValueError(
            "group-by must preserve comparability fields: " + ", ".join(missing)
        )


def normal_interval(
    control: list[float],
    treatment: list[float],
    direction: str,
    minimum_samples: int,
) -> tuple[float, float, float] | None:
    if len(control) < minimum_samples or len(treatment) < minimum_samples:
        return None
    raw_effect = mean(treatment) - mean(control)
    effect = raw_effect if direction == "higher_is_better" else -raw_effect
    standard_error = math.sqrt(
        variance(control) / len(control) + variance(treatment) / len(treatment)
    )
    margin = 1.96 * standard_error
    return effect, effect - margin, effect + margin


def classify(
    interval: tuple[float, float, float] | None,
    minimum_effect: float,
    treatment_guardrail_violations: int,
) -> tuple[str, str]:
    if treatment_guardrail_violations:
        return "HARMFUL", "hard guardrail violation observed in the treatment arm"
    if interval is None:
        return "UNKNOWN", "insufficient mature control/treatment observations for an interval"
    _, lower, upper = interval
    if lower > minimum_effect:
        return "USEFUL", "interval exceeds the practical-improvement threshold"
    if upper < -minimum_effect:
        return "HARMFUL", "interval exceeds the practical-harm threshold"
    if lower >= -minimum_effect and upper <= minimum_effect:
        return "NEUTRAL", "interval is contained within the equivalence band"
    return "UNKNOWN", "interval overlaps multiple decision regions"


def summarize(
    records: Iterable[dict[str, Any]],
    minimum_effect: float,
    group_by: tuple[str, ...] = DEFAULT_GROUP_BY,
    minimum_samples: int = 5,
) -> list[dict[str, Any]]:
    if not math.isfinite(minimum_effect) or minimum_effect < 0:
        raise ValueError("minimum_effect must be a finite non-negative number")
    if minimum_samples < 2:
        raise ValueError("minimum_samples must be at least 2")
    validate_group_by(group_by)

    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["eligible"]:
            groups[tuple(record.get(field) for field in group_by)].append(record)

    results: list[dict[str, Any]] = []
    for key in sorted(groups, key=lambda item: tuple(str(value) for value in item)):
        group = groups[key]
        assigned = {
            assignment: [record for record in group if record["assignment"] == assignment]
            for assignment in sorted(ASSIGNMENTS)
        }
        mature_values = {
            assignment: [
                float(record["metric_value"])
                for record in assigned[assignment]
                if record["outcome_mature"] and record["metric_value"] is not None
            ]
            for assignment in sorted(ASSIGNMENTS)
        }
        guardrails = {
            assignment: sum(
                len(record["hard_guardrail_violations"])
                for record in assigned[assignment]
            )
            for assignment in sorted(ASSIGNMENTS)
        }
        direction = str(key[group_by.index("metric_direction")])
        interval = normal_interval(
            mature_values["control"],
            mature_values["treatment"],
            direction,
            minimum_samples,
        )
        status, reason = classify(interval, minimum_effect, guardrails["treatment"])
        effect, lower, upper = interval if interval is not None else (None, None, None)
        validity_note = (
            "control-arm hard guardrail events were observed; inspect baseline risk and assignment validity"
            if guardrails["control"]
            else None
        )
        results.append(
            {
                "segment": {field: value for field, value in zip(group_by, key)},
                "control_assigned": len(assigned["control"]),
                "treatment_assigned": len(assigned["treatment"]),
                "control_activated": sum(1 for record in assigned["control"] if record["activated"]),
                "treatment_activated": sum(1 for record in assigned["treatment"] if record["activated"]),
                "control_mature": len(mature_values["control"]),
                "treatment_mature": len(mature_values["treatment"]),
                "control_mean": mean(mature_values["control"]) if mature_values["control"] else None,
                "treatment_mean": mean(mature_values["treatment"]) if mature_values["treatment"] else None,
                "normalized_effect": effect,
                "ci95_lower": lower,
                "ci95_upper": upper,
                "control_hard_guardrail_violations": guardrails["control"],
                "treatment_hard_guardrail_violations": guardrails["treatment"],
                "hard_guardrail_violations": guardrails["treatment"],
                "classification_guardrail_scope": "treatment arm",
                "comparison_validity_note": validity_note,
                "classification": status,
                "reason": reason,
            }
        )
    return results


def format_number(value: Any) -> str:
    return "—" if value is None else f"{value:.6g}"


def render_markdown(
    results: list[dict[str, Any]],
    group_by: tuple[str, ...],
    minimum_effect: float,
    minimum_samples: int,
) -> str:
    lines = [
        "# Evaluation Summary",
        "",
        f"Minimum practical effect (delta): `{minimum_effect:g}`",
        f"Minimum mature observations per arm: `{minimum_samples}`",
        "",
        "The interval is a 95% normal approximation for the normalized treatment-minus-control mean difference. Assignment counts implement an intention-to-treat comparison; activation counts expose non-compliance or contamination.",
        "",
        "Any hard guardrail observed in the treatment arm conservatively classifies the segment as HARMFUL. Control-arm guardrails are reported separately as baseline risk; they do not by themselves classify the intervention as harmful, but they can weaken or invalidate causal interpretation.",
        "",
        "| Segment | Control mature/assigned/activated | Treatment mature/assigned/activated | Control mean | Treatment mean | Effect | 95% interval | Guardrails C/T | Classification |",
        "|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for result in results:
        segment = ", ".join(f"{field}={result['segment'].get(field)}" for field in group_by)
        interval = (
            "—"
            if result["ci95_lower"] is None
            else f"[{format_number(result['ci95_lower'])}, {format_number(result['ci95_upper'])}]"
        )
        classification = f"**{result['classification']}** — {result['reason']}"
        if result["comparison_validity_note"]:
            classification += f"; {result['comparison_validity_note']}"
        lines.append(
            "| "
            + " | ".join(
                [
                    segment.replace("|", "\\|"),
                    f"{result['control_mature']}/{result['control_assigned']}/{result['control_activated']}",
                    f"{result['treatment_mature']}/{result['treatment_assigned']}/{result['treatment_activated']}",
                    format_number(result["control_mean"]),
                    format_number(result["treatment_mean"]),
                    format_number(result["normalized_effect"]),
                    interval,
                    f"{result['control_hard_guardrail_violations']}/{result['treatment_hard_guardrail_violations']}",
                    classification,
                ]
            )
            + " |"
        )
    if not results:
        lines.extend(["", "No eligible groups were found."])
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    group_by = tuple(field.strip() for field in args.group_by.split(",") if field.strip())
    try:
        records = load_records(args.path)
        results = summarize(
            records,
            args.minimum_effect,
            group_by,
            minimum_samples=args.minimum_samples,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(
            json.dumps(
                {
                    "minimum_effect": args.minimum_effect,
                    "minimum_samples": args.minimum_samples,
                    "groups": results,
                },
                indent=2,
            )
        )
    else:
        print(
            render_markdown(
                results,
                group_by,
                args.minimum_effect,
                args.minimum_samples,
            ),
            end="",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
