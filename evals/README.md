# Evaluate the system improvement, not the ritual

No Astra/Fable behavioral runs are bundled with this rewrite. The six synthetic cases are development regression probes, not a representative benchmark, an independent holdout, or evidence of net benefit.

## Quick native smoke test

Use a fresh session with the intended model and verify that explicit invocation loads this exact v2 skill, not an older plugin/copy. Record host version, exact model identifier, effort, plugin commit, and whether invocation and relevant-reference loading worked. Native loading and effectiveness are separate results.

## Prepare an isolated case

From this repository:

```sh
python3 scripts/prepare_eval.py case-a /tmp/sra-case-a-control
python3 scripts/prepare_eval.py case-a /tmp/sra-case-a-treatment
```

Destinations must not exist. The exporter copies only the selected task's input files. It never exports [rubric.json](rubric.json), the reference implementation, tests, or answer checks. Use an external disposable workspace, not a child directory in this repository where a task agent could discover evaluator material.

For a clean control, disable this plugin, older versions, and equivalent global instructions; record other installed skills/memory that cannot be removed. For treatment, use a freshly extracted release package, not a symlink to this entire repository. The task agent should have access to the case workspace and installed skill package, not evaluator files. These files are public, so prior exposure remains possible; disclose contamination rather than calling this a blind benchmark.

Give both arms the same task text. In treatment, prepend only the host invocation (`$align-system` or `/system-reality-alignment:align-system`). Finish the task in one fresh session per run; record timeouts, failures, and refusals instead of dropping them. Do not add the rubric to the task prompt or adapt the task after seeing an answer.

| Case | Work | Primary diagnostic |
| --- | --- | --- |
| case-a | Read-only recovery review | External commit/timeout, separate mechanisms, reconciliation coverage |
| case-b | Implement a projection | Ordering, correction, conflict, validation, limited scope |
| case-c | Evaluate a success claim | Cohort denominator and dependent outcome signals |
| case-d | Greenfield workflow design | Acceptance versus result; missing provider guarantees |
| case-e | Read-only healthy-path review | Avoid unsupported redesign of a safe local effect |
| case-f | Typo fix | Avoid triggering a system audit for a routine edit |

Case-f explicit invocation tests graceful non-applicability. Separately run its plain prompt with the plugin installed to test automatic over-triggering.

## Score evidence and behavior

Freeze task inputs, rubrics, model/effort, tool access, time budget, and acceptable overhead before comparisons. Randomize arm order; use at least three independent fresh runs per case/arm for an exploratory regression sweep, but do not treat that small sweep as statistical proof. Add v1.1 as a separate arm only with its own isolated installation.

A reviewer who did not author the run should grade anonymized outputs against [rubric.json](rubric.json), inspecting citations, diffs, and actual execution logs. A grader model may assist, but its opinion or keyword match is not ground truth. For each check record pass/fail/unclear with evidence; record critical failures separately. Unsupported severe findings and unrequested edits count against the result even if another finding is correct.

For case-b, also run the evaluator-side black-box checks after the agent finishes:

```sh
python3 evals/check_projection.py /tmp/sra-case-b-treatment/projection.py
```

This imports candidate Python code. Run it only in a disposable, appropriately restricted environment; it is not a sandbox. The initial case-b implementation intentionally fails. Repository tests verify that the checker rejects it and representative wrong implementations, while accepting a reference implementation. That is fixture/oracle validation, not an agent run.

Record per run: case/input hash, randomized assignment, plugin commit, exact model and host versions, effort, other instructions, tools/permissions, outcome checks, critical errors, incorrect claims, unnecessary changes, elapsed time, tokens when available, and minutes the reviewer needed to verify the result. Keep missing measurements missing; do not fill them with estimates from another model.

Report paired outcomes per task and model, raw denominators, critical incidents, and overhead. Do not pool Astra and Fable or count repeated runs of one task as independent task coverage. Unclear findings require adjudication or remain unclear. A small or inconsistent difference means benefit is unknown, not that the plugin is equivalent or neutral.

## First complex real task

Synthetic cases can catch regressions but miss real codebase complexity. Choose a held-out task from an actual repository whose ground truth can be inspected without production writes. Pin the same source revision and access for each arm. A useful starting prompt, customized to a concrete flow:

```text
Review <one real lifecycle> at <revision>. Determine where recorded state or
success signals can diverge from actual outcomes and how the system corrects
that mismatch. Use the repository and the supplied read-only operational
sources. Do not change code or invoke external side effects. Deliver prioritized,
reachable findings with evidence, existing controls, a minimal improvement plan,
and the observations needed to distinguish remaining hypotheses. Stay within
this lifecycle; follow dependencies only when they can change a conclusion.
```

Keep the task prompt identical between arms except the skill invocation. Where access permits, include a known past failure as a positive control and a deliberately healthy path as a negative control; keep their labels from the task agent. Domain experts should inspect execution paths and compare operational evidence. Do not manufacture a current incident from an old log or infer today's deployment from the code branch.

Promote a change only when the resulting evidence supports a useful gain for the intended task cohort without unacceptable error or review cost. Preserve failed and neutral-looking trials. This repository does not automatically schedule runs, call model APIs, or upload private source data.
