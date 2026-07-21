# Repair Mode

## Objective

Contain active harm, establish what actually happened, correct source and downstream state, and prevent recurrence through verified system changes.

## Procedure

1. Define the incident or inconsistency in terms of affected decisions and real outcomes.
2. Pin the exact revision, deployment/configuration version, operational evidence window, and commands used to identify affected entities.
3. Contain ongoing harm with the most reversible safe control.
4. Preserve evidence before destructive cleanup.
5. Establish a timeline using explicit event, observation, ingestion, processing, effective, and correction times.
6. Separate confirmed facts, derived conclusions, hypotheses, conflicts, and unknowns.
7. Inventory independent mechanisms and trace the failure through the actual path, including exception swallowing, retries, transaction boundaries, compensation, feature flags, and legacy fallbacks.
8. Verify the role of each state store and the driving set and blind spots of every reconciliation job involved.
9. Quantify affected entities with reproducible queries and identify false negatives as well as visible failures.
10. Before replay, retry, DLT redelivery, or batch reprocessing, complete the handler-level safety gate in `analysis-verification.md`. Correct non-idempotent progress accounting and swallowed failures first.
11. Correct the source mechanism; do not stop at downstream data repair.
12. Design reconciliation, backfill, compensation, notification, and audit trail with deduplication and restart-safe progress.
13. Add regression tests, invariants, telemetry, and owned alerts.
14. Stage rollout and verify against independent outcomes.
15. Record residual uncertainty, follow-up actions, and evidence-retention needs.

## Required deliverable

Use `assets/templates/repair.md` and include:

- incident statement and impact;
- evidence snapshot and containment;
- timeline and actual execution path;
- mechanism and storage-role inventory;
- causal mechanism and counterevidence;
- affected-data query and coverage limits;
- retry/replay safety matrix when reprocessing is involved;
- source fix;
- correction, reconciliation, compensation, and backfill;
- tests and observability;
- rollout and rollback;
- verification and closure criteria;
- residual risk and follow-up ownership.

## Closure gate

Do not close the repair because the visible symptom disappeared. Closure requires evidence that:

- the source mechanism is removed or bounded;
- replayed or retried handlers are proven safe for duplicates and partial failure;
- affected state was reconciled from a driving set that covers the failure population;
- downstream consumers received corrections;
- recurrence is detectable;
- an independent outcome confirms recovery.
