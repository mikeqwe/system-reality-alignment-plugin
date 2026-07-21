# Operations Mode

## Objective

Operate the system as a learning loop: detect divergence, reconcile claims with outcomes, correct state, and improve rules and processes.

## Procedure

1. Review decision-quality, data-quality, reconciliation, and feedback-latency metrics.
2. Investigate breaches by tracing the decision loop, not only the metric pipeline.
3. Separate source defects, transport defects, transformation defects, model defects, business-rule defects, and legitimate exceptions.
4. Review unknown, conflict, correction, and manual-override rates.
5. Sample decisions and verify reproducibility from evidence and logic version.
6. Compare system claims with independent outcomes.
7. Age and assign unresolved discrepancies.
8. Decide whether to contain, repair, change a rule, improve observation, or accept a bounded risk.
9. Update contracts, invariants, runbooks, and ownership when recurring patterns appear.
10. Verify whether prior improvements reduced recurrence and correction latency.

## Required deliverable

Use `assets/templates/operations.md` and include:

- scorecard and period;
- material changes from baseline;
- discrepancies and aging;
- drift and anomaly analysis;
- sampled decision verification;
- incidents and corrections;
- decisions and assigned actions;
- residual risk and next review criteria.

## Operating principle

A dashboard without an owner, threshold, and required action is information display, not a feedback loop.
