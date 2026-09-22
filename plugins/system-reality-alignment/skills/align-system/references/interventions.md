# From a mismatch to a better system

Choose the intervention for the requested result. Do not turn a small task into a mandatory lifecycle.

| Requested work | Useful deliverable |
| --- | --- |
| Design | A minimal domain model, important contracts, uncertainty behavior, and a way to observe and correct wrong outcomes. Proposed guarantees remain untested. |
| Review | Ranked, source-backed reachable findings, preserved controls, and important coverage limits. No code changes unless requested. |
| Plan | Dependency-aware changes with concrete acceptance observations, costs, ownership, and decision points. |
| Repair | Authorized containment, source-mechanism correction, affected-state reconciliation, and recurrence detection. |
| Implementation | The scoped code/contract/test change, compatibility and recovery behavior, and checks actually run. |
| Operations | A discrepancy population, age/impact, owner, response, and confirmation that correction reached the outcome. |
| Evaluation | A comparison against a defined baseline with independent outcome evidence, costs, and explicit uncertainty. |

## Pick the next useful action

Rank by consequence, credible reachability, affected population, reversibility, and detection/correction delay. Use qualitative judgments when frequency is unknown; do not fabricate probability scores. Consider an observation-only change or no change alongside larger redesigns.

Connect the proposal to a falsifiable expectation:

> Because mechanism M loses or misinterprets observation O, decision D can be wrong. Change C should alter observable result R under condition T. Observation F would disconfirm this explanation.

This is a reasoning aid, not compulsory output syntax. Prefer correcting the producer and closing the feedback path over repeatedly cleaning its symptoms. Do not require an upstream fix before urgent, authorized containment.

## Change safely where relevant

For behavioral or data changes, examine the affected contracts and consumers. Cover mixed versions, default behavior, historical state, and rollback when they apply. A new invariant may expose legitimate exceptions: use bounded observation or a staged rollout before enforcement when warranted, rather than silently discarding violations.

Keep accepted intent distinct from confirmed outcome during partial failures. Retain evidence needed to reconcile uncertain effects. A backfill needs a source population, transformation version, duplicate policy, checkpoints, and a way to detect incorrect corrections. Reversal of code and reversal of data/effects are separate questions.

The task's authorization sets the action boundary. Prefer a reviewable local patch and disposable checks; do not automatically deploy, send external commands, or modify production data. Conversely, finish already-authorized implementation work rather than repeatedly asking permission for its ordinary local steps.

## Check the mechanism and the outcome separately

Choose tests that could fail if the claimed fix is wrong, including the relevant failure boundary. Existing happy-path tests may be insufficient; adding unrelated tests is not the goal. Report the command, result, and what it establishes. A test built from the same mistaken model may pass: compare contracts or independently observed outcomes when available.

A local regression test establishes bounded behavior, not production improvement. When effects arrive later, state the expected observation, where it will come from, when it is meaningful, and the responsible role (unassigned if unknown). Never invent an owner, monitoring process, or measurement already performed.

For intervention evaluation, keep task/model/effort/tool access comparable. Measure wrong claims, unsafe changes, missed defects, needless changes, and human review burden alongside success. Do not treat self-assessed confidence, report length, or passing document checks as effectiveness. Without an adequate comparison, the effect is unknown; lack of visible benefit is not evidence of equivalence.

## Handoff without a second bureaucracy

Prefer the existing PR, issue, test, or runbook. Preserve the few facts a later reader needs: boundary/revision, mismatch and evidence, decision or change, verification, and unresolved consequential questions. Do not create a parallel ledger or a repository-wide architecture map unless it solves an actual task need.
