from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from support import copy_project


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0"


def run_validator(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate_package.py"],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )


class PackageValidationTests(unittest.TestCase):
    def test_missing_marketplace_description_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = copy_project(Path(temp_dir))
            path = project / ".claude-plugin" / "marketplace.json"
            marketplace = json.loads(path.read_text(encoding="utf-8"))
            marketplace.pop("description", None)
            path.write_text(json.dumps(marketplace), encoding="utf-8")

            result = run_validator(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Claude marketplace description is required", result.stderr)

    def test_marketplace_version_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = copy_project(Path(temp_dir))
            path = project / ".claude-plugin" / "marketplace.json"
            marketplace = json.loads(path.read_text(encoding="utf-8"))
            marketplace["plugins"][0]["version"] = "9.9.9"
            path.write_text(json.dumps(marketplace), encoding="utf-8")

            result = run_validator(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Claude marketplace version must match plugin version", result.stderr)

    def test_release_version_other_than_expected_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = copy_project(Path(temp_dir))
            manifest_paths = [
                project
                / "plugins"
                / "system-reality-alignment"
                / platform
                / "plugin.json"
                for platform in (".codex-plugin", ".claude-plugin")
            ]
            for path in manifest_paths:
                manifest = json.loads(path.read_text(encoding="utf-8"))
                manifest["version"] = "9.9.9"
                path.write_text(json.dumps(manifest), encoding="utf-8")
            marketplace_path = project / ".claude-plugin" / "marketplace.json"
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
            marketplace["plugins"][0]["version"] = "9.9.9"
            marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

            result = run_validator(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"release version must be {VERSION}", result.stderr)

    def test_missing_publisher_metadata_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = copy_project(Path(temp_dir))
            path = project / "plugins" / "system-reality-alignment" / ".claude-plugin" / "plugin.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest.pop("repository", None)
            path.write_text(json.dumps(manifest), encoding="utf-8")

            result = run_validator(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("publisher metadata must match the public repository", result.stderr)

    def test_missing_evaluation_schema_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = copy_project(Path(temp_dir))
            path = (
                project
                / "plugins"
                / "system-reality-alignment"
                / "skills"
                / "align-system"
                / "schemas"
                / "evaluation-run.schema.json"
            )
            path.unlink()

            result = run_validator(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing bundled resource", result.stderr)

    def test_evaluation_schema_requires_versioned_assignment_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = copy_project(Path(temp_dir))
            path = (
                project
                / "plugins"
                / "system-reality-alignment"
                / "skills"
                / "align-system"
                / "schemas"
                / "evaluation-run.schema.json"
            )
            schema = json.loads(path.read_text(encoding="utf-8"))
            schema["required"].remove("evaluation_id")
            path.write_text(json.dumps(schema), encoding="utf-8")

            result = run_validator(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("evaluation run schema must require evaluation_id", result.stderr)


if __name__ == "__main__":
    unittest.main()
