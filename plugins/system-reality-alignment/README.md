# System Reality Alignment

This is the installable plugin source for the shared `align-system` Agent Skill. The repository carries compatible Codex and Claude Code manifests; each platform-specific release archive includes the shared skill and the manifest needed by that platform.

Project source, installation instructions, and release checksums:

https://github.com/mikeqwe/system-reality-alignment-plugin

## Capability

Use the skill to:

- design evidence-backed system behavior;
- review architecture, data, state, and feedback-loop integrity;
- plan staged improvements;
- repair incidents and data corruption at the source;
- implement contracts, invariants, lineage, reconciliation, and observability;
- define operating controls and adaptation metrics;
- evaluate whether the plugin or another intervention is useful, neutral, harmful, or still unknown.

Material analysis is revision-specific and reproducible. The skill isolates independently configured mechanisms, traces real execution and compensation paths, verifies counts and inherited dependencies, classifies storage roles, checks compatibility fallbacks, and requires per-handler replay-safety evidence before recommending retry or redelivery.

The skill is instruction-first. Bundled Python scripts scaffold and validate Markdown artifacts and summarize local JSONL evaluation records. They do not access the network or modify a system under review. Python is not required to load the skill.

## Invocation

Claude Code:

```text
/system-reality-alignment:align-system review this repository's order lifecycle
```

Codex:

```text
$align-system design a reality-aligned payment reconciliation workflow
```
