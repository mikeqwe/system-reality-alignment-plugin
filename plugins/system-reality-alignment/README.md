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
- define operating controls and adaptation metrics.

The skill is instruction-first. Bundled Python scripts only scaffold and validate Markdown artifacts; they do not access the network or modify a system under review. Python is not required to load the skill.

## Invocation

Claude Code:

```text
/system-reality-alignment:align-system review this repository's order lifecycle
```

Codex:

```text
$align-system design a reality-aligned payment reconciliation workflow
```
