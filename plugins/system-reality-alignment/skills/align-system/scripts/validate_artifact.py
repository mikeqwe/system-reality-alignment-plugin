#!/usr/bin/env python3
"""Validate required structure in a System Reality Alignment Markdown artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

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
        "Incident or Inconsistency Statement", "Impact and Affected Outcomes", "Immediate Containment", "Evidence Inventory",
        "Timeline", "Facts, Conflicts, Hypotheses, and Unknowns", "Causal Mechanism", "Affected-Data Analysis",
        "Source-Level Fix", "Data Correction and Reconciliation", "Regression Tests and Invariants",
        "Observability and Recurrence Detection", "Rollout and Rollback", "Verification and Closure Criteria",
        "Residual Risk and Follow-Up Owners",
    ],
    "implementation": [
        "Objective and Acceptance Criteria", "Scope and Non-Goals", "Current Behavior and Evidence",
        "Proposed Semantic Changes", "Contracts, Schemas, and Versions", "Identity and Time Semantics",
        "Unknown, Conflict, and Correction Handling", "Invariants and Enforcement Points",
        "Idempotency, Retry, and Partial Failure", "Code and Data Changes", "Migration and Backfill", "Test Matrix",
        "Telemetry, Reconciliation, and Alerts", "Rollout, Stop Conditions, and Rollback", "Validation Results",
        "Residual Risks and Unknowns",
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
    r"\*\*Classification:\*\*\s*(USEFUL|NEUTRAL|HARMFUL|UNKNOWN)\b",
    re.IGNORECASE,
)
EMPTY_MARKERS = ("TBD", "TODO", "TO BE DEFINED", "FILL THIS", "PLACEHOLDER")


def normalize_heading(value: str) -> str:
    value = re.sub(r"`|\*|_", "", value)
    return re.sub(r"\s+", " ", value.strip()).casefold()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(REQUIRED_HEADINGS))
    parser.add_argument("path", type=Path)
    parser.add_argument("--strict", action="store_true", help="Also reject unresolved markers, empty sections, and missing reproducibility gates")
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


def validate_review_semantics(text: str, bodies: dict[str, str], strict: bool, errors: list[str], warnings: list[str]) -> None:
    snapshot = bodies.get(normalize_heading("Reproducibility Snapshot"), "")
    has_revision = bool(FULL_SHA_RE.search(snapshot))
    revision_unavailable = "REVISION UNAVAILABLE" in snapshot.upper()
    if not has_revision and not revision_unavailable:
        message = "review reproducibility snapshot must contain a full 40-character revision or REVISION UNAVAILABLE with a reason"
        (errors if strict else warnings).append(message)

    quantitative = bodies.get(normalize_heading("Quantitative Claims and Commands"), "")
    has_command = "```" in quantitative
    no_quantitative_claims = "NO QUANTITATIVE CLAIMS WERE USED" in quantitative.upper()
    if not has_command and not no_quantitative_claims:
        message = "review must include reproducible commands for quantitative claims or state that no quantitative claims were used"
        (errors if strict else warnings).append(message)

    for field in ("Mechanism ID:", "Reachability status:", "Counterevidence checked:", "Prerequisites and safety gates:"):
        if field.casefold() not in text.casefold():
            message = f"review findings must include {field.rstrip(':')}"
            (errors if strict else warnings).append(message)

    maturity = bodies.get(normalize_heading("Maturity Assessment"), "")
    if "MATURITY RATING:" not in maturity.upper():
        message = "maturity assessment must declare Maturity rating: NOT RATED or show a scored rubric"
        (errors if strict else warnings).append(message)
    elif "NOT RATED" not in maturity.upper():
        required_tokens = ("| O |", "| S |", "| D |", "| A |", "| R |", "| L |")
        if not all(token in maturity for token in required_tokens):
            message = "a rated maturity assessment must include all O/S/D/A/R/L dimension rows"
            (errors if strict else warnings).append(message)


def validate_evaluation_semantics(text: str, strict: bool, errors: list[str], warnings: list[str]) -> None:
    if not EVALUATION_CLASSIFICATION_RE.search(text):
        message = "evaluation must declare Classification as USEFUL, NEUTRAL, HARMFUL, or UNKNOWN"
        (errors if strict else warnings).append(message)
    required_phrases = (
        "minimum practically meaningful effect",
        "counterfactual",
        "guardrail",
        "outcome maturity",
    )
    for phrase in required_phrases:
        if phrase.casefold() not in text.casefold():
            message = f"evaluation does not explicitly define {phrase}"
            (errors if strict else warnings).append(message)


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

    if mode == "review":
        validate_review_semantics(text, bodies, strict, errors, warnings)
    if mode == "evaluation":
        validate_evaluation_semantics(text, strict, errors, warnings)

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
