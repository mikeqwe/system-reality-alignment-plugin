# Implementation Mode

## Objective

Translate an approved alignment design or finding into minimal, testable code, schema, contract, telemetry, migration, and operational changes.

## Procedure

1. Confirm the target decision, invariant, contract, or verified failure mechanism and pin the base revision.
2. Inspect repository conventions, inherited build configuration, runtime wiring, active feature flags, compatibility paths, and current tests before editing.
3. Identify the exact mechanism and execution path being changed; do not modify a similarly named but independent path.
4. Define the smallest coherent change and its compatibility boundary.
5. Implement observation, lineage, storage-role, time, identity, uncertainty, and version semantics explicitly.
6. Preserve raw evidence and avoid destructive mutation when corrections or replay matter.
7. Before enabling retry, replay, redelivery, or a DLT, audit every affected handler for stable identity, duplicate detection, side effects, transaction boundary, error propagation, progress accounting, completion rules, ambiguous results, ordering, and restart safety.
8. Implement idempotency, retry, ambiguous-result, and partial-failure behavior for side effects. Do not increment success progress after a swallowed failure.
9. Add executable invariants at the appropriate layer.
10. Add tests for normal, duplicate, late, out-of-order, missing, conflicting, corrected, retry, rollback, repeated-part, partial-failure, and replay cases as applicable.
11. Add domain-level telemetry and reconciliation, not only infrastructure metrics. Verify the reconciliation driving set covers the target population.
12. Add migration, backfill, mixed-version operation, rollout, rollback, and cleanup steps.
13. Run and record the relevant test, lint, type, dependency-resolution, migration, count, and validation commands.
14. Compare the implementation to observable acceptance criteria and document residual gaps.

## Required deliverable

When code is changed, provide:

- concise change summary and base revision;
- mechanism and files changed;
- semantic and storage-role decisions;
- dependency, feature-flag, and compatibility behavior;
- retry/replay safety evidence when applicable;
- migration and reconciliation behavior;
- tests and exact commands run;
- telemetry and operational response;
- rollout and rollback;
- unresolved risks.

For a durable specification, use `assets/templates/implementation.md`.

## Implementation guardrails

- Do not create a new canonical status without defining derivation and correction.
- Do not silently coerce invalid or conflicting inputs.
- Do not backfill with logic that cannot be versioned or reproduced.
- Do not rely on an asynchronous side effect without idempotency or reconciliation.
- Do not enable automatic retry when a handler suppresses errors or mutates non-idempotent progress.
- Do not remove old evidence until retention, migration, compatibility, and audit needs are satisfied.
- Do not declare success based only on unit tests when real outcome verification is required.
