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
from statistics import mean, variance
import sys
from typing import Any, Iterable

ASSIGNMENTS = {"control", "treatment"}
DIRECTIONS = {"higher_is_better", "lower_is_better"}
DEFAULT_GROUP_BY = (
    "evaluation_id",
    "intervention_version",
    "model_version",
    "primary_metric",
    "metric_direction",
    "mode",
    "complexity",
    "risk_tier",
)
REQUIRED_FIELDS = {
    "evaluation_id",
    "task_id",
    "eligible",
    "assignment",
    "activated",
    "intervention_version",
    "mode",
    "model_version",
    "complexity",
    "risk_tier",
    "started_at",
    "completed_at",
    "primary_metric",
    "metric_direction",
    "metric_value",
    "outcome_mature",
    "hard_guardrail_violations",
    "outcome_source",
}


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


def validate_record(record: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(f"line {line_number}: record must be a JSON object")
    missing = sorted(REQUIRED_FIELDS - set(record))
    if missing:
        raise ValueError(f"line {line_number}: missing fields: {', '.join(missing)}")
    for field in ("evaluation_id", "task_id", "intervention_version"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"line {line_number}: {field} must be a non-empty string")
    if not isinstance(record["eligible"], bool):
        raise ValueError(f"line {line_number}: eligible must be boolean")
    if record["assignment"] not in ASSIGNMENTS:
        raise ValueError(f"line {line_number}: assignment must be control or treatment")
    if not isinstance(record["activated"], bool):
        raise ValueError(f"line {line_number}: activated must be boolean")
    if record["metric_direction"] not in DIRECTIONS:
        raise ValueError(
            f"line {line_number}: metric_direction must be higher_is_better or lower_is_better"
        )
    if record["metric_value"] is not None and (
        isinstance(record["metric_value"], bool) or not isinstance(record["metric_value"], (int, float))
    ):
        raise ValueError(f"line {line_number}: metric_value must be numeric or null")
    if not isinstance(record["outcome_mature"], bool):
        raise ValueError(f"line {line_number}: outcome_mature must be boolean")
    if record["outcome_mature"] and (
        not isinstance(record["outcome_source"], str) or not record["outcome_source"].strip()
    ):
        raise ValueError(f"line {line_number}: mature outcomes require a non-empty outcome_source")
    violations = record["hard_guardrail_violations"]
    if not isinstance(violations, list) or any(not isinstance(item, str) or not item for item in violations):
        raise ValueError(f"line {line_number}: hard_guardrail_violations must be a list of strings")
    for field in ("mode", "model_version", "complexity", "risk_tier", "primary_metric"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"line {line_number}: {field} must be a non-empty string")
    try:
        started = datetime.fromisoformat(str(record["started_at"]).replace("Z", "+00:00"))
        completed = datetime.fromisoformat(str(record["completed_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"line {line_number}: started_at and completed_at must be ISO-8601 timestamps") from exc
    if started.tzinfo is None or completed.tzinfo is None:
        raise ValueError(f"line {line_number}: timestamps must include a timezone")
    if completed < started:
        raise ValueError(f"line {line_number}: completed_at precedes started_at")
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
    standard_error = math.sqrt(variance(control) / len(control) + variance(treatment) / len(treatment))
    margin = 1.96 * standard_error
    return effect, effect - margin, effect + margin


def classify(
    interval: tuple[float, float, float] | None,
    minimum_effect: float,
    hard_guardrail_violations: int,
) -> tuple[str, str]:
    if hard_guardrail_violations:
        return "HARMFUL", "hard guardrail violation"
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
    if minimum_effect < 0:
        raise ValueError("minimum_effect must be non-negative")
    if minimum_samples < 2:
        raise ValueError("minimum_samples must be at least 2")
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["eligible"]:
            groups[tuple(record.get(field) for field in group_by)].append(record)

    results: list[dict[str, Any]] = []
    for key in sorted(groups, key=lambda item: tuple(str(value) for value in item)):
        group = groups[key]
        directions = {record["metric_direction"] for record in group}
        if len(directions) != 1:
            raise ValueError(f"group {key!r} mixes metric directions")
        direction = directions.pop()
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
        violations = sum(
            len(record["hard_guardrail_violations"])
            for record in assigned["treatment"]
        )
        interval = normal_interval(
            mature_values["control"],
            mature_values["treatment"],
            direction,
            minimum_samples,
        )
        status, reason = classify(interval, minimum_effect, violations)
        effect, lower, upper = interval if interval is not None else (None, None, None)
        result = {
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
            "hard_guardrail_violations": violations,
            "classification": status,
            "reason": reason,
        }
        results.append(result)
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
        "| Segment | Control mature/assigned/activated | Treatment mature/assigned/activated | Control mean | Treatment mean | Effect | 95% interval | Guardrail violations | Classification |",
        "|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for result in results:
        segment = ", ".join(f"{field}={result['segment'].get(field)}" for field in group_by)
        interval = (
            "—"
            if result["ci95_lower"] is None
            else f"[{format_number(result['ci95_lower'])}, {format_number(result['ci95_upper'])}]"
        )
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
                    str(result["hard_guardrail_violations"]),
                    f"**{result['classification']}** — {result['reason']}",
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
    if not group_by:
        print("error: group-by must contain at least one field", file=sys.stderr)
        return 2
    try:
        records = load_records(args.path)
        results = summarize(
            records,
            args.minimum_effect,
            group_by,
            minimum_samples=args.minimum_samples,
        )
    except (OSError, ValueError) as exc:
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
