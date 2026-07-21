# Contributing

Issues and pull requests are welcome when they keep the plugin small, evidence-driven, and compatible with both Codex and Claude Code.

## Before opening a change

- Use an issue to describe material behavior or workflow changes before implementing them.
- Do not report security vulnerabilities in public issues. Follow [SECURITY.md](SECURITY.md).
- Keep the shared `SKILL.md` concise and put detailed doctrine or examples in `references/`.
- Do not add network access, MCP servers, hooks, or runtime dependencies unless the capability cannot be implemented safely with instructions or deterministic local scripts.

## Development

Python 3.11 or newer is required only for the bundled helper, validation, test, and release scripts. The skill itself is Markdown.

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

Do not commit `dist/`, bytecode, local marketplace caches, or editor metadata.

## Pull requests

Describe the observed problem, the evidence for the change, and how the result was verified. Keep unrelated refactors out of the pull request. If required artifact sections change, update the normative reference, templates, validator, tests, README, and changelog together.
