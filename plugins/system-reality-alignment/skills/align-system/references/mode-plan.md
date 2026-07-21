# Planning Mode

## Objective

Convert alignment gaps into a staged, evidence-driven change program that reduces risk while preserving service and data integrity.

## Procedure

1. State the target decisions and measurable outcomes.
2. Establish the current baseline and known evidence gaps.
3. Group work by source mechanism, not by downstream symptom.
4. Sequence instrumentation and observe-only controls before enforcement.
5. Identify dependencies across producers, consumers, schemas, teams, and external systems.
6. Define migration states, mixed-version compatibility, replay, backfill, reconciliation, rollback, and deprecation.
7. Assign semantic and technical ownership.
8. Define milestones with observable acceptance criteria.
9. Add guardrails and metrics that show whether each stage improved reality alignment.
10. Include explicit stop, rollback, and escalation conditions.

## Required deliverable

Use `assets/templates/plan.md` and include:

- target state and measurable outcomes;
- baseline and gap map;
- principles and non-goals;
- workstreams;
- sequencing and dependency graph;
- milestones and acceptance criteria;
- migration, backfill, reconciliation, rollout, and rollback;
- ownership and governance;
- risks, assumptions, and decision log;
- operating metrics after delivery.

## Sequencing pattern

Prefer:

```text
instrument → baseline → observe-only checks → source fix → compatibility → backfill/reconcile → staged enforcement → outcome review
```

Avoid beginning with broad historical cleanup or hard enforcement before the production mechanism and legitimate exceptions are understood.
