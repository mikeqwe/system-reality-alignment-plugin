# Evaluation Mode

## Objective

Determine whether an intervention, workflow, agent behavior, plugin version, or operating practice is **useful**, **neutral**, **harmful**, or **unknown** for a defined task population and outcome.

The target is causal and operational evidence, not a preference score or a claim that a longer artifact is better.

## Classification

Use four states:

- **USEFUL**: the practically meaningful improvement is supported and no hard guardrail is violated.
- **NEUTRAL**: the entire uncertainty interval lies inside the predeclared equivalence band around zero.
- **HARMFUL**: the intervention causes a practically meaningful degradation or violates a hard guardrail.
- **UNKNOWN**: evidence is insufficient, immature, contradictory, or compatible with more than one state.

Failure to prove improvement is not proof of neutrality.

## Procedure

1. Define the eligible task population, unit of analysis, intervention, version, target users, and exclusions.
2. Segment by mode, complexity, risk, system type, model version, and tool availability when effects may differ.
3. Record assignment separately from actual activation or compliance.
4. Establish a counterfactual. Prefer randomized live assignment; otherwise use historical replay, shadow mode, matched controls, or a clearly limited before/after design.
5. Predeclare one primary metric per evaluation question, its direction, the minimum practically meaningful effect `δ`, the observation window, and hard guardrails.
6. Record fast signals such as first-pass acceptance, false positives, review time, latency, token or compute cost, and scope expansion.
7. Record delayed outcomes such as rollback, escaped defects, incident recurrence, rework, correction accuracy, and operational outcome quality.
8. Use independent review or an independent outcome source. The evaluated agent's self-score is not ground truth.
9. Keep task assignment, outcome labeling, exclusions, and metric definitions stable after results are observed. Record deviations.
10. Compare treatment and control within comparable segments. Report sample sizes, effect, uncertainty interval, outcome maturity, and guardrail violations.
11. Classify:
    - `USEFUL` when the lower confidence bound is greater than `+δ` and guardrails pass;
    - `HARMFUL` when the upper confidence bound is less than `-δ`, or any hard guardrail fails;
    - `NEUTRAL` when the full interval is contained in `[-δ, +δ]` and guardrails pass;
    - `UNKNOWN` otherwise.
12. Make a routing decision per segment: enable, shadow, restrict, disable, gather more evidence, or revise the intervention.
13. Preserve a persistent holdout or periodic replay suite so later model or plugin changes remain measurable.

## Minimum run record

Use `schemas/evaluation-run.schema.json` as the interchange contract. Each completed task should record at least:

- a stable evaluation ID shared by the control and treatment population;
- task ID and eligibility;
- control or treatment assignment;
- whether the intervention actually activated;
- the intervention or plugin version under evaluation, recorded identically for control and treatment assignments;
- model and tool versions;
- mode, complexity, risk tier, and repository revision;
- start and completion time;
- primary metric name, direction, value, and outcome maturity;
- human review effort and cost where available;
- hard guardrail violations;
- independent reviewer or outcome source;
- notes explaining exclusions or overrides.

## Counterfactual ladder

Use the strongest design that is safe and feasible:

1. randomized live rollout with stratification;
2. randomized shadow evaluation;
3. blinded historical replay on known outcomes;
4. matched concurrent control;
5. interrupted time series with stable definitions;
6. simple before/after comparison, explicitly labeled weak.

Do not claim causality from an uncontrolled before/after comparison without ruling out changes in task mix, model version, tools, repository state, or reviewer behavior.

## Hard guardrails

Examples that override average gains:

- fabricated evidence or nonexistent paths;
- unapproved destructive changes;
- violation of read-only or mode boundaries;
- security, privacy, financial-integrity, or production-data incident;
- irreversible action without rollback;
- recommendation based on a conflated mechanism;
- automatic replay without verified handler safety;
- systematic conversion of unknowns into confident claims;
- production incident causally attributed to the intervention.

## Required deliverable

Use `assets/templates/evaluation.md` and include:

- evaluation question and decision;
- eligible population and segments;
- intervention and version snapshot;
- counterfactual and assignment method;
- primary metric, direction, `δ`, observation window, and guardrails;
- data-quality and outcome-maturity assessment;
- results by segment with sample sizes and uncertainty;
- guardrail events and qualitative failure modes;
- classification per segment;
- economic or workflow impact;
- rollout, restriction, kill-switch, or evidence-gathering decision;
- residual uncertainty and next review trigger.

## Local summarizer

The bundled script accepts JSONL run records and emits a segment scorecard:

```bash
python3 <skill-directory>/scripts/summarize_evaluations.py runs.jsonl \
  --minimum-effect 0.15 \
  --minimum-samples 5
```

The script uses a transparent normal-approximation interval for the mean difference. Treat it as a reproducible diagnostic, not a substitute for experimental design, power analysis, or domain review.

By default it segments by evaluation ID, intervention version, model version, metric, mode, complexity, and risk tier. It reports assignment and activation separately so the primary comparison remains intention-to-treat while contamination and non-compliance stay visible. Do not override grouping in a way that combines different intervention or model versions.
