from __future__ import annotations

import json
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "ppt-studio"
SKILL = PLUGIN / "skills" / "presentation-director"


class PackageTests(unittest.TestCase):
    def test_dual_manifests_exist(self) -> None:
        self.assertTrue((PLUGIN / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue((PLUGIN / ".claude-plugin" / "plugin.json").is_file())

    def test_runtime_has_theme_contract(self) -> None:
        source = (SKILL / "assets" / "runtime" / "base-deck.html").read_text(encoding="utf-8")
        for theme in ("light", "dark", "custom"):
            self.assertIn(f'data-theme="{theme}"', source)
        for token in ("--slide-bg", "--surface", "--text", "--accent", "--accent-2"):
            self.assertIn(token, source)
        self.assertIn('id="theme-dialog"', source)
        self.assertIn('<meta name="generator" content="PPT Studio by intellbits">', source)
        self.assertIn('<meta name="generator-url" content="https://intellbits.com">', source)
        self.assertIn('id="about-dialog"', source)
        self.assertIn("Apache-2.0", source)
        self.assertIn("presentation-project-data", source)

    def test_brand_attribution_and_trademark_files(self) -> None:
        for root in (ROOT, PLUGIN, SKILL):
            self.assertTrue((root / "NOTICE").is_file())
            self.assertTrue((root / "TRADEMARKS.md").is_file())
            notice = (root / "NOTICE").read_text(encoding="utf-8")
            self.assertIn("Copyright 2026 intellbits", notice)
            self.assertIn("https://intellbits.com", notice)
        codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["author"]["name"], "intellbits")
        self.assertEqual(codex["interface"]["developerName"], "intellbits")
        self.assertEqual(claude["author"]["name"], "intellbits")

    def test_no_external_code_is_declared(self) -> None:
        lock = json.loads((ROOT / "release" / "vendor-lock.json").read_text(encoding="utf-8"))
        self.assertFalse(lock["bundled_external_code"])
        self.assertTrue(all(not item["included_paths"] for item in lock["references"]))

    def test_claude_zip_shape_when_built(self) -> None:
        manifest = json.loads((ROOT / "release" / "manifest.json").read_text(encoding="utf-8"))
        archive = ROOT / "dist" / f"presentation-director-{manifest['version']}-claude.zip"
        if not archive.exists():
            self.skipTest("Release archive has not been built yet.")
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
        self.assertIn("presentation-director/SKILL.md", names)
        self.assertFalse(any(name.startswith("ppt-studio/") for name in names))


if __name__ == "__main__":
    unittest.main()
