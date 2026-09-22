# Examples: reasoning quality, not a prescribed format

The following are invented examples, not evidence about the user's repository.

## An accepted request is not a completed outcome

Weak: "Add retries and better logging to make provisioning reliable."

Useful: "The API stores `active` when the vendor returns HTTP 202. That response confirms acceptance, not provisioning. Access decisions can therefore use a state that has not been observed. Keep accepted work pending, correlate the vendor operation with its eventual result, and expire or escalate overdue observations. Check the vendor's actual completion contract before choosing a polling or callback design. A test should keep access inactive after acceptance and activate it only after the authoritative completion signal. Production reliability remains unmeasured."

Why it helps: a specific semantic collapse, an affected decision, and an observation that closes the loop. It does not assume an event bus is needed.

## Clean output can hide lost inputs

Weak: "All materialized rows have valid status, so the pipeline is healthy."

Useful: "The status query starts from materialized rows. It cannot observe input records dropped before materialization. Compare against the eligible source population, preserve rejected identities with reason codes, and give unresolved discrepancies an owner. The missing population must remain visible in the denominator. Do not change invalid records to success to raise the metric."

Why it helps: finding more errors can initially make a metric look worse while improving the system's contact with reality.

## A correction is not always a later domain event

A sensor report for Monday may be corrected on Wednesday. Sorting by ingestion time confuses transport with domain ordering; sorting only by event time can discard a valid correction. Use the source's documented revision/supersession contract and retain the relevant lineage. When the source supplies no resolution rule, surface the conflict rather than inventing one.

## A justified non-change

A retried worker writes a pure projection using an atomic unique intent key in one database transaction. No external effect exists on that path, the key survives restarts for the entire supported retry horizon, and error propagation is tested. There is no established need for a new distributed deduplication service. Retain the control and scope the conclusion to this path; another handler may differ.

## Honest incompleteness that still helps

"The patch now preserves pending status on an ambiguous timeout; the regression test passes. I did not verify vendor-side deduplication because its contract is unavailable. Broad replay remains unsafe to recommend. Before enabling it, obtain the key-retention and timeout-recovery contract for this endpoint."

This completes a bounded local improvement without pretending the production loop is verified or blocking unrelated work.
