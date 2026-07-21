from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from support import copy_project


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = "system-reality-alignment"
VERSION = "1.0.0"


def run_builder(output_dir: Path, project: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/build_release.py", "--output-dir", str(output_dir)],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )


def expected_common_files() -> set[str]:
    relative_files = {
        "LICENSE",
        "README.md",
        "skills/align-system/SKILL.md",
        "skills/align-system/assets/templates/data-contract.md",
        "skills/align-system/assets/templates/decision-record.md",
        "skills/align-system/assets/templates/design.md",
        "skills/align-system/assets/templates/implementation.md",
        "skills/align-system/assets/templates/operations.md",
        "skills/align-system/assets/templates/plan.md",
        "skills/align-system/assets/templates/repair.md",
        "skills/align-system/assets/templates/review.md",
        "skills/align-system/references/core-standard.md",
        "skills/align-system/references/evidence-and-risk.md",
        "skills/align-system/references/mode-design.md",
        "skills/align-system/references/mode-implementation.md",
        "skills/align-system/references/mode-operations.md",
        "skills/align-system/references/mode-plan.md",
        "skills/align-system/references/mode-repair.md",
        "skills/align-system/references/mode-review.md",
        "skills/align-system/scripts/new_artifact.py",
        "skills/align-system/scripts/validate_artifact.py",
    }
    return {
        f"{ARCHIVE_ROOT}/{relative}"
        for relative in relative_files
    }


class ReleaseBuildTests(unittest.TestCase):
    def test_build_creates_platform_archives_with_exact_contents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "dist"

            result = run_builder(output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            archives = {
                "codex": output_dir / f"system-reality-alignment-codex-v{VERSION}.zip",
                "claude-code": output_dir / f"system-reality-alignment-claude-code-v{VERSION}.zip",
            }
            common = expected_common_files()
            for platform, archive in archives.items():
                self.assertTrue(archive.is_file(), archive)
                manifest = ".codex-plugin/plugin.json" if platform == "codex" else ".claude-plugin/plugin.json"
                expected = common | {f"{ARCHIVE_ROOT}/{manifest}"}
                with zipfile.ZipFile(archive) as bundle:
                    self.assertEqual(set(bundle.namelist()), expected)
                    script = bundle.getinfo(
                        f"{ARCHIVE_ROOT}/skills/align-system/scripts/new_artifact.py"
                    )
                    self.assertEqual((script.external_attr >> 16) & 0o777, 0o755)

            checksum_path = output_dir / "SHA256SUMS"
            checksum_lines = checksum_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(checksum_lines), 2)
            checksums = {
                filename: digest
                for digest, filename in (line.split("  ", 1) for line in checksum_lines)
            }
            self.assertEqual(set(checksums), {archive.name for archive in archives.values()})
            for archive in archives.values():
                self.assertEqual(
                    checksums[archive.name],
                    hashlib.sha256(archive.read_bytes()).hexdigest(),
                )

    def test_build_rejects_mismatched_manifest_versions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project = copy_project(temp_path)
            manifest_path = (
                project
                / "plugins"
                / "system-reality-alignment"
                / ".claude-plugin"
                / "plugin.json"
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["version"] = "9.9.9"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = run_builder(temp_path / "dist", project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest versions must match", result.stderr)

    def test_build_rejects_non_semantic_version(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project = copy_project(temp_path)
            for platform in (".claude-plugin", ".codex-plugin"):
                manifest_path = (
                    project
                    / "plugins"
                    / "system-reality-alignment"
                    / platform
                    / "plugin.json"
                )
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["version"] = "../bad"
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = run_builder(temp_path / "dist", project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("version must be semantic", result.stderr)

    def test_build_validates_extracted_manifest_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project = copy_project(temp_path)
            manifest_path = (
                project
                / "plugins"
                / "system-reality-alignment"
                / ".codex-plugin"
                / "plugin.json"
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"] = "./missing-skills/"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = run_builder(temp_path / "dist", project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("archive manifest path is missing", result.stderr)

    def test_build_is_reproducible(self):
        with (
            tempfile.TemporaryDirectory() as first_dir,
            tempfile.TemporaryDirectory() as second_dir,
        ):
            first = Path(first_dir) / "dist"
            second = Path(second_dir) / "dist"

            first_result = run_builder(first)
            second_result = run_builder(second)

            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            filenames = [
                f"system-reality-alignment-claude-code-v{VERSION}.zip",
                f"system-reality-alignment-codex-v{VERSION}.zip",
                "SHA256SUMS",
            ]
            for filename in filenames:
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())

    def test_failed_rebuild_preserves_previous_verified_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "dist"
            first_result = run_builder(output_dir)
            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            original = {path.name: path.read_bytes() for path in output_dir.iterdir()}

            project = copy_project(temp_path)
            manifest_path = (
                project
                / "plugins"
                / "system-reality-alignment"
                / ".codex-plugin"
                / "plugin.json"
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"] = "./missing-skills/"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = run_builder(output_dir, project)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                {path.name: path.read_bytes() for path in output_dir.iterdir()},
                original,
            )


if __name__ == "__main__":
    unittest.main()
