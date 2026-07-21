#!/usr/bin/env python3
"""Validate dual plugin manifests, marketplace entries, skill metadata, and bundled resources."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "system-reality-alignment"
SKILL = PLUGIN / "skills" / "align-system"


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return {}


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    if not path.is_file():
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return {}
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        errors.append(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"unsupported frontmatter line in {path.relative_to(ROOT)}: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    codex = load_json(PLUGIN / ".codex-plugin" / "plugin.json", errors)
    claude = load_json(PLUGIN / ".claude-plugin" / "plugin.json", errors)
    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json", errors)

    if not str(claude_market.get("description", "")).strip():
        errors.append("Claude marketplace description is required")

    for field in (
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "skills",
    ):
        if codex.get(field) != claude.get(field):
            errors.append(f"manifest mismatch for {field!r}: {codex.get(field)!r} != {claude.get(field)!r}")

    expected_name = "system-reality-alignment"
    expected_version = "1.0.0"
    if codex.get("name") != expected_name:
        errors.append("unexpected plugin name")
    if codex.get("version") != expected_version:
        errors.append(f"release version must be {expected_version}")

    if codex.get("skills") != "./skills/":
        errors.append("skills path must be ./skills/")

    expected_publisher = {
        "author": {
            "name": "Mikhail Sherstiannikov",
            "url": "https://github.com/mikeqwe",
        },
        "homepage": "https://github.com/mikeqwe/system-reality-alignment-plugin#readme",
        "repository": "https://github.com/mikeqwe/system-reality-alignment-plugin",
    }
    if any(codex.get(field) != value or claude.get(field) != value for field, value in expected_publisher.items()):
        errors.append("publisher metadata must match the public repository")

    for market, label in ((codex_market, "Codex"), (claude_market, "Claude")):
        entries = market.get("plugins", [])
        if not any(entry.get("name") == expected_name for entry in entries):
            errors.append(f"{label} marketplace does not list {expected_name}")

    claude_entry = next(
        (entry for entry in claude_market.get("plugins", []) if entry.get("name") == expected_name),
        {},
    )
    if claude_entry.get("version") != codex.get("version"):
        errors.append("Claude marketplace version must match plugin version")

    metadata = parse_frontmatter(SKILL / "SKILL.md", errors)
    if metadata.get("name") != "align-system":
        errors.append("skill name must be align-system")
    description = metadata.get("description", "")
    if len(description) < 80:
        errors.append("skill description is too short for reliable discovery")

    required = [
        SKILL / "references" / "core-standard.md",
        SKILL / "references" / "evidence-and-risk.md",
        SKILL / "references" / "mode-design.md",
        SKILL / "references" / "mode-review.md",
        SKILL / "references" / "mode-plan.md",
        SKILL / "references" / "mode-repair.md",
        SKILL / "references" / "mode-implementation.md",
        SKILL / "references" / "mode-operations.md",
        SKILL / "scripts" / "new_artifact.py",
        SKILL / "scripts" / "validate_artifact.py",
    ]
    required += sorted((SKILL / "assets" / "templates").glob("*.md"))
    for path in required:
        if not path.is_file():
            errors.append(f"missing bundled resource: {path.relative_to(ROOT)}")

    for path in (SKILL / "scripts").glob("*.py"):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"Python compile failure in {path.relative_to(ROOT)}: {exc.msg}")

    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if "\r\n" in text:
            warnings.append(f"CRLF line endings: {path.relative_to(ROOT)}")

    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)
    for item in warnings:
        print(f"WARNING: {item}", file=sys.stderr)
    if errors:
        print(f"package invalid: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("package valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
