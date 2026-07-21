# System Reality Alignment Plugin

A dual-compatible plugin for **Codex** and **Claude Code** that helps agents design, review, plan, repair, implement, and operate software and socio-technical systems while keeping observations, data, decisions, actions, and outcomes traceable to reality.

The package uses one shared Agent Skill and thin platform manifests. It requires no MCP server, network access, background process, lifecycle hook, or runtime dependency.

## Install

### Claude Code

```bash
claude plugin marketplace add mikeqwe/system-reality-alignment-plugin
claude plugin install system-reality-alignment@system-reality-tools
```

Start a new session and invoke the skill explicitly:

```text
/system-reality-alignment:align-system review the order lifecycle and produce a prioritized remediation plan
```

For direct development from a checkout:

```bash
claude --plugin-dir ./plugins/system-reality-alignment
```

### Codex

```bash
codex plugin marketplace add mikeqwe/system-reality-alignment-plugin --ref main
codex plugin add system-reality-alignment@system-reality-tools
```

Start a new session and invoke:

```text
$align-system review the payment state machine for semantic ambiguity, missing invariants, and broken feedback loops
```

For repo-local authoring without installation, copy or symlink `plugins/system-reality-alignment/skills/align-system` into `.agents/skills/align-system`.

## Requirements

The skill itself is Markdown and runs through Codex or Claude Code. Python 3.11 or newer is needed only for the optional artifact helpers, package validation, tests, and release builder.

## Repository layout

```text
.
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── plugins/system-reality-alignment/
│   ├── .codex-plugin/plugin.json
│   ├── .claude-plugin/plugin.json
│   └── skills/align-system/
│       ├── SKILL.md
│       ├── references/
│       ├── assets/templates/
│       └── scripts/
├── scripts/
└── tests/
```

## Typical prompts

```text
$align-system design an auditable order fulfillment state model from the existing repository

$align-system review this service boundary for data-contract, time-semantics, lineage, and reconciliation risks

$align-system plan a staged migration from mutable status fields to evidence-backed derived state

$align-system repair the duplicate-charge failure mode, including containment, reconciliation, backfill, tests, and rollout

$align-system implement the agreed invariants and observability in this codebase

$align-system define an operating scorecard for data quality, decision quality, and feedback-loop latency
```

## Generated artifacts

The skill covers system design, review, improvement planning, repair, implementation, and operating review. It also includes supporting decision-record and data-contract templates.

Create a review scaffold:

```bash
python3 plugins/system-reality-alignment/skills/align-system/scripts/new_artifact.py review \
  --system "Payments" \
  --output docs/system-reality/payments-review.md
```

Fill the generated sections with evidence before running strict validation. An untouched scaffold is intentionally incomplete and will fail `--strict`.

```bash
python3 plugins/system-reality-alignment/skills/align-system/scripts/validate_artifact.py review \
  docs/system-reality/payments-review.md --strict
```

## Validate and build

Run the complete local gate:

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s plugins/system-reality-alignment/tests -v
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir dist
```

When Claude Code is installed, also run:

```bash
claude plugin validate . --strict
claude plugin validate ./plugins/system-reality-alignment --strict
```

The release builder creates and validates:

- `system-reality-alignment-codex-v1.0.0.zip`
- `system-reality-alignment-claude-code-v1.0.0.zip`
- `SHA256SUMS`

Each ZIP contains the shared skill and only the manifest for its target platform. The builder verifies the extracted archive before publishing any checksum.

## Design principles

The plugin enforces five operational distinctions:

1. **Reality is not the same as stored state.**
2. **Observations are not interpretations.**
3. **Interpretations are not decisions.**
4. **Decisions are not actions.**
5. **Actions are not outcomes.**

Unknown, conflicting, late, and corrected information remain explicit rather than being collapsed into premature certainty.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development and pull-request gate. Report vulnerabilities privately according to [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
