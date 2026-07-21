# System Reality Alignment Standard

## 1. Purpose

This standard defines how to design and evolve a software or socio-technical system so that its internal model remains meaningfully connected to the real-world process it represents.

The target is not abstract cleanliness. The target is **adaptive accuracy**: the system can observe relevant events, preserve their meaning, make decisions from traceable evidence, compare expected and actual outcomes, and improve its model and behavior.

This standard applies to transactional systems, workflows, event-driven architectures, data platforms, automation, machine-learning-assisted decisions, operational processes, and human-in-the-loop systems.

## 2. Normative language

- **MUST**: required for an alignment claim.
- **SHOULD**: normally required; omission needs a documented reason.
- **MAY**: optional technique.

## 3. Reference loop

Analyze the system as a closed loop:

```text
Reality
  → Observation
  → Capture
  → Transport
  → Storage
  → Interpretation
  → Decision
  → Action
  → Outcome
  → Reconciliation
  → Learning
  ↺
```

Definitions:

- **Reality**: the external or operational process the system is intended to affect or represent.
- **Observation**: a signal about an event or condition, including who or what observed it.
- **Capture**: conversion of the observation into a record.
- **Transport**: movement through APIs, queues, files, people, or other channels.
- **Storage**: persisted evidence or state.
- **Interpretation**: a rule, model, query, or human judgment that assigns meaning.
- **Decision**: selection of an intended course of action.
- **Action**: an attempted change to the world or another system.
- **Outcome**: what actually happened after the action or independently of it.
- **Reconciliation**: comparison of claims, actions, and outcomes using independent evidence.
- **Learning**: change to rules, models, contracts, controls, or operations based on discrepancies.

A system is not meaningfully adaptive when this loop is open, unobservable, or too slow to correct material errors.

## 4. Primary objective: decision fitness

Work MUST begin with a decision or outcome, not with a generic request to clean data.

For each target decision, define:

- decision owner and affected actors;
- decision frequency and latency requirement;
- inputs and their authority;
- possible actions;
- cost of false positive, false negative, delay, and no decision;
- actual outcome used to judge the decision;
- time horizon for feedback;
- escalation path when evidence is insufficient.

Data quality is contextual. A dataset is fit only relative to a decision, use case, and time requirement.

## 5. Required semantic separation

The model MUST distinguish the following:

### 5.1 Observation

A report that something was seen or measured.

Example: `courier_scanned_package_at = 2026-07-21T09:12:00Z`.

### 5.2 Command

A request or intent to perform an action.

Example: `capture_payment_requested`.

### 5.3 Derived state

A conclusion calculated from one or more observations and rules.

Example: `order_status = delivered` derived from delivery evidence and exception rules.

### 5.4 Decision

A selected action with its evidence, rule or model version, actor, and timestamp.

### 5.5 Action attempt

What the system or operator attempted, including idempotency and execution result.

### 5.6 Outcome

What independently occurred in the domain.

### 5.7 Correction

A later statement that supersedes, disputes, or invalidates a prior observation or interpretation.

A single mutable status field SHOULD NOT be treated as sufficient evidence for all seven categories.

## 6. Observation and evidence requirements

Critical observations MUST preserve enough context to evaluate meaning and reliability:

- stable identifier;
- subject or entity identifier;
- event type;
- source and observing actor;
- event time;
- observation or capture time;
- ingestion time where transport delay matters;
- schema version;
- units, timezone, and coordinate system where applicable;
- correlation or causation identifiers;
- raw payload or recoverable source reference where lawful and proportionate;
- confidence or collection method when the observation is probabilistic;
- correction and supersession relationship.

The system SHOULD preserve raw observations before destructive normalization. Normalized records MUST retain lineage to their source observations.

## 7. Time semantics

A timestamp without semantics is ambiguous. Critical records MUST state which time they represent.

Common times:

- **event time**: when the domain event occurred;
- **observation time**: when an actor observed it;
- **capture time**: when it became a record;
- **ingestion time**: when the receiving system accepted it;
- **processing time**: when logic evaluated it;
- **effective time**: when a rule, contract, or value applies;
- **recorded time**: when the system stored the current statement.

The design MUST define behavior for late, out-of-order, future-dated, corrected, and replayed events. It MUST define the precision and timezone for each contractual timestamp.

## 8. Identity and causality

