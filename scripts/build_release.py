#!/usr/bin/env python3
"""Build deterministic Codex and Claude Code release archives."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "system-reality-alignment"
ARCHIVE_ROOT = Path("system-reality-alignment")
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    return parser.parse_args()


def load_version() -> str:
    manifests = [
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
    ]
    versions = {
        str(json.loads(manifest.read_text(encoding="utf-8"))["version"])
        for manifest in manifests
    }
    if len(versions) != 1:
        raise ValueError("manifest versions must match")
    version = versions.pop()
    if not SEMVER_RE.fullmatch(version):
        raise ValueError("version must be semantic")
    return version


def is_bundled_file(path: Path) -> bool:
    return (
        path.is_file()
        and not path.is_symlink()
        and path.name != ".DS_Store"
        and path.suffix != ".pyc"
        and "__pycache__" not in path.parts
    )


def common_files() -> list[Path]:
    paths = [PLUGIN / "LICENSE", PLUGIN / "README.md"]
    invalid = [path for path in paths if not is_bundled_file(path)]
    if invalid:
        raise ValueError(f"required bundled file is missing or unsafe: {invalid[0]}")
    paths.extend(path for path in (PLUGIN / "skills").rglob("*") if is_bundled_file(path))
    return sorted(paths, key=lambda path: path.relative_to(PLUGIN).as_posix())


def write_archive(archive: Path, manifest: Path) -> None:
    if not is_bundled_file(manifest):
        raise ValueError(f"manifest is missing or unsafe: {manifest}")
    sources = [*common_files(), manifest]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for source in sorted(sources, key=lambda path: path.relative_to(PLUGIN).as_posix()):
            relative = ARCHIVE_ROOT / source.relative_to(PLUGIN)
            mode = 0o755 if source.parent.name == "scripts" and source.suffix == ".py" else 0o644
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIMESTAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | mode) << 16
            bundle.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def validate_archive(archive: Path, manifest: Path, version: str) -> None:
    expected = {
        (ARCHIVE_ROOT / source.relative_to(PLUGIN)).as_posix()
        for source in [*common_files(), manifest]
    }
    with zipfile.ZipFile(archive) as bundle:
        names = set(bundle.namelist())
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != ARCHIVE_ROOT.name:
                raise ValueError(f"unsafe archive path: {name}")
        if names != expected:
            missing = sorted(expected - names)
            unexpected = sorted(names - expected)
            raise ValueError(f"archive contents differ: missing={missing}, unexpected={unexpected}")

        with tempfile.TemporaryDirectory() as temp_dir:
            extract_dir = Path(temp_dir)
            bundle.extractall(extract_dir)
            plugin_root = extract_dir / ARCHIVE_ROOT
            extracted_manifest = plugin_root / manifest.relative_to(PLUGIN)
            manifest_data = json.loads(extracted_manifest.read_text(encoding="utf-8"))
            if (
                manifest_data.get("name") != "system-reality-alignment"
                or manifest_data.get("version") != version
            ):
                raise ValueError("archive manifest identity or version is invalid")
            skills = manifest_data.get("skills")
            if not isinstance(skills, str) or not skills.startswith("./"):
                raise ValueError("archive manifest skills path is invalid")
            skills_path = (plugin_root / skills[2:]).resolve()
            plugin_root_resolved = plugin_root.resolve()
            if plugin_root_resolved not in skills_path.parents or not skills_path.is_dir():
                raise ValueError(f"archive manifest path is missing: {skills}")
            for script in skills_path.rglob("*.py"):
                compile(script.read_text(encoding="utf-8"), str(script), "exec")

            if manifest.parent.name == ".claude-plugin" and shutil.which("claude"):
                result = subprocess.run(
                    ["claude", "plugin", "validate", str(plugin_root), "--strict"],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if result.returncode:
                    detail = result.stderr.strip() or result.stdout.strip()
                    raise ValueError(f"Claude archive validation failed: {detail}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    try:
        version = load_version()
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".sra-release-", dir=output_dir.parent) as temp_dir:
        staging_dir = Path(temp_dir)
        archives = [
            (
                staging_dir / f"system-reality-alignment-claude-code-v{version}.zip",
                PLUGIN / ".claude-plugin" / "plugin.json",
            ),
            (
                staging_dir / f"system-reality-alignment-codex-v{version}.zip",
                PLUGIN / ".codex-plugin" / "plugin.json",
            ),
        ]
        try:
            for archive, manifest in archives:
                write_archive(archive, manifest)
                validate_archive(archive, manifest, version)
        except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        checksum_path = staging_dir / "SHA256SUMS"
        checksum_path.write_text(
            "".join(f"{sha256(archive)}  {archive.name}\n" for archive, _ in archives),
            encoding="utf-8",
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        published = [archive.replace(output_dir / archive.name) for archive, _ in archives]
        published.append(checksum_path.replace(output_dir / checksum_path.name))

    for path in published:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
