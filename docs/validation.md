# Validation record — 2026-09-22

This records checks on the v2 rewrite proposed against main commit
`b4663d041a569acb702087750a54065d3a9486fb`. It is not an effectiveness claim.

## Executed locally

Environment: Linux authoring container, Python 3.13.5, standard library only.

```sh
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir dist
```

- Repository-owned structure/link/manifest checks passed.
- 27 top-level unit tests passed. These test packaging, negative structural
  mutations, repeatable archive bytes and checksums, input-only case export,
  and the consistency of synthetic fixtures and their evaluator.
- Both platform ZIPs built and their extracted payloads passed the local checks.
  Tests build twice and compare bytes; `dist/SHA256SUMS` identifies each payload.
- The root skill has 797 whitespace-delimited words, below the repository's
  950-word review budget. This is not a token-cost measurement.

The fixture tests reproduce the payment timeout/replay hazard and reconciliation
blind spot, exercise arrival-order/semantic-rank mistakes, check a healthy
idempotent projection, and verify supplied population counts. The evaluator's
reference implementation and deliberately broken mutations check the checker;
none of them is a model-generated treatment run.

## Not executed here

- Native `claude plugin validate` and actual Claude Code/Fable invocation.
- Actual Codex/Astra skill discovery, invocation, and plugin loading.
- macOS host validation or Python 3.11 / latest-Python CI execution.
- Control/treatment model runs, blind human review, or real-production outcomes.

Neither native CLI is installed in the authoring container. Portable manifests
and installation instructions were checked against the official sources in
[the design note](design.md), not claimed as native integration results.
GitHub Actions results must be read from the PR checks; local success does not
substitute for them.

## Next acceptance gate

Use [the evaluation protocol](../evals/README.md) on the actual Astra and Fable
hosts, then on a real held-out lifecycle task. Keep the six supplied cases as
regression probes, not evidence of broad generalization. Until those comparisons
exist, behavioral effect is **UNKNOWN**; package correctness is a separate claim.
