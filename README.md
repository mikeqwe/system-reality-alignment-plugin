# System Reality Alignment · v2

An instruction-only plugin for **Astra in Codex** and **Fable in Claude Code**. Improve systems whose recorded state, decisions, and success signals can diverge from real outcomes.

The original idea is about the system, not the agent: better order and meaningful data should make it easier to observe reality, detect a wrong model, and adapt. The practical unit is one loop:

`event → observation → state → decision → action → outcome → correction`

Version 2.0.0 is a ground-up rewrite. It preserves the domain purpose and public invocation name, not the old mandatory procedures. **Behavioral benefit on Astra/Fable is not yet established.** The repository includes reproducible regression cases and a comparison protocol rather than claiming that passing package tests proves effectiveness.

## Use it

```text
$align-system Review whether our entitlement state reflects actual provider outcomes. Remain read-only; prioritize reachable failures and the smallest useful correction.

$align-system Implement the agreed timeout recovery fix. Keep the public API, finish the local tests, and distinguish verified behavior from rollout assumptions.

$align-system Design a minimal correction path for late and conflicting observations using our existing database.
```

For Claude Code, use `/system-reality-alignment:align-system` instead of `$align-system` when installed as a plugin. A plain manually copied Claude skill uses `/align-system`.

The skill reads only the references relevant to the task. It does not require a system-wide audit, a separate report, an event-sourcing migration, a fixed subagent team, or a special model setting. Cosmetic edits and general code review are outside its automatic trigger.

## Try this PR before merging

Check out the PR branch in a separate clone. Commands below assume its repository root; `main` continues to contain v1.1 until the PR is merged. Disable the older installation in your host before testing, and avoid having both a plugin and a manual skill copy enabled.

### Claude Code / Fable

```sh
SRA_REPO="$PWD"
cd /path/to/target-project
claude --plugin-dir "$SRA_REPO/plugins/system-reality-alignment"
```

Choose the Fable model available in your account using the host's model selector. The plugin does not change your selection, permissions, or effort.

For a marketplace install after merge:

```sh
claude plugin marketplace add mikeqwe/system-reality-alignment-plugin
claude plugin install system-reality-alignment@system-reality-tools
```

Start a fresh session after installation changes.

### Codex / Astra

For testing a checkout, install just the shared skill at the user scope:

```sh
SRA_REPO="$PWD"
mkdir -p "$HOME/.agents/skills"
ln -s "$SRA_REPO/plugins/system-reality-alignment/skills/align-system" \
  "$HOME/.agents/skills/align-system"
```

`ln` intentionally refuses to overwrite an existing destination. Disable/remove an older plugin through the host, or move a previous manual copy aside before retrying. Start Codex in the target project, select your Astra model, and invoke `$align-system`.

For repo-local installation, put the same skill directory in the target repository's `.agents/skills/align-system`. For marketplace discovery:

```sh
codex plugin marketplace add mikeqwe/system-reality-alignment-plugin --ref main
```

Install it through the host's plugin interface. Host surfaces differ; the direct skill path above avoids depending on a particular plugin-install CLI. Portable and compatibility manifests are included; native host loading still needs the smoke checks below. See [compatibility sources](docs/design.md#compatibility-and-model-guidance).

## What is different from v1.1

| v1.1 | v2 |
| --- | --- |
| Mandatory standard + evidence documents + mode procedure | One compact entry point; four topic references loaded by relevance |
| Required artifact sections and document validators | Existing PR/tests/runbook, with only decision-relevant evidence |
| Seven formally selected modes | Task-driven design, review, planning, repair, implementation, operations, or evaluation |
| Maturity and intervention-effect scoring machinery | No unsupported ratings; effectiveness assessed outside the runtime skill |
| Large blanket completion gate | Complete the authorized deliverable and available relevant checks; bound unknown outcomes |

Retained: source authority and time semantics, real execution paths, independent mechanism boundaries, storage roles, per-effect retry safety, reconciliation populations, correction ownership, and separation of actions from outcomes. No hooks, MCP server, executable runtime, network dependency, telemetry, forced model selection, or automatic background activity.

**Breaking change:** v1 artifact templates, `new_artifact.py`, `validate_artifact.py`, evaluation schema/summarizer, and old reference paths are removed. Existing generated documents are not deleted. Remove old workflow calls to those helpers; use normal repository tests and the new evaluation protocol. Do not concatenate the v1 standard into the v2 skill. The old implementation remains in Git history at `b4663d041a569acb702087750a54065d3a9486fb`.

## Validate and evaluate

Python 3.11+ is needed only by the authoring/test tools, never by the installed skill.

```sh
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir dist
```

The builder creates deterministic Codex and Claude Code ZIPs plus `SHA256SUMS`, checks extracted contents, and excludes evaluation answers and developer tools. In a machine with Claude Code installed, additionally run:

```sh
claude plugin validate . --strict
claude plugin validate ./plugins/system-reality-alignment --strict
```

Then smoke-test actual invocation in a fresh Codex/Astra and Claude Code/Fable session. A local structural checker is not a vendor schema validator or a native-host test.

See [evaluation protocol and real-task prompt](evals/README.md), [design and original intent](docs/design.md), and [validation record](docs/validation.md). Package tests verify structure and fixture consistency, not prompt adherence or production outcomes.

## License and contributions

MIT. See [LICENSE](LICENSE), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).
