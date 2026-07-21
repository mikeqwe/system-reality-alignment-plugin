# Evidence, Findings, Risk, and Prioritization

## 1. Evidence labels

Use labels when the distinction affects a recommendation, implementation, or risk decision.

| Label | Meaning | Required handling |
|---|---|---|
| `FACT` | Directly supported by inspected evidence | Cite the real file and line, command, query, log, schema, or user-provided source |
| `DERIVED` | Deterministic calculation from facts | Show inputs, transformation, counting unit, and reproducible command |
| `INFERENCE` | Reasoned conclusion supported by facts but not directly observed | State reasoning, counterevidence checked, and plausible alternatives |
| `HYPOTHESIS` | Testable possible explanation or reachable path not yet proven | Define a test that can confirm or reject it |
| `ASSUMPTION` | Unverified input used to proceed | State impact if false and verification owner |
| `UNKNOWN` | Evidence is missing, inaccessible, immature, or not observed | Do not replace with a confident value; define acquisition path |
| `CONFLICT` | Credible sources disagree | Preserve both claims and define resolution or reconciliation |

Do not label every sentence mechanically. Label decision-relevant claims, disputed facts, failure scenarios, and uncertainty boundaries.

## 2. Reproducibility snapshot

Every repository-based review, repair, or implementation artifact MUST record:

- repository or source identity;
- full immutable revision, normally a 40-character Git commit SHA;
- branch or tag only as supplemental context;
- working-tree state when local changes affect evidence;
- analysis date and operational evidence window;
- agent/model and tool versions when available;
- actual paths inspected;
- exact commands or queries used for material counts and derived claims;
- unavailable evidence.

A branch name, shortened logical path, or narrative summary alone is not enough to reproduce the result. When an immutable revision is unavailable, state `REVISION UNAVAILABLE`, explain why, and reduce confidence.

## 3. Evidence inventory

For each material source, record:

- source name and actual location;
- owner;
- fact or claim it supports;
- mechanism ID or system boundary it belongs to;
- authority scope;
- time coverage and freshness;
- collection method;
- known gaps;
- whether it is independent of the system under evaluation;
- retention and reproducibility;
- counterevidence or conflicting sources.

Do not use evidence from one mechanism to support a claim about another without an explicit bridge.

## 4. Claim ledger

Use a claim ledger for material conclusions:

| Claim ID | Label | Claim | Mechanism ID | Supporting evidence | Counterevidence checked | Coverage | Verification command or test | Status |
|---|---|---|---|---|---|---|---|---|

Coverage states SHOULD be one of:

- `EXHAUSTIVE`: all items in the declared population were inspected;
- `SAMPLED`: a declared sample was inspected;
- `PARTIAL`: only a subset is known;
- `UNKNOWN`: the population or coverage cannot be established.

A claim such as “most handlers are idempotent” is not decision-ready unless the population, inspected set, exceptions, and audit method are shown.

## 5. Finding format

Each review, repair, or implementation finding SHOULD use:

```text
ID:
Title:
Severity:
Confidence:
Status:
Affected decision or outcome:
Mechanism ID:
Reachability status: CONFIRMED | HYPOTHESIS | UNKNOWN
Evidence snapshot and real paths:
Evidence coverage:
Counterevidence checked:
Mechanism:
Failure scenario:
Impact:
Recommendation:
Prerequisites and safety gates:
Verification:
Owner:
Dependencies:
Residual risk:
```

A finding is incomplete when it contains only a preference or abstract best practice without an observable mechanism. A failure scenario is incomplete when the actual execution path, compensation, feature flag, or reconciliation direction could invalidate it.

## 6. Severity

- **Critical**: credible risk of safety, legal, security, financial-integrity, irreversible data, or broad silent-decision failure requiring immediate containment.
- **High**: systemic correctness or availability failure with substantial blast radius, weak detectability, or expensive recovery.
- **Medium**: material localized error, recurring operational burden, or constrained decision-quality degradation.
- **Low**: limited impact, maintainability risk, or future fragility with no current material failure.

Severity measures impact and urgency, not certainty.

## 7. Confidence

- **High**: direct evidence at an immutable revision, reproducible path, relevant configuration and compatibility modes checked, material counterevidence rejected, and few plausible alternatives.
- **Medium**: strong partial evidence with remaining assumptions, sampled coverage, or incomplete operational confirmation.
- **Low**: plausible but materially dependent on unverified assumptions, incomplete mechanism identity, or unproven reachability.

A high-severity, low-confidence item usually requires rapid investigation or containment, not confident implementation of a speculative fix.

Confidence MUST decrease when:

- the exact revision is missing;
- logical paths cannot be mapped to real paths;
- counts lack commands or clear units;
- independent mechanisms may be conflated;
- inherited configuration or fallback modes were not inspected;
- a retry recommendation lacks exhaustive handler coverage;
- a maturity claim lacks operational evidence.

## 8. Quantitative claims

A material count or percentage MUST state:

- population and counting unit;
- revision and path scope;
- exclusions;
- command or query;
- raw result or retained output reference;
- coverage and parser limitations.

