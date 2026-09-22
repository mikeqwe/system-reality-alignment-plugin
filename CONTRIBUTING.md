# Contributing

Preserve the original system-design goal and the instruction-only runtime. Explain which observed task failure or missing capability motivates a change. Prefer deleting redundant instructions to accumulating generic rules.

Run the repository gate from [AGENTS.md](AGENTS.md). For packaging changes, also validate the plugin with the actual installed host where available. Keep portable, Codex, and Claude manifests version-aligned. Preserve the CI job names `validate (3.11)` and `validate (3.x)`, which are required by the current branch protection.

Behavioral changes need representative task evidence or an explicit `not run` limitation, not just passing package checks. See [evals/README.md](evals/README.md). Keep evaluator answers outside runtime archives. Do not commit private logs, credentials, source exports, or raw personal data.

A PR should state the intended effect, changed behavior, performed checks, counterexamples, and remaining uncertainty. Do not merge or tag a release solely because document structure passed validation.
