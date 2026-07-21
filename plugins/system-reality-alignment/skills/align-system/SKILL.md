---
name: align-system
description: Design, review, plan, repair, implement, operate, or evaluate software and socio-technical systems so observations, data, decisions, actions, and outcomes remain traceable and aligned with reality. Use for architecture and system design, data-quality or state-model problems, observability and feedback loops, incident remediation, migrations, domain contracts, invariants, lineage, reconciliation, decision auditability, adaptive operations, and controlled evaluation of an intervention or this plugin. Do not use for isolated cosmetic edits or local syntax changes with no system-behavior implications.
---

# System Reality Alignment

## Objective

Improve the system's ability to observe what happened, distinguish fact from interpretation, make reproducible decisions, verify real outcomes, and adapt without erasing uncertainty or contradiction.

## Mandatory operating rules

1. Pin the evidence snapshot before material analysis: repository or source identity, exact revision, working-tree state when relevant, inspected paths, tool versions, and commands used for derived values or counts.
2. Read `references/core-standard.md`, `references/evidence-and-risk.md`, and `references/analysis-verification.md` before producing recommendations or changes.
3. Select the appropriate mode and read its procedure:
   - design: `references/mode-design.md`
   - review: `references/mode-review.md`
   - plan: `references/mode-plan.md`
   - repair: `references/mode-repair.md`
   - implementation: `references/mode-implementation.md`
   - operations: `references/mode-operations.md`
   - evaluation: `references/mode-evaluation.md`
4. Label decision-relevant statements as `FACT`, `DERIVED`, `INFERENCE`, `HYPOTHESIS`, `ASSUMPTION`, `UNKNOWN`, or `CONFLICT` when the distinction affects a decision.
5. Never invent ground truth. Missing evidence remains explicit and has an acquisition or verification path.
6. Treat independent mechanisms independently. Do not transfer delivery guarantees, configuration, failure handling, or retry behavior from one producer/channel/consumer path to another because they share a technology or broad label such as “messaging.”
7. Trace the actual execution path before describing a failure scenario. Include retries, exception propagation or swallowing, transaction boundaries, compensation, disable/delete behavior, reconciliation direction, feature flags, and legacy fallbacks.
8. Treat raw observations, commands, derived state, decisions, action attempts, outcomes, corrections, checkpoints, rollback data, and audit history as distinct roles.
9. Preserve event time, observation time, ingestion time, processing time, effective time, source, schema version, and correction history when they matter.
10. Represent unknown, conflicting, late, duplicate, corrected, invalid, stale, and not-applicable information explicitly. Do not collapse them into a generic null or a confident status.
11. Define authority per fact, scope, and effective time. Do not declare a universal source of truth.
12. Do not recommend retries, replay, redelivery, or a dead-letter path as ready to deploy until every affected handler has evidence for idempotency, deduplication, error propagation, progress accounting, completion semantics, and partial-failure safety. Otherwise recommend an audit or prerequisite work and label safety `UNKNOWN`.
13. Verify quantitative claims with reproducible commands and declared counting units. Verify dependency claims across inherited build configuration and runtime wiring. Verify repository provenance with version-control evidence. Verify all active compatibility modes, not only the preferred path.
14. Prefer the smallest intervention that closes a measurable feedback loop. Fix the production mechanism before cleaning downstream symptoms.
15. For code changes, include migrations, compatibility, tests, instrumentation, rollout, rollback, reconciliation, and post-change verification where applicable.
16. Keep conclusions proportional to evidence. Attempt to disprove material findings and record counterevidence before finalizing them.

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
| Evaluation | determining whether an intervention, workflow, agent behavior, or this plugin is useful, neutral, harmful, or still unknown |

Use multiple modes only when the request genuinely spans stages. State the selected mode or sequence at the beginning of the result.

Mode execution boundaries:

- In **review** mode, remain read-only unless the user also requests fixes.
- In **design** or **plan** mode, create the requested design or plan; do not modify production code unless implementation is also requested.
- In **repair** or **implementation** mode, make repository changes when tools and permissions allow; do not stop at recommendations or a speculative plan.
- In **operations** mode, investigate and recommend owned actions; do not perform destructive correction without explicit authorization and a rollback path.
- In **evaluation** mode, do not alter treatment assignment, outcome labels, or control data after observing results. Self-assessment by the evaluated agent is diagnostic evidence, not ground truth.