Examples of distinct units:

- source files;
- top-level classes;
- endpoint classes;
- route methods;
- message types;
- handlers;
- database rows;
- unique domain entities.

Do not convert a file count into a class count. One file may contain zero, one, or multiple classes. Use a language-aware parser where possible; otherwise mark the result approximate and inspect exceptions.

## 9. Recommendation quality

A recommendation MUST specify:

- the exact source mechanism being changed;
- the decision or outcome it improves;
- concrete contract, invariant, code, data, or process change;
- prerequisites and evidence gaps;
- compatibility and migration path;
- rollout, stop conditions, and rollback;
- verification signal;
- owner;
- residual risk.

For retry, replay, redelivery, DLT, or reprocessing, the recommendation MUST include the handler-level safety matrix from `analysis-verification.md`. If coverage is incomplete, the recommendation is an audit or prerequisite change, not “enable retry.”

Avoid recommendations such as “improve logging,” “clean the data,” “use a single source of truth,” “add monitoring,” or “retry failed jobs” without precise semantics and an operational response.

## 10. Priority

Prioritize using a transparent combination of:

- severity;
- probability or observed frequency;
- blast radius;
- irreversibility;
- detectability;
- evidence confidence and coverage;
- time to feedback;
- dependency unlock;
- cost and migration risk;
- intervention reversibility.

Suggested classes:

- **P0 — contain now**: active or imminent critical harm.
- **P1 — next committed work**: high-value correction with sufficient evidence.
- **P2 — planned improvement**: material but not immediately urgent.
- **P3 — investigate, monitor, or defer**: low impact, weak evidence, incomplete safety gate, or blocked dependency.

Do not rank an unverified replay change as implementation-ready merely because the transport supports retries.

## 11. Maturity model

Use maturity only as a diagnostic. A maturity claim MUST show the rubric, evidence, and calculation. Otherwise report `Maturity rating: NOT RATED`.

### 11.1 Dimensions

Score each dimension that is material to the target decision:

| Code | Dimension | What is evaluated |
|---|---|---|
| `O` | Observation | Capture, identity, time, source, corrections, and raw evidence |
| `S` | Semantics and lineage | Contracts, authority, storage roles, derivation, and traceability |
| `D` | Decisions | Reproducible inputs, rule/model version, overrides, and reasons |
| `A` | Actions | Idempotency, retries, partial failure, progress accounting, and compensation |
| `R` | Outcomes and reconciliation | Independent outcomes, driving-set coverage, discrepancy ownership, and correction proof |
| `L` | Learning and operations | Measured feedback, recurrence analysis, controlled changes, and bounded automation |

### 11.2 Level criteria

Assign one confirmed level per dimension:

| Level | Evidence criterion |
|---|---|
| 0 — Opaque | The capability is absent, contradictory, or cannot be evidenced. Mutable status or user reports are the main signal. |
| 1 — Recorded | Some structured records or procedures exist, but coverage, lineage, semantics, or ownership is limited. |
| 2 — Traceable | The relevant path has stable identity, explicit contracts or semantics, correlation, versioned logic, and reproducible repository evidence. |
| 3 — Reconciled | Operational evidence shows systematic comparison with an independent source, owned discrepancies, correction records, and measurable coverage. |
| 4 — Adaptive | Operational evidence shows short feedback loops, measured decision quality, controlled rule or process changes, and demonstrated reduction in recurrence or correction latency. |
| 5 — Self-correcting within bounds | Automated detection and correction operate safely with explicit policy, guardrails, audit, rollback, and human escalation. |

### 11.3 Calculation

Use this scorecard:

| Dimension | Confirmed level | Evidence | Missing evidence | Maximum plausible level |
|---|---:|---|---|---:|
| O | | | | |
| S | | | | |
| D | | | | |
| A | | | | |
| R | | | | |
| L | | | | |

The **confirmed system level** is the minimum confirmed score across material dimensions because the closed loop is constrained by its weakest material stage. Also report the full profile, for example `O2/S2/D1/A1/R0/L0`.

Rules:

- Repository evidence alone can normally confirm at most level 2. Levels 3–5 require operational evidence from reconciliation, outcomes, incidents, metrics, or controlled correction.
- Do not average dimensions into a higher level.
- A range such as `2–3` is allowed only when each affected dimension has a documented lower bound, upper bound, and exact missing evidence. Otherwise use the lower confirmed level or `NOT RATED`.
- Tooling presence does not prove operation. A reconciliation job in code is not level 3 without evidence that it runs, covers the relevant population, produces owned discrepancies, and applies corrections.
- Exclude a dimension only with a written reason tied to the target decision.

## 12. Intervention evaluation

When judging whether this plugin or another intervention is useful, neutral, or harmful, use `mode-evaluation.md`.

Do not use artifact length, checklist completion, or the evaluated agent's confidence as the primary outcome. Require a control or justified counterfactual, a predeclared meaningful-effect threshold, independent outcomes, and the fourth state `UNKNOWN`.
