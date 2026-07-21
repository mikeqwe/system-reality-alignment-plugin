# Repair Mode

## Objective

Contain active harm, establish what actually happened, correct source and downstream state, and prevent recurrence through verified system changes.

## Procedure

1. Define the incident or inconsistency in terms of affected decisions and real outcomes.
2. Contain ongoing harm with the most reversible safe control.
3. Preserve evidence before destructive cleanup.
4. Establish a timeline using explicit event, observation, ingestion, processing, and correction times.
5. Separate confirmed facts, derived conclusions, hypotheses, conflicts, and unknowns.
6. Trace the failure mechanism through the full feedback loop.
7. Quantify affected entities and identify false negatives as well as visible failures.
8. Correct the source mechanism; do not stop at downstream data repair.
9. Design reconciliation, backfill, compensation, notification, and audit trail.
10. Add regression tests, invariants, telemetry, and owned alerts.
11. Stage rollout and verify against independent outcomes.
12. Record residual uncertainty, follow-up actions, and evidence-retention needs.

## Required deliverable

Use `assets/templates/repair.md` and include:

- incident statement and impact;
- containment;
- evidence and timeline;
- causal mechanism;
- affected-data analysis;
- source fix;
- correction, reconciliation, compensation, and backfill;
- tests and observability;
- rollout and rollback;
- verification and closure criteria;
- residual risk and follow-up ownership.

## Closure gate

Do not close the repair because the visible symptom disappeared. Closure requires evidence that:

- the source mechanism is removed or bounded;
- affected state was reconciled;
- downstream consumers received corrections;
- recurrence is detectable;
- an independent outcome confirms recovery.
