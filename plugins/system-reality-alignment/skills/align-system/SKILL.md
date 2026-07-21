---
name: align-system
description: Design, review, plan, repair, implement, or operate software and socio-technical systems so observations, data, decisions, actions, and outcomes remain traceable and aligned with reality. Use for architecture and system design, data-quality or state-model problems, observability and feedback loops, incident remediation, migrations, domain contracts, invariants, lineage, reconciliation, decision auditability, and adaptive operations. Do not use for isolated cosmetic edits or local syntax changes with no system-behavior implications.
---

# System Reality Alignment

## Objective

Improve the system's ability to observe what happened, distinguish fact from interpretation, make reproducible decisions, verify real outcomes, and adapt without erasing uncertainty or contradiction.

## Mandatory operating rules

1. Inspect the available repository, diagrams, schemas, events, logs, tests, runbooks, incidents, and user-provided evidence before making material claims.
2. Read `references/core-standard.md` and `references/evidence-and-risk.md` before producing recommendations or changes.
3. Select the appropriate mode and read its procedure:
   - design: `references/mode-design.md`
   - review: `references/mode-review.md`
   - plan: `references/mode-plan.md`
   - repair: `references/mode-repair.md`
   - implementation: `references/mode-implementation.md`
   - operations: `references/mode-operations.md`
4. Label material statements as `FACT`, `DERIVED`, `INFERENCE`, `HYPOTHESIS`, `ASSUMPTION`, `UNKNOWN`, or `CONFLICT` when the distinction affects a decision.
5. Never invent ground truth. When evidence is missing, continue with explicit assumptions and define how to verify them.
6. Treat raw observations, derived state, decisions, actions, and outcomes as separate entities.
7. Preserve event time, observation time, ingestion time, processing time, source, schema version, and correction history when they matter.
8. Represent unknown, conflicting, late, duplicate, corrected, and not-applicable information explicitly. Do not collapse them into a generic null or a confident status.
9. Define authority per fact. Do not declare a universal source of truth without specifying the exact fact, time, and scope for which the source is authoritative.
10. Prefer the smallest intervention that closes a measurable feedback loop. Fix the production mechanism before cleaning downstream symptoms.
11. For code changes, include migrations, compatibility, tests, instrumentation, rollout, rollback, reconciliation, and post-change verification where applicable.
12. Keep conclusions proportional to evidence. Report residual uncertainty and risks.

## Mode selection

Choose the mode from the user's intended outcome, not from the artifact name alone.

| Mode | Use when the primary outcome is |
|---|---|
| Design | defining a new system, domain model, data flow, decision loop, or major redesign |
| Review | assessing an existing system and producing evidence-backed findings |
| Plan | sequencing improvements, migrations, ownership, milestones, and acceptance criteria |
| Repair | containing and permanently correcting a failure, inconsistency, incident, or corrupted state |
| Implementation | changing code, schemas, contracts, tests, telemetry, or runbooks |
| Operations | monitoring alignment, investigating drift, reconciling outcomes, and deciding follow-up actions |

Use multiple modes only when the request genuinely spans stages. State the selected mode or sequence at the beginning of the result.

Mode execution boundaries:

- In **review** mode, remain read-only unless the user also requests fixes.
- In **design** or **plan** mode, create the requested design or plan; do not modify production code unless implementation is also requested.
- In **repair** or **implementation** mode, make the repository changes when tools and permissions allow; do not stop at recommendations or a speculative plan.
- In **operations** mode, investigate and recommend owned actions; do not perform destructive correction without explicit authorization and a rollback path.

## Universal workflow

1. **Frame the decision loop.** Identify the real-world process, actors, decisions, actions, outcomes, costs of error, and scope boundary.
2. **Map the loop.** Trace `reality → observation → capture → transport → storage → interpretation → decision → action → outcome → reconciliation → learning`.
3. **Build an evidence inventory.** Record sources, freshness, coverage, ownership, authority, contradictions, and inaccessible evidence.
4. **Separate semantics.** Distinguish observations, commands, derived state, decisions, actions, outcomes, and corrections. Define time and identity semantics.
5. **Find gaps and failure modes.** Look for silent loss, ambiguity, forced certainty, stale state, duplicates, order dependence, untraceable overrides, weak incentives, and missing independent outcomes.
6. **Define controls.** Specify contracts, invariants, lineage, reconciliation, decision records, metrics, alerts, and human escalation.
7. **Prioritize intervention.** Rank by expected harm reduction, evidence, reversibility, dependency, effort, and time to feedback.
8. **Execute or specify the change.** Follow repository conventions. Minimize unrelated edits.
9. **Verify against reality.** Test both technical behavior and the connection between system claims and independently observed outcomes.
10. **Record residual uncertainty.** State what remains unknown, how it could invalidate the result, and the next verification step.

## Output requirements

Every substantial result must include:

- scope and selected mode;
- the decision or outcome the system is trying to improve;
- evidence used and evidence missing;
- a map of the relevant feedback loop;
- facts separated from interpretations and assumptions;
- prioritized findings or design decisions;
- verification criteria tied to observable outcomes;
- residual risks, unknowns, and ownership.

For durable Markdown artifacts, use the nearest matching template in `assets/templates/`. If the repository has no established location, write to `docs/system-reality/` using a descriptive kebab-case filename. Do not overwrite an existing artifact unless the user requested an update.

The bundled scripts may be used to scaffold or validate artifacts. Resolve the absolute directory containing this `SKILL.md`, then run:

```bash
python3 <skill-directory>/scripts/new_artifact.py <mode> --system "<name>" --output <path>
python3 <skill-directory>/scripts/validate_artifact.py <mode> <path> --strict
```

## Completion gate

Do not call the work complete until:

- the relevant real-world outcome is explicit;
- critical claims have evidence or are labeled as uncertainty;
- source authority and time semantics are defined for critical facts;
- invariants are testable;
- decisions and manual overrides are reproducible;
- reconciliation or an equivalent independent verification path exists;
- rollout and rollback protect data integrity;
- tests cover duplicate, late, out-of-order, conflicting, missing, and corrected inputs when applicable;
- metrics can detect recurrence and measure correction latency;
- the artifact or implementation has been validated.
