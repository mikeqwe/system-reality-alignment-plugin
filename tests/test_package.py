import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_package import PLUGIN, validate, validate_plugin
from build_release import build
from prepare_eval import prepare


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"))
        self.plugin = self.root / PLUGIN

    def tearDown(self):
        self.temp.cleanup()

    def test_package(self):
        self.assertEqual([], validate(self.root))

    def test_version_mismatch(self):
        p = self.plugin / ".claude-plugin/plugin.json"
        data = json.loads(p.read_text()); data["version"] = "99.0.0"
        p.write_text(json.dumps(data))
        self.assertIn("manifest versions differ or are missing", validate(self.root))

    def test_bad_manifest(self):
        (self.plugin / "plugin.json").write_text("[]")
        self.assertTrue(validate_plugin(self.plugin))

    def test_missing_manifest(self):
        (self.plugin / ".codex-plugin/plugin.json").unlink()
        self.assertTrue(validate_plugin(self.plugin))

    def test_runtime_file_rejected(self):
        (self.plugin / "stealth.py").write_text("print('unexpected')")
        self.assertTrue(any("unexpected distributable" in e for e in validate(self.root)))

    def test_runtime_manifest_rejected(self):
        p = self.plugin / ".codex-plugin/plugin.json"
        data = json.loads(p.read_text()); data["hooks"] = "./hooks.json"
        p.write_text(json.dumps(data))
        self.assertTrue(any("runtime component" in e for e in validate(self.root)))

    def test_broken_reference(self):
        (self.plugin / "skills/align-system/references/semantics.md").unlink()
        self.assertTrue(any("broken/escaping link" in e for e in validate(self.root)))

    def test_broken_root_document_link(self):
        (self.root / "docs/design.md").unlink()
        self.assertTrue(any("broken/escaping link" in e for e in validate(self.root)))

    def test_escaping_reference(self):
        p = self.plugin / "README.md"
        p.write_text("[escape](../../../../outside.md)")
        self.assertTrue(any("broken/escaping link" in e for e in validate(self.root)))

    def test_extra_frontmatter(self):
        p = self.plugin / "skills/align-system/SKILL.md"
        p.write_text(p.read_text().replace("name: align-system", "name: align-system\nmodel: astra"))
        self.assertTrue(any("frontmatter" in e for e in validate(self.root)))

    def test_root_budget(self):
        p = self.plugin / "skills/align-system/SKILL.md"
        p.write_text(p.read_text() + " excess" * 1000)
        self.assertTrue(any("950-word" in e for e in validate(self.root)))

    def test_symlink_rejected(self):
        (self.plugin / "alias").symlink_to(self.plugin / "README.md")
        self.assertTrue(any("symlink" in e for e in validate(self.root)))

    def test_wrong_marketplace(self):
        p = self.root / ".agents/plugins/marketplace.json"
        data = json.loads(p.read_text()); data["plugins"][0]["source"]["path"] = "../wrong"
        p.write_text(json.dumps(data))
        self.assertTrue(any("marketplace" in e for e in validate(self.root)))


class ReleaseTests(unittest.TestCase):
    def test_reproducible_payloads_and_checksums(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = build(root / "a"), build(root / "b")
            for a, b in zip(first, second):
                self.assertEqual(a.read_bytes(), b.read_bytes())
                with zipfile.ZipFile(a) as archive:
                    names = archive.namelist()
                    self.assertFalse(any("eval" in p or "tests/" in p or p.endswith(".py") for p in names))
                    self.assertIn("skills/align-system/SKILL.md", names)
                    self.assertIn("plugin.json", names)
                    target = "claude" if "claude-code" in a.name else "codex"
                    foreign = "codex" if target == "claude" else "claude"
                    self.assertIn(f".{target}-plugin/plugin.json", names)
                    self.assertNotIn(f".{foreign}-plugin/plugin.json", names)
                    extract = root / target
                    archive.extractall(extract)
                    self.assertEqual([], validate_plugin(extract, target))
            for line in (root / "a/SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ")
                self.assertEqual(digest, hashlib.sha256((root / "a" / name).read_bytes()).hexdigest())


class ExportTests(unittest.TestCase):
    def test_exports_only_case_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            for case in ("case-a", "case-b", "case-c", "case-d", "case-e", "case-f"):
                output = prepare(case, Path(directory) / case)
                self.assertTrue((output / "task.md").is_file())
                self.assertFalse((output / "rubric.json").exists())
                self.assertFalse((output / "check_projection.py").exists())
                self.assertFalse(list(output.rglob("__pycache__")))

    def test_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):
                prepare("case-a", Path(directory))

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                prepare("../rubric.json", Path(directory) / "out")
