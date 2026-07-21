# Design Mode

## Objective

Define a system whose internal claims, decisions, and actions remain traceable to real observations and verifiable outcomes.

## Procedure

1. Define the real-world process, actors, target decisions, and cost of error.
2. Draw the full feedback loop and identify system boundaries.
3. Define observations before derived state. Specify source, identity, time, confidence, correction, and retention.
4. Define commands, decisions, action attempts, and outcomes as separate records.
5. Assign authority per fact and define conflict resolution.
6. Specify state derivation rules, versions, and recomputation behavior.
7. Define contracts, invariants, idempotency, ordering, and late-data behavior.
8. Define reconciliation and independent outcome signals.
9. Define observability, metrics, alerts, and owned operational actions.
10. Design migration, rollout, rollback, backfill, privacy, and failure recovery.
11. Test the design with adversarial scenarios: duplicate, missing, late, out-of-order, conflicting, corrected, partial, and ambiguous outcomes.

## Required deliverable

Use `assets/templates/design.md` and include:

- context and target decisions;
- scope and boundaries;
- feedback-loop map;
- domain vocabulary;
- observation, state, decision, action, outcome, and correction models;
- time, identity, authority, and uncertainty semantics;
- contracts and invariants;
- reconciliation and outcome verification;
- failure modes;
- observability and metrics;
- security, privacy, and retention implications;
- rollout and validation plan;
- unresolved decisions.

## Design review gate

Reject or revise the design when a critical status cannot be traced to observations, a material action cannot be reconciled, or the system judges success using only data it generated itself.
