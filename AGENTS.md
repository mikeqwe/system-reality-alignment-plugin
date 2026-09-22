# Repository guidance

This repository ships an instruction-only skill, not an agent runtime. Preserve the domain goal: improve how a system observes, represents, acts on, and corrects against reality. Do not replace it with generic agent self-verification.

Keep the root skill small and its trigger narrow. References are selected by relevance, not a mandatory reading list. Keep all three plugin manifests on the same version; shared skill frontmatter uses only `name` and `description`.

Local tests and evaluation preparation use disposable fixtures, have no production access, and require no network or model credentials. Run them, repair failures caused by the requested change, and rerun affected checks without asking for separate approval. Repository gate:

```sh
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir dist
```

The package checker validates structure, not truth or model effectiveness. Keep evaluation rubrics outside exported task workspaces and release archives. Do not claim Astra/Fable runs unless they actually occurred. Read `evals/README.md` when changing behavioral evaluation; read `docs/design.md` when changing the scope or instruction design.
