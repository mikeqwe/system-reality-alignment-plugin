#!/usr/bin/env python3
"""Validate required structure and semantic gates in an alignment artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Iterable

REQUIRED_HEADINGS = {
    "design": [
        "Executive Summary", "Scope and Boundaries", "Target Decisions and Real-World Outcomes",
        "Evidence and Assumptions", "Feedback-Loop Map", "Observation Model", "Derived State Model",
        "Decision and Override Model", "Action and Outcome Model", "Identity, Time, and Authority Semantics",
        "Unknown, Conflict, and Correction Semantics", "Data and Event Contracts", "Invariants",
        "Reconciliation and Independent Verification", "Observability and Metrics", "Migration, Rollout, and Rollback",
        "Verification Plan", "Risks and Residual Unknowns",
    ],
    "review": [
        "Executive Assessment", "Reproducibility Snapshot", "Scope and Target Decisions", "Mechanism Inventory",
        "Evidence and Claim Ledger", "Execution-Path Traces", "Reconciliation Direction and Blind Spots",
        "State, Dependency, and Compatibility Model", "Feedback-Loop Map", "Quantitative Claims and Commands",
        "Strengths to Preserve", "Findings", "Maturity Assessment", "Prioritized Actions",
        "Review Limitations and Missing Evidence", "Residual Unknowns",
    ],
    "plan": [
        "Executive Summary", "Scope, Target Decisions, and Outcomes", "Current Baseline", "Gap Map", "Target State",
        "Workstreams", "Sequencing and Dependencies", "Milestones and Acceptance Criteria",
        "Instrumentation and Observe-Only Phase", "Migration and Mixed-Version Operation", "Backfill and Reconciliation",
        "Rollout, Stop Conditions, and Rollback", "Ownership and Governance", "Metrics and Operating Handoff",
        "Risks, Assumptions, and Unknowns",
    ],
    "repair": [
        "Incident or Inconsistency Statement", "Impact and Affected Outcomes", "Reproducibility Snapshot",
        "Immediate Containment", "Evidence Inventory", "Mechanism and Storage-Role Inventory", "Timeline",
        "Facts, Conflicts, Hypotheses, and Unknowns", "Execution-Path Trace and Causal Mechanism",
        "Affected-Data Analysis", "Retry, Replay, and Reprocessing Safety", "Source-Level Fix",
        "Data Correction and Reconciliation", "Compensation, Notification, and Audit",
        "Regression Tests and Invariants", "Observability and Recurrence Detection", "Rollout and Rollback",
        "Verification and Closure Criteria", "Residual Risk and Follow-Up Owners",
    ],
    "implementation": [
        "Objective and Acceptance Criteria", "Scope and Non-Goals", "Reproducibility Snapshot",
        "Current Behavior and Evidence", "Mechanism, Storage, Dependency, and Compatibility Inventory",
        "Proposed Semantic Changes", "Contracts, Schemas, and Versions", "Identity and Time Semantics",
        "Unknown, Conflict, and Correction Handling", "Invariants and Enforcement Points",
        "Retry, Replay, and Partial-Failure Safety", "Code and Data Changes", "Migration and Backfill", "Test Matrix",
        "Telemetry, Reconciliation, and Alerts", "Rollout, Stop Conditions, and Rollback",
        "Operational Runbook Changes", "Validation Results", "Residual Risks and Unknowns",
    ],
    "operations": [
        "Executive Summary", "Target Decisions and Outcomes", "Scorecard", "Changes from Baseline",
        "Reconciliation Results and Discrepancy Aging", "Unknown, Conflict, Correction, and Override Trends",
        "Drift and Anomaly Analysis", "Sampled Decision Reproducibility", "Incidents, Corrections, and Learned Changes",
        "Decisions Taken", "Assigned Actions and Owners", "Residual Risk", "Next Review Triggers and Criteria",
    ],
    "evaluation": [
        "Executive Decision", "Evaluation Question and Eligible Population", "Intervention and Version Snapshot",
        "Segments and Exclusions", "Counterfactual and Assignment", "Primary Metric and Equivalence Band",
        "Guardrails and Stop Conditions", "Data Quality and Outcome Maturity", "Results by Segment",
        "Guardrail Events and Failure Modes", "Classification", "Cost and Workflow Impact",
        "Rollout, Restriction, or Kill-Switch Decision", "Residual Uncertainty and Next Review",
    ],
    "decision-record": [
        "Context and Target Outcome", "Evidence Available", "Evidence Missing or Conflicting", "Options Considered",
        "Decision", "Decision Rule, Policy, Query, or Model Version", "Expected Outcome and Guardrails",
        "Action and Owner", "Verification Signal and Feedback Date", "Actual Outcome",
        "Corrections, Appeals, or Superseding Decisions",
    ],
    "data-contract": [
        "Purpose and Domain Meaning", "Producer, Consumers, and Owners", "Authority by Fact",
        "Schema and Field Semantics", "Identity and Idempotency",
        "Event, Observation, Ingestion, Processing, and Effective Time", "Units, Timezones, and Precision",
        "Ordering, Duplicate, Late, Replay, and Correction Behavior",
        "Unknown, Conflict, Invalid, and Not-Applicable Representation", "Validation, Quarantine, and Error Handling",
        "Compatibility and Versioning", "Service Levels and Freshness", "Retention, Privacy, and Deletion",
        "Reconciliation and Audit", "Change and Deprecation Process",
    ],
}

PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}")
HEADING_RE = re.compile(r"^#{2,6}\s+(.+?)\s*$", re.MULTILINE)
FULL_SHA_RE = re.compile(r"\b[0-9a-fA-F]{40}\b")
EVALUATION_CLASSIFICATION_RE = re.compile(
    r"\*\*Classification:\*\*[ \t]*(USEFUL|NEUTRAL|HARMFUL|UNKNOWN)\b",
    re.IGNORECASE,
)
EMPTY_MARKERS = ("TBD", "TODO", "TO BE DEFINED", "FILL THIS", "PLACEHOLDER")
REVIEW_FINDING_FIELDS = (
    "Severity", "Confidence", "Priority", "Status", "Affected decision or outcome", "Mechanism ID",
    "Reachability status", "Evidence snapshot and real paths", "Evidence coverage", "Counterevidence checked",
    "Mechanism", "Failure scenario", "Impact", "Recommendation", "Prerequisites and safety gates",
    "Verification", "Owner", "Dependencies", "Residual risk",
)
REVIEW_DECISION_FIELDS = (
    "Mechanism ID", "Reachability status", "Evidence snapshot and real paths", "Evidence coverage",
    "Counterevidence checked", "Failure scenario", "Recommendation", "Prerequisites and safety gates",
    "Verification",
)


def normalize_heading(value: str) -> str:
    value = re.sub(r"`|\*|_", "", value)
    return re.sub(r"\s+", " ", value.strip()).casefold()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(REQUIRED_HEADINGS))
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also reject unresolved markers, empty sections, and missing semantic gates",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable results")
    return parser.parse_args()


def section_bodies(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[normalize_heading(match.group(1))] = text[start:end].strip()
    return result


def subsection_bodies(text: str, level: int = 3) -> list[tuple[str, str]]:
    marker = "#" * level
    matches = list(re.finditer(rf"^{re.escape(marker)}\s+(.+?)\s*$", text, re.MULTILINE))
    result: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match.group(1).strip(), text[start:end].strip()))
    return result


def report(strict: bool, errors: list[str], warnings: list[str], message: str) -> None:
    (errors if strict else warnings).append(message)


def label_value(text: str, label: str) -> str | None:
    match = re.search(
        rf"(?im)^[ \t]*-[ \t]*\*\*{re.escape(label)}:\*\*[ \t]*(.*?)[ \t]*$",
        text,
    )
    return None if match is None else match.group(1).strip()


def require_label_value(
    text: str,
    label: str,
    context: str,
    strict: bool,
    errors: list[str],
    warnings: list[str],
    *,
    reject_choices: bool = False,
) -> str | None:
    value = label_value(text, label)
    if value is None:
        report(strict, errors, warnings, f"{context} must include {label}")
        return None
    if not value:
        report(strict, errors, warnings, f"{context} must provide a value for {label}")
        return value
    if reject_choices and "|" in value:
        report(strict, errors, warnings, f"{context} must select one value for {label}, not retain an option list")
    return value


def validate_snapshot(
    body: str,
    revision_label: str,
    context: str,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    require_label_value(body, "Repository or source", context, strict, errors, warnings)
    require_label_value(body, "Actual paths inspected", context, strict, errors, warnings)
    revision = require_label_value(body, revision_label, context, strict, errors, warnings)
    if not revision:
        return
    if FULL_SHA_RE.search(revision):
        return
    unavailable = re.search(r"REVISION UNAVAILABLE\s*[—:-]\s*(\S.+)", revision, re.IGNORECASE)
    if unavailable:
        return
    report(
        strict,
        errors,
        warnings,
        f"{context} must contain a full 40-character revision or `REVISION UNAVAILABLE — <reason>`",
    )


def has_table_data_row(body: str) -> bool:
    rows = [line for line in body.splitlines() if line.lstrip().startswith("|")]
    return len(rows) >= 3


def validate_safety_section(
    body: str,
    context: str,
    required_headers: Iterable[str],
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    match = re.search(r"(?im)^\*\*Applicability:\*\*[ \t]*(.*?)[ \t]*$", body)
    if match is None:
        report(strict, errors, warnings, f"{context} must declare Applicability as APPLICABLE or NOT APPLICABLE with a reason")
        return
    value = match.group(1).strip()
    if not value or "|" in value or "<reason>" in value.casefold():
        report(strict, errors, warnings, f"{context} must resolve the Applicability choice")
        return
    upper = value.upper()
    if upper.startswith("NOT APPLICABLE"):
        if not re.search(r"NOT APPLICABLE\s*[—:-]\s*\S", value, re.IGNORECASE):
            report(strict, errors, warnings, f"{context} must explain why it is not applicable")
        return
    if not upper.startswith("APPLICABLE"):
        report(strict, errors, warnings, f"{context} Applicability must be APPLICABLE or NOT APPLICABLE")
        return
    for header in required_headers:
        if f"| {header} |".casefold() not in body.casefold():
            report(strict, errors, warnings, f"{context} safety matrix must include the {header} column")
    if strict and not has_table_data_row(body):
        errors.append(f"{context} is applicable but has no handler data row")


def validate_review_findings(
    body: str,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    if "NO MATERIAL FINDINGS" in body.upper():
        return
    findings = [item for item in subsection_bodies(body) if item[0].casefold().startswith("finding")]
    if not findings:
        report(strict, errors, warnings, "review must contain at least one `### Finding ...` block or state `No material findings.`")
        return
    for title, finding in findings:
        for field in REVIEW_FINDING_FIELDS:
            if label_value(finding, field) is None:
                report(strict, errors, warnings, f"{title} must include {field}")
        for field in REVIEW_DECISION_FIELDS:
            value = label_value(finding, field)
            if value is not None and not value:
                report(strict, errors, warnings, f"{title} must provide a value for {field}")


def validate_review_semantics(
    bodies: dict[str, str],
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    snapshot = bodies.get(normalize_heading("Reproducibility Snapshot"), "")
    validate_snapshot(snapshot, "Repository revision", "review reproducibility snapshot", strict, errors, warnings)

    quantitative = bodies.get(normalize_heading("Quantitative Claims and Commands"), "")
    has_command = "```" in quantitative
    no_claims = "NO QUANTITATIVE CLAIMS WERE USED" in quantitative.upper()
    if not has_command and not no_claims:
        report(
            strict,
            errors,
            warnings,
            "review must include reproducible commands for quantitative claims or state `No quantitative claims were used.`",
        )

    validate_review_findings(bodies.get(normalize_heading("Findings"), ""), strict, errors, warnings)

    maturity = bodies.get(normalize_heading("Maturity Assessment"), "")
    if "MATURITY RATING:" not in maturity.upper():
        report(strict, errors, warnings, "maturity assessment must declare `Maturity rating: NOT RATED` or show a scored rubric")
    elif "NOT RATED" not in maturity.upper():
        required_tokens = ("| O |", "| S |", "| D |", "| A |", "| R |", "| L |")
        if not all(token in maturity for token in required_tokens):
            report(strict, errors, warnings, "a rated maturity assessment must include all O/S/D/A/R/L dimension rows")


def validate_repair_semantics(
    bodies: dict[str, str],
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    snapshot = bodies.get(normalize_heading("Reproducibility Snapshot"), "")
    validate_snapshot(snapshot, "Repository revision", "repair reproducibility snapshot", strict, errors, warnings)

    inventory = bodies.get(normalize_heading("Mechanism and Storage-Role Inventory"), "")
    for token, label in (("| Mechanism ID |", "mechanism table"), ("| Store or table |", "storage-role table")):
        if token.casefold() not in inventory.casefold():
            report(strict, errors, warnings, f"repair inventory must include a {label}")

    affected = bodies.get(normalize_heading("Affected-Data Analysis"), "")
    if "```" not in affected and "NO AFFECTED-DATA QUERY WAS RUN" not in affected.upper():
        report(
            strict,
            errors,
            warnings,
            "repair affected-data analysis must include reproducible commands/queries or state `No affected-data query was run — <reason>.`",
        )

    safety = bodies.get(normalize_heading("Retry, Replay, and Reprocessing Safety"), "")
    validate_safety_section(
        safety,
        "repair retry/replay safety",
        ("Handler", "Stable operation identity", "Duplicate detection", "Error propagation", "Progress accounting", "Completion rule", "Status"),
        strict,
        errors,
        warnings,
    )


def validate_implementation_semantics(
    bodies: dict[str, str],
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    snapshot = bodies.get(normalize_heading("Reproducibility Snapshot"), "")
    validate_snapshot(snapshot, "Base revision", "implementation reproducibility snapshot", strict, errors, warnings)

    inventory = bodies.get(normalize_heading("Mechanism, Storage, Dependency, and Compatibility Inventory"), "")
    for token, label in (
        ("| Mechanism ID |", "mechanism and storage-role table"),
        ("| Module or component |", "dependency and runtime-wiring table"),
        ("| Mode or flag |", "compatibility and fallback table"),
    ):
        if token.casefold() not in inventory.casefold():
            report(strict, errors, warnings, f"implementation inventory must include a {label}")

    safety = bodies.get(normalize_heading("Retry, Replay, and Partial-Failure Safety"), "")
    validate_safety_section(
        safety,
        "implementation retry/replay safety",
        ("Handler", "Stable identity", "Deduplication", "Error propagation", "Progress accounting", "Completion rule", "Status"),
        strict,
        errors,
        warnings,
    )

    validation = bodies.get(normalize_heading("Validation Results"), "")
    if "```" not in validation and "VALIDATION NOT RUN" not in validation.upper():
        report(
            strict,
            errors,
            warnings,
            "implementation validation results must include exact commands or state `Validation not run — <reason>.`",
        )


def validate_evaluation_semantics(
    bodies: dict[str, str],
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    executive = bodies.get(normalize_heading("Executive Decision"), "")
    if not EVALUATION_CLASSIFICATION_RE.search(executive):
        report(strict, errors, warnings, "evaluation executive decision must declare Classification as USEFUL, NEUTRAL, HARMFUL, or UNKNOWN")

    counterfactual = bodies.get(normalize_heading("Counterfactual and Assignment"), "")
    for label in ("Design", "Unit of assignment", "Assignment method", "Assignment versus activation handling", "Reviewer blinding or independent outcome source"):
        require_label_value(counterfactual, label, "evaluation counterfactual", strict, errors, warnings, reject_choices=(label == "Design"))

    metric = bodies.get(normalize_heading("Primary Metric and Equivalence Band"), "")
    for label in (
        "Primary metric", "Direction", "Minimum practically meaningful effect (delta)", "Observation window",
        "Outcome maturity rule", "Minimum mature observations per arm",
    ):
        require_label_value(metric, label, "evaluation metric protocol", strict, errors, warnings, reject_choices=(label == "Direction"))

    guardrails = bodies.get(normalize_heading("Guardrails and Stop Conditions"), "")
    require_label_value(guardrails, "Hard guardrails", "evaluation guardrails", strict, errors, warnings)
    require_label_value(
        guardrails,
        "Treatment-arm classification rule",
        "evaluation guardrails",
        strict,
        errors,
        warnings,
    )
    require_label_value(guardrails, "Control-arm handling", "evaluation guardrails", strict, errors, warnings)

    maturity = bodies.get(normalize_heading("Data Quality and Outcome Maturity"), "")
    require_label_value(maturity, "Outcome maturity", "evaluation data quality", strict, errors, warnings)
    require_label_value(maturity, "Independent outcome source", "evaluation data quality", strict, errors, warnings)


def validate(mode: str, path: Path, strict: bool) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.is_file():
        return {"valid": False, "errors": [f"file not found: {path}"], "warnings": []}

    text = path.read_text(encoding="utf-8")
    headings = {normalize_heading(h) for h in HEADING_RE.findall(text)}
    missing = [h for h in REQUIRED_HEADINGS[mode] if normalize_heading(h) not in headings]
    if missing:
        errors.append("missing required headings: " + ", ".join(missing))

    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    if placeholders:
        errors.append("unresolved placeholders: " + ", ".join(placeholders))

    bodies = section_bodies(text)
    if strict:
        upper = text.upper()
        unresolved = [marker for marker in EMPTY_MARKERS if marker in upper]
        if unresolved:
            errors.append("unresolved markers: " + ", ".join(unresolved))

        empty = [h for h in REQUIRED_HEADINGS[mode] if len(bodies.get(normalize_heading(h), "")) < 20]
        if empty:
            errors.append("empty or underspecified sections: " + ", ".join(empty))

    validators = {
        "review": validate_review_semantics,
        "repair": validate_repair_semantics,
        "implementation": validate_implementation_semantics,
        "evaluation": validate_evaluation_semantics,
    }
    if mode in validators:
        validators[mode](bodies, strict, errors, warnings)

    if "UNKNOWN" not in text.upper() and mode in {"design", "review", "plan", "repair", "implementation", "evaluation"}:
        warnings.append("artifact does not explicitly discuss unknowns")
    if "EVIDENCE" not in text.upper():
        warnings.append("artifact does not explicitly discuss evidence")
    if "VERIFICATION" not in text.upper() and mode not in {"operations", "data-contract", "evaluation"}:
        warnings.append("artifact does not explicitly discuss verification")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    args = parse_args()
    result = validate(args.mode, args.path, args.strict)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        for item in result["errors"]:
            print(f"ERROR: {item}", file=sys.stderr)
        for item in result["warnings"]:
            print(f"WARNING: {item}", file=sys.stderr)
        if result["valid"]:
            print(f"valid: {args.path}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
