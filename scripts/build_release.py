"""Build deterministic, target-specific ZIPs; validate extracted payloads."""
import argparse
import hashlib
from pathlib import Path
import tempfile
import zipfile
from validate_package import ROOT, PLUGIN, validate, validate_plugin


def build(output: Path) -> list[Path]:
    problems = validate()
    if problems:
        raise ValueError("\n".join(problems))
    plugin = ROOT / PLUGIN
    import json
    version = json.loads((plugin / "plugin.json").read_text())["version"]
    output.mkdir(parents=True, exist_ok=True)
    result = []
    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary)
        for target, label in (("codex", "codex"), ("claude", "claude-code")):
            archive = stage / f"system-reality-alignment-{label}-v{version}.zip"
            foreign = ".claude-plugin" if target == "codex" else ".codex-plugin"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
                for source in sorted(plugin.rglob("*")):
                    relative = source.relative_to(plugin)
                    if not source.is_file() or foreign in relative.parts:
                        continue
                    info = zipfile.ZipInfo(relative.as_posix(), (2020, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    bundle.writestr(info, source.read_bytes())
            extracted = stage / target
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(extracted)  # Only our allowlisted, relative paths.
            errors = validate_plugin(extracted, target)
            if errors:
                raise ValueError("\n".join(errors))
            result.append(archive)
        checksums = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in result)
        for archive in result:
            (output / archive.name).write_bytes(archive.read_bytes())
        (output / "SHA256SUMS").write_text(checksums, encoding="utf-8")
    return [output / p.name for p in result]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        for archive in build(args.output_dir):
            print(archive)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"build failed: {exc}\n")
