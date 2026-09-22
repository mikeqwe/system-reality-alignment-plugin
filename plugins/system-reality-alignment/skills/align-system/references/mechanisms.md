# Trace the mechanism before transferring a guarantee

Use for claims about execution, delivery, durable state, external effects, or recovery. Documentation suggests where to look; the effective path establishes what the implementation does.

## Establish the actual boundary

Trace a concrete caller through the configured path to the effect and its acknowledgement. Include reachable flags, synchronous calls, exception handling, compensation, and legacy fallbacks. Read inherited build/configuration and relevant runtime dependencies when they determine behavior. Do not extrapolate one queue's settings to another producer, topic, consumer, or scheduler that merely shares a framework.

Name storage by role: live process state, derived cache, checkpoint, rollback evidence, or audit history. A durable audit record may not resume a process. A cache miss may not mean absence in the authoritative system. Check tracked history before alleging unknown provenance.

For a claimed failure, identify its preconditions and the reachable sequence. Tests or bounded fault injection can establish possibility; production incidence requires operational evidence. A guard or compensation path may refute the finding. Report inspected coverage rather than implying exhaustive analysis.

## Retries and ambiguous results

Before recommending replay for the affected handlers, locate:

- the external or non-repeatable effect and the identity of the intended operation;
- idempotency/deduplication scope, durability, retention, and behavior under concurrency;
- commit boundaries between the effect, local state, completion marker, and acknowledgement;
- failure propagation, including swallowed errors and progress advanced on failure;
- recovery after a timeout, crash, restart, partial effect, or expired deduplication window.

A new retry attempt ID is not necessarily a stable intent ID. A local transaction cannot roll back an already committed external effect. A timeout can mean the effect occurred but its response was lost. Obtain provider-side confirmation or use a documented idempotent protocol; do not convert uncertainty into permission to repeat the effect.

Scope conclusions to checked paths. A safe projection consumer does not make a payment handler safe. Unknown safety blocks the risky replay, not unrelated useful work. Compensation can itself fail and needs observation; a rollback script does not automatically undo an external outcome.

## Reconciliation has a population

Name the compared claims, matching identity, authority, delay tolerance, and the starting population. Starting from local completed rows cannot detect an external operation whose local row was never committed. Starting from a queue cannot see messages never enqueued. An inner join can hide missing records on either side.

Ask how missing, extra, duplicated, stale, and conflicting records enter the comparison. Use an independent inventory or complementary direction where necessary. If no complete inventory exists, explicitly bound the coverage rather than claim universal recovery.

Define what happens to a mismatch: classify it, preserve evidence, decide under the correct authority, apply an authorized correction, and check affected consumers. Observe overdue/failed corrections as well as detected mismatches. Reconciliation without a correction path only reports an open loop.

## Useful probes

Prefer the cheapest observation that distinguishes the leading explanations: a configured handler registration, an exception-path test, a comparison against a provider export, or a query for missing identities. Preserve revision/environment, query, unit, and time window when they affect reproducibility. A source-file count is not a runtime-handler count.

Use disposable fixtures or explicitly authorized test environments for fault injection. Do not exercise production effects, replay real messages, change access, or fetch private data solely to satisfy a checklist.
