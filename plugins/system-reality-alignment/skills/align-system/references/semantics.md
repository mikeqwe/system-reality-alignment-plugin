# Meaning that survives contact with reality

Use only the parts that affect the target decision. This is not a request to redesign every table.

## Start at the decision

Which actor decides what, for whom, and by when? What is the cost of acting incorrectly, waiting, or not acting? Which later observation can distinguish success from a convenient story? Data is fit for a particular decision and time horizon, not universally clean.

Draw the smallest useful model: relevant entities, observations, derived claims, allowed actions, and feedback. Separate the current model from the proposed one. An apparently messy exception may represent a real distinction; do not normalize it away before understanding it.

## Authority, identity, and time

Specify authority per fact: a provider can attest that it accepted a request without attesting that the customer received the result. Record the source, subject, scope, and applicable time. Two copies of one source are not two independent witnesses.

At consequential boundaries, preserve enough context to recover meaning: subject and event identity, source, units, schema/rule version, and the relevant times. Distinguish occurrence, ingestion, processing, and effective time when their difference changes behavior. Define how duplicates, late delivery, correction, deletion, and conflicting identities behave. Correlation alone does not establish causality.

Use the producer's actual ordering/authority contract. Arrival order is not necessarily event order; a later timestamp is not necessarily a more authoritative correction. An older effective-time correction may legitimately arrive later. Do not invent a universal last-write-wins or monotonic-state rule.

## Unknown is a useful state

Distinguish not yet observed, explicitly absent, stale, conflicting, invalid, and not applicable where they lead to different actions. A failed probe is not a negative business fact. Define how the system acts under uncertainty: defer, restrict a risky action, seek another observation, or escalate. The policy depends on the relative cost of false positives and false negatives.

Retain a proportionate source reference and correction history so derived claims can be rebuilt or disputed. This does not require event sourcing or indefinite raw-data retention. Respect deletion requirements, privacy, access controls, and storage budgets; minimize sensitive payloads and use restricted references rather than copying secrets into reports.

## Testable domain contracts

State an invariant in domain terms with its scope, enforcement/detection point, and exception policy. For example: one purchase intent must not cause two committed charges, including across timeouts and restarts. A database uniqueness constraint only proves the part it actually protects.

Keep input observations, desired state, inferred current state, decision, and action result distinct in the minimal representation that supports correction. A single status field is acceptable when its meaning and required recovery evidence are genuinely sufficient.

## Close the human loop too

Ask who sees a mismatch, who can correct the producer and downstream state, and how the correction is confirmed. Assign semantic ownership, not just infrastructure ownership. Check whether incentives make truthful recording costly or reward hiding exceptions. A new dashboard with no possible response does not close a loop.

For useful operational measures, define the population, numerator/denominator, window, exclusions, observation coverage, and response. Include missing outcomes and discrepancy age, not only success among completed records. A falling unknown rate can mean better observation or suppressed uncertainty: distinguish those mechanisms before celebrating.

For manual or model-assisted judgments, retain the policy/version and evidence needed for correction or appeal. Do not grade decisions against labels produced by the same decision rule and call that independent accuracy.
