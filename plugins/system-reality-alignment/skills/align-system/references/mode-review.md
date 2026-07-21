# Review Mode

## Objective

Assess an existing system using reproducible repository and operational evidence, identify where its internal model diverges from reality, and produce prioritized, testable findings without conflating independent mechanisms or imagined failure paths.

## Procedure

1. Establish scope, target decisions, expected real-world outcomes, and the cost of error.
2. Pin the evidence snapshot: repository, full commit identifier, working-tree state, tools, actual paths, commands, and operational evidence window.
3. Inventory architecture, schemas, state machines, APIs, domain-event paths, background-job paths, migrations, tests, telemetry, runbooks, incidents, and manual procedures.
4. Assign a mechanism ID to each independent producer → transport → consumer path. Record its own configuration, delivery, retry, acknowledgement, failure, and deduplication semantics.
5. Build an evidence inventory and claim ledger. Mark inaccessible evidence and record counterevidence.
6. Trace at least one normal case and each material failure case end to end through synchronous calls, persistence, transactions, retries, exception handling, compensation, state changes, and reconciliation.
7. Verify reconciliation direction, driving set, join keys, and blind spots. Do not claim it can find entities absent from the source it enumerates.
8. Classify each material store as live state, projection, rollback data, history, checkpoint, progress accounting, cache, outbox/inbox, or quarantine from actual read/write paths.
9. Review semantic separation, authority, time, identity, uncertainty, contracts, invariants, lineage, decision reproducibility, and outcome verification.
10. Audit handler-level replay safety before recommending retry, redelivery, DLT replay, or reprocessing. Unknown handler behavior blocks a ready-to-deploy recommendation.
11. Verify quantitative claims with included commands and explicit units. Verify dependency claims across inherited build configuration and runtime wiring. Verify repository provenance and all active compatibility or fallback paths.
12. Identify observable failure mechanisms, not stylistic preferences. A scenario not proven reachable is a `HYPOTHESIS`, not a confirmed defect.
13. Attempt to disprove every critical or high finding and every recommendation with material migration risk. Record the counterevidence checked.
14. Rank findings by severity, confidence, blast radius, detectability, time to correction, and evidence coverage.
15. Recommend source-level changes with prerequisites, compatibility, rollout, rollback, and observable verification criteria.
16. Score maturity only with the rubric and cited evidence in `evidence-and-risk.md`; otherwise state `Maturity rating: NOT RATED`.
17. State review limitations, residual unknowns, and claims withdrawn or narrowed during adversarial verification.

## Required deliverable

Use `assets/templates/review.md` and include:

- executive assessment;
- reproducibility snapshot with the full revision;
- scope and target decisions;
- mechanism inventory;
- evidence and claim ledger;
- actual execution-path traces;
- reconciliation direction and blind spots;
- storage-role, dependency, and compatibility model;
- feedback-loop map;
- quantitative claims with commands;
- findings with evidence, counterevidence, mechanism, reachable scenario, impact, recommendation, prerequisites, and verification;
- strengths worth preserving;
- maturity scorecard or `NOT RATED`;
- prioritized actions;
- unavailable evidence, review limitations, and residual risks.

## Review discipline

- Cite real repository paths and line ranges when possible.
- Do not use logical path aliases without mapping them to real paths.
- Separate confirmed defects, architectural risks, hypotheses, and unknowns.
- Do not inflate severity to compensate for weak evidence.
- Do not treat missing observability as proof that a failure occurs; treat it as inability to verify.
- Do not transfer guarantees between domain events and background jobs, or between any other independently configured paths.
- Do not describe a retry or replay change as safe because “most handlers” appear idempotent; show coverage for every affected handler.
- Do not use a file count as a class or endpoint count without proving the counting unit.
- Do not call tracked artifacts of unknown provenance without checking version-control history.
- Do not describe only the preferred storage or execution mode when a legacy or feature-flag fallback remains active.
- Do not approve a system solely because tests pass if tests validate only internal state and not domain outcomes.