## Universal workflow

1. **Pin the snapshot.** Record source identity, full revision, working-tree state, real paths, tool versions, and reproducible commands.
2. **Frame the decision loop.** Identify the real-world process, actors, decisions, actions, outcomes, costs of error, and scope boundary.
3. **Inventory mechanisms.** Give each independent producer → transport → storage → consumer path a mechanism ID and its own configuration and guarantees.
4. **Build an evidence and claim ledger.** Record sources, freshness, coverage, authority, contradictions, inaccessible evidence, derived commands, and counterevidence.
5. **Trace execution.** Follow at least one normal path and each material failure path through code, configuration, state changes, compensation, and reconciliation.
6. **Separate semantics and storage roles.** Distinguish observations, commands, live state, projections, rollback data, checkpoints, decisions, actions, outcomes, and corrections. Define time and identity semantics.
7. **Challenge the model.** Look for silent loss, ambiguity, forced certainty, stale state, duplicates, order dependence, untraceable overrides, compatibility branches, and missing independent outcomes. Try to falsify each high-impact finding.
8. **Define controls.** Specify contracts, invariants, lineage, retry/replay prerequisites, reconciliation, decision records, metrics, alerts, and human escalation.
9. **Prioritize intervention.** Rank by expected harm reduction, evidence, reversibility, dependency, effort, and time to feedback.
10. **Execute or specify the change.** Follow repository conventions and minimize unrelated edits.
11. **Verify against reality.** Test technical behavior and the connection between system claims and independently observed outcomes.
12. **Record residual uncertainty.** State what remains unknown, how it could invalidate the result, and the next verification step.

## Output requirements

Every substantial result must include:

- scope, selected mode, source identity, and exact revision or an explicit reason it is unavailable;
- the decision or outcome the system is trying to improve;
- evidence used, evidence missing, and commands used for material derived claims;
- a mechanism inventory and relevant execution-path trace;
- facts separated from interpretations, assumptions, and counterevidence;
- prioritized findings or design decisions;
- verification criteria tied to observable outcomes;
- residual risks, unknowns, and ownership.

Repository citations must use actual paths. Logical aliases are allowed only when mapped to real paths. Counts must state their unit and command. A maturity rating must include the scored rubric and evidence; otherwise report `NOT RATED`.

For durable Markdown artifacts, use the nearest matching template in `assets/templates/`. If the repository has no established location, write to `docs/system-reality/` using a descriptive kebab-case filename. Do not overwrite an existing artifact unless the user requested an update.

The bundled scripts may be used to scaffold, validate, or summarize artifacts. Resolve the absolute directory containing this `SKILL.md`, then run:

```bash
python3 <skill-directory>/scripts/new_artifact.py <mode> --system "<name>" --output <path>
python3 <skill-directory>/scripts/validate_artifact.py <mode> <path> --strict
python3 <skill-directory>/scripts/summarize_evaluations.py <runs.jsonl> --minimum-effect <delta>
```

## Completion gate

Do not call the work complete until:

- the relevant real-world outcome is explicit;
- the evidence snapshot and material commands are reproducible;
- independent mechanisms and compatibility paths are not conflated;
- critical failure scenarios are reachable through the verified execution path or are labeled hypotheses;
- critical claims have evidence, counterevidence review, or explicit uncertainty;
- source authority, storage role, identity, and time semantics are defined for critical facts;
- retry or replay recommendations pass the handler-level safety gate;
- invariants are testable;
- decisions and manual overrides are reproducible;
- reconciliation or an equivalent independent verification path exists and its driving set and blind spots are known;
- rollout and rollback protect data integrity;
- tests cover duplicate, late, out-of-order, conflicting, missing, corrected, retry, and replay inputs when applicable;
- metrics can detect recurrence and measure correction latency;
- maturity and intervention-effect claims have a shown method rather than an unsupported score;
- the artifact or implementation has been validated.
