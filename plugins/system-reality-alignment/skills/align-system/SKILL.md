---
name: align-system
description: Design, review, plan, repair, implement, operate, or evaluate software and socio-technical systems so observations, data, decisions, actions, and outcomes remain traceable and aligned with reality. Use for architecture and system design, data-quality or state-model problems, observability and feedback loops, incident remediation, migrations, domain contracts, invariants, lineage, reconciliation, decision auditability, adaptive operations, and controlled evaluation of an intervention or this plugin. Do not use for isolated cosmetic edits or local syntax changes with no system-behavior implications.
---

# System Reality Alignment

## Objective

Improve the system's ability to observe what happened, distinguish fact from interpretation, make reproducible decisions, verify real outcomes, and adapt without erasing uncertainty or contradiction.

## Mandatory operating rules

1. Pin the evidence snapshot before material analysis: source identity, exact revision, working-tree state when relevant, actual paths, tool versions, and commands behind derived values.
2. Read `references/core-standard.md`, `references/evidence-and-risk.md`, and `references/analysis-verification.md` before producing recommendations or changes.
3. Select the appropriate mode and read its procedure:
   - design: `references/mode-design.md`
   - review: `references/mode-review.md`
   - plan: `references/mode-plan.md`
   - repair: `references/mode-repair.md`
   - implementation: `references/mode-implementation.md`
   - operations: `references/mode-operations.md`
   - evaluation: `references/mode-evaluation.md`
4. Label decision-relevant statements as `FACT`, `DERIVED`, `INFERENCE`, `HYPOTHESIS`, `ASSUMPTION`, `UNKNOWN`, or `CONFLICT`. Never invent ground truth.
5. Isolate independently configured mechanisms and trace actual execution, compensation, reconciliation, feature-flag, and compatibility paths according to `analysis-verification.md`.
6. Keep observations, commands, derived state, decisions, action attempts, outcomes, corrections, live state, checkpoints, rollback data, and audit history semantically distinct.
7. Apply the quantitative-claim, dependency, provenance, and handler-level retry/replay gates in `analysis-verification.md`; unverified replay safety remains `UNKNOWN`.
8. Prefer the smallest intervention that closes a measurable feedback loop. Fix the producing mechanism before cleaning downstream symptoms.
9. For code changes, include applicable compatibility, migration, tests, instrumentation, rollout, rollback, reconciliation, and post-change verification.
10. Keep conclusions proportional to evidence, attempt to falsify material findings, and record residual uncertainty.

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
- In **design** or **plan** mode, do not modify production code unless implementation is also requested.
- In **repair** or **implementation** mode, make repository changes when tools and permissions allow; do not stop at a speculative plan.
- In **operations** mode, do not perform destructive correction without explicit authorization and a rollback path.
- In **evaluation** mode, do not alter assignment, labels, exclusions, or control data after observing results. Self-assessment is not ground truth.

## Universal workflow

1. **Pin the snapshot.** Record source identity, full revision, actual paths, tool context, and reproducible commands.
2. **Frame the decision loop.** Identify the process, actors, decisions, actions, outcomes, costs of error, and scope.
3. **Inventory mechanisms and evidence.** Separate independent paths; record authority, coverage, counterevidence, and inaccessible sources.
4. **Trace execution and semantics.** Follow normal and material failure paths; classify storage roles, identity, time, uncertainty, compatibility, and reconciliation direction.
5. **Challenge the model.** Test reachability, alternative explanations, replay safety, count methods, dependencies, provenance, and outcome independence.
6. **Define and prioritize controls.** Specify contracts, invariants, reconciliation, metrics, escalation, ownership, and prerequisites.
7. **Execute or specify the smallest coherent change.** Follow repository conventions and avoid unrelated edits.
8. **Verify and record uncertainty.** Test technical behavior against independent outcomes and state residual gaps.

## Output requirements

Every substantial result must include:

- scope, selected mode, source identity, and exact revision or an explicit reason it is unavailable;
- the decision or outcome being improved;
- evidence used, missing evidence, and commands behind material derived claims;
- relevant mechanism inventory and execution-path trace;
- facts separated from interpretation, assumptions, and counterevidence;
- prioritized findings or design decisions;
- verification criteria tied to observable outcomes;
- residual risks, unknowns, and ownership.

Use actual repository paths. Counts must state their unit and command. A maturity rating must show its rubric and evidence; otherwise report `NOT RATED`.

For durable Markdown artifacts, use the nearest template in `assets/templates/`. If no location is established, write to `docs/system-reality/` with a descriptive kebab-case name. Do not overwrite an artifact unless requested.

```bash
python3 <skill-directory>/scripts/new_artifact.py <mode> --system "<name>" --output <path>
python3 <skill-directory>/scripts/validate_artifact.py <mode> <path> --strict
python3 <skill-directory>/scripts/summarize_evaluations.py <runs.jsonl> --minimum-effect <delta>
```

## Completion gate

Do not call the work complete until the applicable mode procedure is satisfied and:

- evidence, revisions, paths, and material commands are reproducible;
- mechanisms and compatibility paths are not conflated;
- failure scenarios are verified reachable or labeled as hypotheses;
- retry/replay recommendations pass the handler-level safety gate;
- critical semantics, invariants, reconciliation coverage, rollout, and rollback are defined;
- tests and metrics can detect recurrence and independently verify outcomes;
- maturity and intervention-effect claims show their method;
- the artifact or implementation passes its validator and relevant repository checks.
