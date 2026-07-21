# Repository instructions

This repository packages one cross-platform Agent Skill for Codex and Claude Code.

## Change discipline

- Keep `plugins/system-reality-alignment/skills/align-system/SKILL.md` concise. Put detailed doctrine, mode procedures, and examples in `references/`.
- Keep the Codex and Claude Code manifests on the same semantic version.
- Preserve cross-platform compatibility: shared skill frontmatter must use only `name` and `description` unless a platform-specific field is strictly necessary.
- Do not add network access, MCP servers, or hooks unless the capability cannot be implemented safely as instructions or local deterministic scripts.
- Treat the documents in `references/` as normative. Templates and scripts must remain consistent with them.
- When changing required artifact sections, update the templates, validator, tests, README, and changelog in the same change.

## Required validation

Run before considering a change complete:

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

## Release discipline

- Update both plugin manifests.
- Add a dated entry to `CHANGELOG.md`.
- Rebuild both distributable ZIP files.
- Let `scripts/build_release.py` validate both extracted ZIP files and produce `SHA256SUMS`.
- Verify a clean Git tree and matching release-asset checksums before tagging.
