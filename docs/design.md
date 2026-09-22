# Why v2 exists

## Original intent

The July 20–21, 2026 brief began with the idea that more order in a system and cleaner data make accurate adaptation to reality easier. The follow-up was how to bring an existing real-world system closer to that principle, then to express the approach as a self-contained English Markdown document an agent could use for design, review, planning, repair, and development.

This paragraph is a reconstruction of the author's brief, not a published raw conversation transcript. The original repository's [v1.1 core standard](https://github.com/mikeqwe/system-reality-alignment-plugin/blob/b4663d041a569acb702087750a54065d3a9486fb/plugins/system-reality-alignment/skills/align-system/references/core-standard.md) also defines the object as a software or socio-technical system and its connection to the real-world process it represents.

The target is not tidy data for its own sake, and not a generic honesty/judgment/memory framework for agents. A useful intervention must improve a consequential observation, interpretation, decision, effect, or correction path in the target system. Agent evidence discipline supports that task; it does not replace it.

## Design choices, not established benefits

The [v1.1 entry point](https://github.com/mikeqwe/system-reality-alignment-plugin/blob/b4663d041a569acb702087750a54065d3a9486fb/plugins/system-reality-alignment/skills/align-system/SKILL.md) required multiple reference reads, explicit modes, a broad completion gate, and artifact validation. This is observable design overhead, not proof that those requirements caused worse results. We do not have a controlled v1-versus-v2 effectiveness comparison.

V2 is written afresh with one domain-focused skill and four optional lenses. No v1 runtime code, templates, or reference text is carried forward. Package identity, licensing, marketplace names, and existing CI action pins are retained for continuity. The runtime has no executable code; Python is limited to repository checks, release packaging, and evaluation preparation.

The default unit of work is one consequential loop. This favors mechanism-level precision without requiring exhaustive inventories. The original concerns about data meaning and feedback remain explicit, including human incentives, source authority, late corrections, uncertain outcomes, and the population a reconciliation can actually see.

Removing mandatory artifact validation is deliberate: a heading or schema can be structurally correct while its claim is false. The new package checker says only what it checks. The evaluation includes negative controls so verbosity, excessive investigation, and needless redesign are not mistaken for added value.

## Compatibility and model guidance

Sources checked September 22, 2026. These sources inform implementation choices; none validates this plugin's effectiveness.

- OpenAI, [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), September 11, 2026: narrower triggers, relevant reference loading, less rigid scaffolding, and explicit completion boundaries. V2 uses these as design constraints rather than adding an Astra-specific prompt layer.
- Anthropic, [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1): completion, scope, source retrieval, and progress communication need clear expectations. V2 makes those task boundaries explicit. It does not inject provider-specific API or thinking-history manipulation into Claude Code.
- OpenAI, [Build skills](https://learn.chatgpt.com/docs/build-skills): local discovery supports `.agents/skills`, including symlinked folders. Shared frontmatter stays at `name` and `description`.
- OpenAI, [Package your plugin](https://developers.openai.com/plugins/build/plugins): the portable root `plugin.json` is supported, with `.codex-plugin/plugin.json` retained as a compatibility layout. V2 includes both and a repository marketplace. The README avoids assuming a cross-version plugin-install CLI.
- Anthropic, [Plugins reference](https://code.claude.com/docs/en/plugins-reference): `.claude-plugin/plugin.json` and a root `skills/` directory provide the Claude package, with native validation available from the CLI.

The same instructions run on Astra and Fable. We have not demonstrated that different model-specific prompts help. Keep model snapshot, effort, tools, and permission settings fixed within an experiment; do not compare model changes and plugin changes as though they isolate one cause.

## Acceptance boundaries

A release candidate should have consistent manifests, resolved package references, no unexpected executable payload, deterministic release archives, and regression tasks with an inspectable oracle. Those are necessary packaging/evaluation properties, not claims about agent behavior.

A beneficial plugin must improve real task outcomes relative to a baseline without increasing material false claims, unsafe changes, or human review burden. A short report is not automatically good; neither is a comprehensive one. Judge whether a user can locate the evidence, understand the mechanism, and act with better-calibrated expectations.

Known limits: instructions cannot guarantee adherence, grant unavailable access, supply missing independent observations, verify unobserved production behavior, or schedule delayed checks. A fresh-context review can help on a consequential disputed claim, but a compulsory second agent is not part of this design. No claim of reliable self-enforcement is made.
