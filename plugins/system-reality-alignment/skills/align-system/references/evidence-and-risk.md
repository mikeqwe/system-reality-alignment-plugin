# Evidence, Findings, Risk, and Prioritization

## 1. Evidence labels

Use labels when the distinction affects a recommendation, implementation, or risk decision.

| Label | Meaning | Required handling |
|---|---|---|
| `FACT` | Directly supported by inspected evidence | Cite the file, line, query, command, log, schema, or user-provided source |
| `DERIVED` | Deterministic calculation from facts | Show the inputs and transformation |
| `INFERENCE` | Reasoned conclusion supported by facts but not directly observed | State the reasoning and plausible alternatives |
| `HYPOTHESIS` | Testable possible explanation | Define a test that can confirm or reject it |
| `ASSUMPTION` | Unverified input used to proceed | State impact if false and verification owner |
| `UNKNOWN` | Evidence is missing, inaccessible, or not observed | Do not replace with a confident value; define acquisition path |
| `CONFLICT` | Credible sources disagree | Preserve both claims and define resolution or reconciliation |

Do not label every sentence mechanically. Label decision-relevant claims, disputed facts, and uncertainty boundaries.

## 2. Evidence inventory

For each material source, record:

- source name and location;
- owner;
- fact or claim it supports;
- authority scope;
- time coverage and freshness;
- collection method;
- known gaps;
- whether it is independent of the system under evaluation;
- retention and reproducibility.

## 3. Finding format

Each review, repair, or implementation finding SHOULD use:

```text
ID:
Title:
Severity:
Confidence:
Status:
Affected decision or outcome:
Evidence:
Mechanism:
Failure scenario:
Impact:
Recommendation:
Verification:
Owner:
Dependencies:
Residual risk:
```

A finding is incomplete when it contains only a preference or abstract best practice without an observable failure mechanism.

## 4. Severity

- **Critical**: credible risk of safety, legal, security, financial-integrity, irreversible data, or broad silent-decision failure requiring immediate containment.
- **High**: systemic correctness or availability failure with substantial blast radius, weak detectability, or expensive recovery.
- **Medium**: material localized error, recurring operational burden, or constrained decision-quality degradation.
- **Low**: limited impact, maintainability risk, or future fragility with no current material failure.

Severity measures impact and urgency, not certainty.

## 5. Confidence

- **High**: direct evidence, reproducible path, and few plausible alternatives.
- **Medium**: strong partial evidence with remaining assumptions or incomplete coverage.
- **Low**: plausible but materially dependent on unverified assumptions.

A high-severity, low-confidence item usually requires rapid investigation, not confident implementation of a speculative fix.

## 6. Priority

Prioritize using a transparent combination of:

- severity;
- probability or observed frequency;
- blast radius;
- irreversibility;
- detectability;
- evidence confidence;
- time to feedback;
- dependency unlock;
- cost and migration risk;
- intervention reversibility.

Suggested classes:

- **P0 — contain now**: active or imminent critical harm.
- **P1 — next committed work**: high-value correction with sufficient evidence.
- **P2 — planned improvement**: material but not immediately urgent.
- **P3 — monitor or defer**: low impact, weak evidence, or blocked dependency.

## 7. Recommendation quality

A recommendation MUST specify:

- the source mechanism being changed;
- the decision or outcome it improves;
- concrete contract, invariant, code, data, or process change;
- rollout and compatibility path;
- verification signal;
- owner;
- residual risk.

Avoid recommendations such as “improve logging,” “clean the data,” “use a single source of truth,” or “add monitoring” without precise semantics and an operational response.

## 8. Maturity model

Use maturity only as a diagnostic, not as a vanity score.

| Level | Characteristics |
|---|---|
| 0 — Opaque | Mutable state, weak identity, no outcome verification, errors found by users |
| 1 — Recorded | Some structured observations and basic ownership, limited lineage |
| 2 — Traceable | Correlation, explicit contracts, decision records, known time semantics |
| 3 — Reconciled | Independent outcomes, systematic reconciliation, owned discrepancies |
| 4 — Adaptive | Short feedback loops, measured decision quality, controlled rule/model evolution |
| 5 — Self-correcting within bounds | Automated detection and safe correction with explicit human and policy limits |

Do not advance a level based solely on more tooling. Evidence must show the corresponding operational capability.
