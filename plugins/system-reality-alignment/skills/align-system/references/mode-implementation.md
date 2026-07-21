# Implementation Mode

## Objective

Translate an approved alignment design or finding into minimal, testable code, schema, contract, telemetry, migration, and operational changes.

## Procedure

1. Confirm the target decision, invariant, contract, or failure mechanism.
2. Inspect repository conventions and current tests before editing.
3. Define the smallest coherent change and its compatibility boundary.
4. Implement observation, lineage, time, identity, uncertainty, and version semantics explicitly.
5. Preserve raw evidence and avoid destructive mutation when corrections or replay matter.
6. Implement idempotency, retry, ambiguous-result, and partial-failure behavior for side effects.
7. Add executable invariants at the appropriate layer.
8. Add tests for normal, duplicate, late, out-of-order, missing, conflicting, corrected, retry, rollback, and replay cases as applicable.
9. Add domain-level telemetry and reconciliation, not only infrastructure metrics.
10. Add migration, backfill, rollout, rollback, and cleanup steps.
11. Run the relevant test, lint, type, migration, and validation commands.
12. Compare the implementation to observable acceptance criteria and document residual gaps.

## Required deliverable

When code is changed, provide:

- concise change summary;
- files and contracts changed;
- semantic decisions;
- migration and compatibility behavior;
- tests and commands run;
- telemetry and operational response;
- rollout and rollback;
- unresolved risks.

For a durable specification, use `assets/templates/implementation.md`.

## Implementation guardrails

- Do not create a new canonical status without defining derivation and correction.
- Do not silently coerce invalid or conflicting inputs.
- Do not backfill with logic that cannot be versioned or reproduced.
- Do not rely on an asynchronous side effect without idempotency or reconciliation.
- Do not remove old evidence until retention, migration, and audit needs are satisfied.
- Do not declare success based only on unit tests when real outcome verification is required.
