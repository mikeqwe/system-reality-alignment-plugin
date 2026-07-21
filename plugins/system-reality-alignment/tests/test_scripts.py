from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "align-system"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new_artifact = load_module("new_artifact", SKILL_ROOT / "scripts" / "new_artifact.py")
validate_artifact = load_module("validate_artifact", SKILL_ROOT / "scripts" / "validate_artifact.py")


class ScriptTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(new_artifact.slugify("Payment Reconciliation"), "payment-reconciliation")
        self.assertEqual(new_artifact.slugify("  "), "system")

    def test_all_templates_exist(self):
        template_dir = SKILL_ROOT / "assets" / "templates"
        for filename in new_artifact.MODES.values():
            self.assertTrue((template_dir / filename).is_file(), filename)

    def test_templates_pass_non_strict_validation_after_base_replacement(self):
        template_dir = SKILL_ROOT / "assets" / "templates"
        with tempfile.TemporaryDirectory() as temp_dir:
            for mode, filename in new_artifact.MODES.items():
                text = (template_dir / filename).read_text(encoding="utf-8")
                text = text.replace("{{SYSTEM_NAME}}", "Example System").replace("{{DATE}}", "2026-07-21")
                path = Path(temp_dir) / filename
                path.write_text(text, encoding="utf-8")
                result = validate_artifact.validate(mode, path, strict=False)
                self.assertTrue(result["valid"], f"{mode}: {result}")

    def test_missing_heading_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.md"
            path.write_text("# Example\n\n## Executive Assessment\n\nSome content.\n", encoding="utf-8")
            result = validate_artifact.validate("review", path, strict=False)
            self.assertFalse(result["valid"])
            self.assertTrue(result["errors"])

    def test_unresolved_placeholder_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.md"
            path.write_text("# {{SYSTEM_NAME}}\n", encoding="utf-8")
            result = validate_artifact.validate("review", path, strict=False)
            self.assertFalse(result["valid"])
            self.assertTrue(any("placeholder" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