Critical facts MUST have stable identity and deduplication semantics.

Define:

- entity identity and merge/split rules;
- event identity;
- command identity;
- action attempt identity;
- idempotency key scope and retention;
- correlation identifiers;
- causal links where they are claimed;
- rules for aliases and external identifiers.

Correlation MUST NOT be represented as causation without additional evidence.

## 9. Authority and source of truth

Authority MUST be defined per fact, scope, and time.

Use the form:

> Source X is authoritative for fact Y within scope Z for effective time T, subject to correction rule C.

A source can be authoritative for one fact and non-authoritative for another. A derived warehouse, dashboard, or status field is not automatically authoritative because it is centralized.

When sources disagree, preserve the conflicting claims and apply an explicit resolution rule. Do not silently discard the losing claim.

## 10. Unknown, conflict, and absence

The model MUST distinguish at least:

- known value;
- unknown or not observed;
- not applicable;
- withheld or inaccessible;
- stale or expired;
- conflicting claims;
- invalid input;
- pending decision;
- corrected or superseded value.

A generic null SHOULD NOT represent multiple meanings. Unknown MUST be allowed as a valid state when the system lacks evidence. Forced classification creates false certainty and damages adaptation.

## 11. Contracts at boundaries

Every material boundary SHOULD have an explicit semantic contract covering:

- purpose and domain meaning;
- producer and consumers;
- authority per field or event;
- required and optional fields;
- allowed values and units;
- identity and idempotency;
- time semantics;
- ordering guarantees;
- duplicate behavior;
- late and corrected data;
- unknown and conflict representation;
- validation and quarantine behavior;
- schema and semantic versioning;
- backward and forward compatibility;
- retention, privacy, and deletion;
- service-level expectations;
- owner and change process.

Structural validity is not semantic validity. Contracts SHOULD include cross-field and lifecycle constraints.

## 12. Invariants

An invariant is a testable statement that MUST remain true within a declared scope.

Use these classes where relevant:

- **domain**: a completed payment has a provider transaction identifier;
- **lifecycle**: a terminal state cannot transition to an active state without an explicit reopening event;
- **temporal**: completion time is not earlier than creation time, subject to defined clock tolerance;
- **identity**: one idempotency key cannot produce two committed charges;
- **conservation**: ledger entries balance and reconcile to balance changes;
- **authorization**: only an authorized actor can perform a protected transition;
- **causal**: an action result references the command and attempt that produced it;
- **auditability**: every automated decision references its input snapshot and logic version.

Each invariant MUST specify scope, enforcement point, detection path, exception handling, and remediation owner.

Introduce uncertain invariants in observe-only mode before blocking production. Measure violations, classify legitimate exceptions, then enforce.

## 13. Decision records and reproducibility

Material automated or manual decisions MUST be reproducible from retained evidence.

Record:

- decision identifier and type;
- actor or service;
- decision time;
- input observation identifiers or immutable snapshot reference;
- missing inputs and uncertainty;
- rule, policy, query, or model version;
- selected action and alternatives where material;
- reason code and human rationale where applicable;
- override identity and justification;
- expected outcome;
- later actual outcome;
- correction or appeal.

A mutable log line alone is not a durable decision record.

## 14. Actions and idempotency

The system MUST distinguish requested actions from attempted and completed actions.

For material side effects, define:

- idempotency key generation and scope;
- retry policy;
- timeout and ambiguous-result handling;
- duplicate suppression;
- compensation or reversal;
- partial-failure behavior;
- external confirmation;
- reconciliation after uncertain execution.

Exactly-once claims SHOULD be avoided unless the guarantee is demonstrable end to end. Prefer explicit at-least-once delivery with idempotent effects and reconciliation.

## 15. Outcomes and independent verification

A system cannot evaluate its own correctness solely from the state it produced.

For each important decision or action, define an outcome signal that is as independent as practicable. Examples include provider settlement files, physical scans, customer confirmation, inventory counts, ledger reconciliation, or later human adjudication.

Store or link:

```text
prediction or expectation
→ decision
→ action attempt
→ actual outcome
→ discrepancy
→ corrective action
```

When no independent outcome exists, label the decision quality as unverified and define a plan to obtain one.

## 16. Reconciliation

Reconciliation MUST compare two or more claims about the same domain fact or conservation rule.

Define:

