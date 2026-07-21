# {{SYSTEM_NAME}} — System Repair and Reconciliation Plan

**Date:** {{DATE}}  
**Mode:** Repair  
**Status:** Draft

## Incident or Inconsistency Statement

## Impact and Affected Outcomes

## Reproducibility Snapshot

- **Repository or source:**
- **Repository revision:** <full 40-character commit SHA, or `REVISION UNAVAILABLE — <reason>`>
- **Deployed revision and configuration:**
- **Branch or tag:**
- **Working tree:**
- **Agent/model and tool versions:**
- **Operational evidence window:**
- **Actual paths inspected:**
- **Commands and queries used:**
- **Unavailable sources:**

## Immediate Containment

## Evidence Inventory

| Evidence ID | Actual path or source | Supports | Mechanism ID | Time coverage | Authority | Independence | Gaps |
|---|---|---|---|---|---|---|---|

## Mechanism and Storage-Role Inventory

### Mechanisms

| Mechanism ID | Purpose | Producer | Channel/API | Effective configuration | Delivery/ack | Consumer | Failure path | Idempotency evidence |
|---|---|---|---|---|---|---|---|---|

### Storage roles

| Store or table | Role | Writers | Readers | Authority scope | Retention/correction behavior |
|---|---|---|---|---|---|

## Timeline

## Facts, Conflicts, Hypotheses, and Unknowns

## Execution-Path Trace and Causal Mechanism

Trace the reachable path from entry through transactions, retries, exception handling, compensation, resulting state, and reconciliation. Record counterevidence that could falsify the mechanism.

## Affected-Data Analysis

- **Population and counting unit:**
- **Coverage and blind spots:**
- **False-negative risk:**
- **Exact commands or queries:**

```text
# reproducible commands or queries
```

## Retry, Replay, and Reprocessing Safety

**Applicability:** APPLICABLE | NOT APPLICABLE — <reason>

When applicable, complete one row per affected handler before enabling retry, replay, redelivery, DLT processing, or batch reprocessing.

| Handler | Stable operation identity | Duplicate detection | Side-effect safety | Transaction boundary | Error propagation | Progress accounting | Completion rule | Replay tests | Status |
|---|---|---|---|---|---|---|---|---|---|

## Source-Level Fix

## Data Correction and Reconciliation

## Compensation, Notification, and Audit

## Regression Tests and Invariants

## Observability and Recurrence Detection

## Rollout and Rollback

## Verification and Closure Criteria

## Residual Risk and Follow-Up Owners
