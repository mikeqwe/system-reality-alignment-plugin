# Review Mode

## Objective

Assess an existing system using repository and operational evidence, identify where the internal model diverges from reality, and produce prioritized, testable findings.

## Procedure

1. Establish scope, target decisions, and expected real-world outcomes.
2. Inspect architecture, schemas, state machines, event definitions, APIs, jobs, tests, telemetry, runbooks, incident history, and manual procedures.
3. Build an evidence inventory and mark inaccessible evidence.
4. Map the actual feedback loop, including human steps and external systems.
5. Trace at least one normal case and material failure case end to end.
6. Review semantic separation, source authority, time, identity, uncertainty, contracts, invariants, lineage, idempotency, reconciliation, and outcome verification.
7. Identify failure mechanisms, not stylistic preferences.
8. Rank findings by severity, confidence, blast radius, detectability, and time to correction.
9. Recommend source-level changes with concrete verification criteria.
10. State review limitations and residual unknowns.

## Required deliverable

Use `assets/templates/review.md` and include:

- executive assessment;
- evidence inventory;
- feedback-loop map;
- findings with evidence, mechanism, scenario, impact, recommendation, and verification;
- strengths worth preserving;
- prioritized actions;
- unavailable evidence and review limitations;
- residual risks and owners.

## Review discipline

- Cite repository paths and line ranges when possible.
- Separate confirmed defects from architectural risks and hypotheses.
- Do not inflate severity to compensate for weak evidence.
- Do not treat missing observability as proof that a failure occurs; treat it as inability to verify.
- Do not approve a system solely because tests pass if tests validate only internal state and not domain outcomes.
