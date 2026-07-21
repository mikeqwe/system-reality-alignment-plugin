# Analysis Verification and Reproducibility

Use this reference whenever the work makes claims about an existing implementation, runtime behavior, counts, dependencies, delivery guarantees, migration state, retries, compatibility, or maturity.

## 1. Evidence snapshot

Before analysis, record:

```text
Repository or source:
Revision: full immutable identifier, normally a 40-character Git commit SHA
Branch or tag, if relevant:
Working tree: clean, dirty, or unavailable
Analysis date:
Agent and model version, when available:
Tools and versions:
Paths inspected:
Operational evidence window:
Unavailable sources:
```

A branch name is not an immutable revision. A shortened SHA may be convenient in prose, but the artifact MUST contain the full identifier. When a revision cannot be obtained, write `REVISION UNAVAILABLE`, explain why, and lower confidence.

Use actual repository paths. If a diagram or report uses logical path aliases, provide an alias-to-path map.

## 2. Mechanism identity and isolation

Broad labels such as “events,” “messaging,” “queue,” or “migration” can conceal independent systems. Before transferring any property, assign a mechanism ID and fill this card:

| Field | Required evidence |
|---|---|
| Purpose and workload | Domain event, command, background job, migration part, notification, or other |
| Producer | Concrete class, function, service, operator, or scheduler |
| Enqueue or publish API | Call site and contract |
| Channel | Topic, queue, table, endpoint, file, or in-process dispatcher |
| Configuration source | Exact configuration object, file, environment, or inherited default |
| Serialization and identity | Schema, message ID, operation ID, correlation |
| Delivery and acknowledgement | At-most-once, at-least-once, manual ack, transaction boundary, or unknown |
| Retry and timeout | Actual configured behavior and owner |
| Consumer | Concrete handler or consumer set |
| Failure path | Exception propagation, swallow, retry, DLT, failed-job table, alert, or silent loss |
| Deduplication and idempotency | Mechanism, scope, persistence, and retention |
| Tests and operational evidence | Exact tests, logs, metrics, or incidents |

Two mechanisms are different when any material producer, channel, configuration, acknowledgement, consumer, or failure path differs. Analyze them separately even if they use the same library.

## 3. Execution-path proof

A failure scenario is a claim about reachable behavior. Trace it from entry to outcome:

```text
entry
→ validation
→ synchronous calls
→ persistence and transaction boundary
→ publish or enqueue
→ consumer or remote call
→ retries
→ exception propagation or swallowing
→ compensation, disable, delete, or reversal
→ resulting live state
→ reconciliation or later repair
```

For each branch, record the condition that selects it and the evidence. Include feature flags, configuration modes, legacy fallbacks, and mixed-version operation.

A compensating action changes the failure scenario. For example, if a downstream synchronous create fails and the source record is disabled, the reachable state is not “source remains active while target is absent.” Describe the state the implementation actually creates.

## 4. Reconciliation direction and blind spots

A reconciliation process can observe only its driving set and reachable joins. Record:

- source used to enumerate candidates;
- join direction and keys;
- filters and time window;
- entities that are absent from the driving source;
- late-arrival behavior;
- correction target;
- proof that downstream corrections were applied.

A process driven from existing target-system entities cannot discover an entity missing from that target unless another source explicitly supplies the candidate. State this blind spot rather than assigning the reconciliation mechanism a capability it does not have.

## 5. Retry, replay, and dead-letter safety gate

Retry or replay is not a transport-only change. Audit every affected handler. Use one row per handler:

| Check | Evidence required |
|---|---|
| Stable operation identity | Key, scope, collision behavior, and retention |
| Duplicate detection | Durable store or deterministic idempotent effect |
| Side effects | Which effects can repeat and how duplicates are prevented or reconciled |
| Transaction boundary | What commits together and what can partially commit |
| Error propagation | Whether errors reach the retry mechanism or are caught and suppressed |
| Progress accounting | Whether counters, checkpoints, offsets, or completion state change exactly once |
| Completion rule | How completion is derived and whether duplicate parts can complete early |
| Ambiguous result | Timeout or lost acknowledgement behavior |
| Ordering and concurrency | Required order, parallel execution, and race handling |
| Replay test | Duplicate, partial-failure, and repeated-part test evidence |
| Recovery and rollback | How a bad replay is contained and corrected |

If any material row is unverified, classify replay safety as `UNKNOWN`. The ready recommendation is then to establish identity, deduplication, error propagation, and progress accounting before enabling automatic retry, replay, or DLT redelivery.

A handler that catches an error, increments progress anyway, or derives completion from a non-idempotent counter fails this gate until corrected.

## 6. Storage-role classification

Do not infer a table's semantic role from its name. Classify each material store from read and write paths:

- authoritative live state;
- observation or event history;
- derived projection;
- rollback or compensation data;
- audit history;
- outbox or inbox;
- job or migration checkpoint;
- progress accounting;
- cache;
- quarantine or dead-letter storage.

Record who writes it, who reads it, when it is authoritative, retention, and how corrections work. Rollback data is not the current migration state unless runtime control flow actually reads it as such.

## 7. Quantitative claims and repository inventory

Every count MUST include:

- immutable revision;
- exact path scope and exclusions;
- counting unit, such as files, top-level classes, endpoints, handlers, or routes;
- command or query;
- relevant raw output or a stored result reference;
- known undercount and overcount risks.

A source file may contain multiple classes or endpoints. File counts are not class counts. Prefer a parser or compiler index; when using text search, label the count approximate and cross-check exceptional files.

Examples of reproducible commands:

```bash
git rev-parse HEAD
git ls-files 'src/**/*.java'
rg --line-number 'class .*Endpoint' src
```

The exact command depends on the language and repository. Preserve the command that produced the published number.

## 8. Repository provenance

Distinguish “origin outside the repository” from “provenance within the repository.” Check:

```bash
git ls-files -- <path>
git log --follow -- <path>
git blame -- <path>
git status --short -- <path>
```

A tracked deployment file with commit history has repository provenance. Its external generation process may still be unknown, but do not call the artifact itself unversioned or of unknown origin without evidence.

## 9. Dependency and runtime-wiring claims

A module's local declaration is not the full dependency set. Inspect:

- root and parent build files;
- convention plugins, `buildSrc`, included builds, version catalogs, BOMs, and platforms;
- dependency constraints and inherited configurations;
- generated code and annotation processors;
- container or framework runtime injection;
- resolved compile and runtime dependency output.

A claim such as “the module depends only on X and Y” requires resolved dependency evidence or must be narrowed to “the module directly declares X and Y in file Z.”

## 10. Compatibility and fallback paths

Inventory all active modes:

- current preferred path;
- legacy read path;
- legacy write path;
- feature-flag-disabled path;
- migration or mixed-version path;
- fallback after partial deployment or unavailable infrastructure.

Trace both writes and reads. A new storage backend does not eliminate a legacy backend when flags or fallback reads still select it.

## 11. Adversarial verification

Before finalizing a material finding:

1. search for a second mechanism with a similar name;
2. inspect configuration at the producer and consumer, including inherited defaults;
3. inspect tests that exercise the alleged failure;
4. inspect compensation and rollback code;
5. inspect feature flags and legacy paths;
6. inspect exception catches and progress updates;
7. identify evidence that would falsify the finding;
8. record counterevidence and explain why the finding survives it.

If the finding does not survive, correct or withdraw it. Do not preserve a recommendation whose mechanism is no longer supported.