- compared sources;
- matching keys and tolerances;
- comparison frequency;
- late-arrival window;
- discrepancy categories;
- owner and service-level objective for resolution;
- correction procedure;
- audit trail;
- proof that the correction reached downstream consumers.

Reconciliation is not only a financial pattern. It applies to inventory, identity, entitlements, workflow completion, model labels, and external side effects.

## 17. Observability

Observability MUST support answering:

- what happened;
- where it happened;
- when each stage happened;
- which version of code, schema, rule, or model participated;
- what evidence drove the decision;
- what action was attempted;
- what outcome followed;
- where evidence was lost, delayed, duplicated, or changed.

Prefer structured events, traces, stable identifiers, and domain-level metrics over free-text logs. Instrument the decision loop, not only infrastructure health.

## 18. Quality and adaptation metrics

Select metrics tied to the target decision. Common measures include:

- completeness;
- semantic validity;
- uniqueness and duplicate rate;
- cross-source consistency;
- freshness;
- transport and processing timeliness;
- lineage coverage;
- unknown rate;
- conflict rate;
- correction rate;
- reconciliation match rate;
- unresolved discrepancy age;
- false-positive and false-negative rates;
- decision-to-outcome latency;
- time to detect misalignment;
- time to correct source and downstream state;
- recurrence rate;
- percentage of decisions with reproducible evidence.

Every metric MUST have an owner, definition, numerator, denominator, exclusions, time window, data source, and expected action when breached.

Metrics are proxies. Use guardrails and independent outcomes to reduce Goodhart effects.

## 19. Human and organizational factors

The system boundary includes people, incentives, procedures, and manual tools.

Review:

- whether correct input is easier than convenient fiction;
- whether users are rewarded for manipulating the metric;
- whether manual overrides are captured and reviewed;
- whether producers feel downstream consequences;
- whether consumers understand data limitations;
- whether ownership covers meaning, not only infrastructure;
- whether incident fixes remove the source mechanism.

Assign both technical ownership and semantic ownership for critical data and decisions.

## 20. Change lifecycle

A reality-alignment change SHOULD follow this sequence:

1. instrument current behavior;
2. collect baseline evidence;
3. define the target contract and invariants;
4. run new checks in observe-only mode;
5. classify violations and legitimate exceptions;
6. implement source fixes and compatibility paths;
7. backfill or reconcile historical state where necessary;
8. canary or stage rollout;
9. compare old and new outcomes;
10. enforce only after evidence supports enforcement;
11. retain rollback and correction capability;
12. review metrics after a meaningful feedback interval.

Migration plans MUST cover mixed-version operation, replay, duplicate delivery, partial deployment, rollback, and downstream consumers.

## 21. Prioritization

Prioritize interventions using:

- severity and probability of wrong decisions;
- blast radius;
- irreversibility;
- detectability;
- evidence strength;
- time to feedback;
- dependency and migration risk;
- implementation effort;
- reversibility of the intervention.

Prefer interventions that close a high-value feedback loop quickly and make later work easier to verify.

## 22. Anti-patterns

Treat these as warning signs:

- declaring a centralized database to be the universal source of truth;
- storing only the latest status and discarding observations;
- using null for unknown, conflict, and not applicable;
- cleaning data without fixing the producing process;
- adding dashboards without an assigned response action;
- calling logs observability without correlation, semantics, or outcomes;
- silently overwriting contradictory claims;
- treating transport success as business success;
- assuming retries are safe without idempotency;
- enforcing a new invariant before observing real exceptions;
- backfilling derived state without preserving method and version;
- measuring model accuracy against labels generated by the same model or rule;
- closing an incident after symptom removal while the source mechanism remains.

## 23. Definition of Done

A system change may claim improved reality alignment only when:

- the target decision and real-world outcome are explicit;
- critical observations have source, identity, and time semantics;
- raw evidence or recoverable lineage is preserved proportionately;
- derived state is distinguishable from observation;
- unknown and conflict are represented explicitly;
- authority is defined per fact;
- critical contracts and invariants are testable;
- decisions and overrides are reproducible;
- material actions are idempotent or reconcilable;
- an independent outcome or reconciliation path exists;
- late, duplicate, out-of-order, missing, and corrected inputs are handled;
- rollout, rollback, backfill, and downstream compatibility are addressed;
- metrics detect recurrence and trigger owned actions;
- residual uncertainty and risk are documented.
