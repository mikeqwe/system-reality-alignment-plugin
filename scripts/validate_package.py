"""Offline repository-owned structural checks; not a model or truth evaluator."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path("plugins/system-reality-alignment")
REFERENCE_NAMES = {"semantics.md", "mechanisms.md", "interventions.md", "examples.md"}


def validate_plugin(plugin: Path, target: str | None = None) -> list[str]:
    errors = []
    manifests = [plugin / "plugin.json"]
    platforms = [target] if target else ["codex", "claude"]
    manifests += [plugin / f".{p}-plugin/plugin.json" for p in platforms]
    versions = set()
    for path in manifests:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("manifest must be an object")
            if data.get("name") != "system-reality-alignment":
                errors.append(f"wrong plugin name: {path}")
            version = data.get("version")
            if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
                errors.append(f"invalid version: {path}")
            else:
                versions.add(version)
            if not isinstance(data.get("description"), str) or not data["description"]:
                errors.append(f"missing description: {path}")
            if any(k in data for k in ("hooks", "mcpServers", "agents", "apps")):
                errors.append(f"unexpected runtime component: {path}")
        except (OSError, ValueError) as exc:
            errors.append(f"invalid manifest {path}: {exc}")
    if len(versions) != 1:
        errors.append("manifest versions differ or are missing")
    skill = plugin / "skills/align-system/SKILL.md"
    try:
        text = skill.read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not front:
            errors.append("missing skill frontmatter")
        else:
            lines = front.group(1).splitlines()
            keys = [line.partition(":")[0] for line in lines]
            if keys != ["name", "description"] or lines[0] != "name: align-system":
                errors.append("shared frontmatter must contain only name and description")
            if len(lines) != 2 or len(lines[-1].partition(":")[2].split()) > 55:
                errors.append("skill description exceeds discovery budget")
        if len(text.split()) > 950:
            errors.append("root skill exceeds 950-word review budget")
        refs = skill.parent / "references"
        if {p.name for p in refs.glob("*.md")} != REFERENCE_NAMES:
            errors.append("reference inventory differs")
    except OSError as exc:
        errors.append(f"missing skill: {exc}")
    allowed = {"plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "README.md", "LICENSE", "skills/align-system/SKILL.md"}
    allowed |= {f"skills/align-system/references/{name}" for name in REFERENCE_NAMES}
    for path in plugin.rglob("*"):
        if path.is_symlink():
            errors.append(f"symlink in distributable: {path}")
        if path.is_file() and path.relative_to(plugin).as_posix() not in allowed:
            errors.append(f"unexpected distributable file: {path}")
    if target:
        other = "claude" if target == "codex" else "codex"
        if (plugin / f".{other}-plugin").exists():
            errors.append("foreign platform manifest in target archive")
    for name in ("README.md", "LICENSE"):
        if not (plugin / name).is_file():
            errors.append(f"missing {name}")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    plugin = root / PLUGIN
    errors = validate_plugin(plugin)
    # Relative Markdown links in our own package and authoring docs must resolve.
    documents = list(root.glob("*.md"))
    for base in (plugin, root / "docs", root / "evals"):
        documents.extend(base.rglob("*.md"))
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("#"):
                continue
            dest = (path.parent / link.split("#")[0]).resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.exists():
                errors.append(f"broken/escaping link: {path}: {link}")
    for name in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
        try:
            data = json.loads((root / name).read_text(encoding="utf-8"))
            entry = data["plugins"][0]
            source = entry["source"]
            source = source["path"] if isinstance(source, dict) else source
            if data["name"] != "system-reality-tools" or entry["name"] != "system-reality-alignment" or source != "./plugins/system-reality-alignment":
                errors.append(f"incorrect marketplace mapping: {name}")
            if name.startswith(".agents") and entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
                errors.append("incorrect Codex marketplace policy")
            if name.startswith(".claude"):
                version = json.loads((plugin / "plugin.json").read_text())["version"]
                if entry.get("version") != version:
                    errors.append("marketplace version mismatch")
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append(f"invalid marketplace {name}: {exc}")
    return errors


if __name__ == "__main__":
    problems = validate()
    print("\n".join(problems) if problems else "Package structure OK (not behavioral validation).")
    raise SystemExit(bool(problems))
