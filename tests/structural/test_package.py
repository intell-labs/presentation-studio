from __future__ import annotations

import json
import importlib.util
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "presentation-studio"
SKILL = PLUGIN / "skills" / "presentation-studio"


class PackageTests(unittest.TestCase):
    def test_dual_manifests_exist(self) -> None:
        self.assertTrue((PLUGIN / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue((PLUGIN / ".claude-plugin" / "plugin.json").is_file())

    def test_public_identity_is_consistently_intell_labs(self) -> None:
        openai_marketplace = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
        claude_marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(openai_marketplace["name"], "presentation-studio-marketplace")
        self.assertEqual(claude_marketplace["name"], "presentation-studio-marketplace")
        self.assertEqual(
            claude_marketplace["plugins"][0]["homepage"],
            "https://github.com/intell-labs/presentation-studio",
        )
        for path in (
            ROOT / "README.md",
            ROOT / "docs" / "index.html",
            ROOT / ".agents" / "plugins" / "marketplace.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            PLUGIN / ".codex-plugin" / "plugin.json",
            PLUGIN / ".claude-plugin" / "plugin.json",
            SKILL / "SKILL.md",
            SKILL / "assets" / "runtime" / "base-deck.html",
        ):
            source = path.read_text(encoding="utf-8").lower()
            for legacy in (
                "github.com/" + "intell" + "bits",
                "intell" + "bits/" + "ppt" + "-studio",
                "ppt" + "-studio-marketplace",
                "ppt" + "-presentation-studio",
                "ppt" + " studio",
            ):
                self.assertNotIn(legacy, source, path.relative_to(ROOT).as_posix())

    def test_versions_use_plain_semver(self) -> None:
        release = json.loads((ROOT / "release" / "manifest.json").read_text(encoding="utf-8"))["version"]
        codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))["plugins"][0]["version"]
        self.assertEqual({release, codex, claude, marketplace}, {release})
        self.assertRegex(release, r"^\d+\.\d+\.\d+$")

    def test_runtime_has_theme_contract(self) -> None:
        source = (SKILL / "assets" / "runtime" / "base-deck.html").read_text(encoding="utf-8")
        for theme in ("light", "dark", "custom"):
            self.assertIn(f'data-theme="{theme}"', source)
        for token in ("--slide-bg", "--surface", "--text", "--accent", "--accent-2"):
            self.assertIn(token, source)
        for token in ("--brand-primary", "--brand-secondary", "--brand-dark", "--brand-light"):
            self.assertIn(token, source)
        self.assertIn('id="theme-dialog"', source)
        self.assertIn('<meta name="generator" content="Presentation Studio by intell labs">', source)
        self.assertIn('<meta name="generator-url" content="https://github.com/intell-labs/presentation-studio">', source)
        self.assertIn('<meta name="presentation-studio-runtime" content="base-deck-v2">', source)
        self.assertIn('data-presentation-studio-runtime="base-deck-v2"', source)
        self.assertIn('data-view-mode="audience"', source)
        self.assertIn('id="deck-chrome"', source)
        self.assertIn("stampEditBaselines", source)
        self.assertIn("preserve_browser_edits", source)
        control_positions = [source.index(f'id="{identifier}"') for identifier in ("prev", "page-count", "next", "menu-trigger")]
        self.assertEqual(control_positions, sorted(control_positions))
        chrome_start = source.index('id="deck-chrome"')
        chrome_end = source.index("</nav>", chrome_start)
        self.assertLess(source.index('id="control-menu"'), chrome_end)
        self.assertIn(".deck-chrome .page-count,.deck-chrome .menu-trigger,.deck-chrome .control-menu{display:none", source)
        self.assertIn('id="about-dialog"', source)
        self.assertIn("Apache-2.0", source)
        self.assertIn("presentation-project-data", source)
        self.assertIn('"schema_version":"1.4"', source)
        self.assertIn("--content-safe-bottom", source)
        self.assertIn("--content-safe-right", source)
        self.assertIn("data-qa-box", source)
        self.assertIn("data-qa-text-stack", source)
        self.assertIn('data-shortcut="E"', source)
        self.assertIn('data-shortcut="Alt/⌥ Y"', source)
        self.assertIn('data-shortcut="⌘/Ctrl S"', source)
        self.assertIn('id="typography-dialog"', source)
        self.assertIn('id="type-family"', source)
        self.assertIn('id="type-size-number"', source)
        self.assertIn('id="type-color"', source)
        self.assertIn('id="element-toolbar"', source)
        self.assertIn('id="context-type-family"', source)
        self.assertIn('id="context-type-size"', source)
        self.assertIn('id="context-type-color"', source)
        self.assertIn('id="context-fill-color"', source)
        self.assertIn('id="context-border-color"', source)
        self.assertIn('id="context-shadow"', source)
        self.assertIn("configureTypographyEditor", source)
        self.assertIn("configureContextToolbar", source)
        self.assertIn("stampStyleTargets", source)
        self.assertIn("typography_bounds", source)
        self.assertIn("contextual_editor_toolbar", source)
        self.assertIn("per_element_text_style", source)
        self.assertIn("visual_style_editor", source)
        self.assertIn("stampShortcuts", source)
        self.assertIn("author_menu_always_visible", source)
        self.assertIn("BRAND_PALETTE.locked", source)
        self.assertNotIn('body[data-view-mode="audience"] [data-author-control]', source)

    def test_edit_preservation_distinguishes_browser_changes(self) -> None:
        path = SKILL / "scripts" / "preserve_edits.py"
        spec = importlib.util.spec_from_file_location("preserve_edits", path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        old_a = module.js_fnv1a("Old generator")
        old_b = module.js_fnv1a("Keep old")
        existing = (
            f'<div data-edit-id="a" data-edit-baseline="{old_a}">Browser edit</div>'
            f'<div data-edit-id="b" data-edit-baseline="{old_b}">Keep old</div>'
        )
        generated = (
            '<div data-edit-id="a">New generator</div>'
            '<div data-edit-id="b">Fresh generator</div>'
        )
        merged, changed, unknown = module.merge(existing, generated)
        self.assertEqual(changed, ["a"])
        self.assertEqual(unknown, [])
        self.assertIn(">Browser edit</div>", merged)
        self.assertIn(">Fresh generator</div>", merged)
        self.assertIn(f'data-edit-baseline="{module.js_fnv1a("New generator")}"', merged)

    def test_edit_preservation_keeps_contextual_text_and_visual_styles(self) -> None:
        path = SKILL / "scripts" / "preserve_edits.py"
        spec = importlib.util.spec_from_file_location("preserve_style_edits", path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        empty = module.js_fnv1a("")
        existing = (
            f'<h2 data-edit-id="title" data-edit-baseline="{module.js_fnv1a("Title")}" '
            f'data-edit-style-baseline="{empty}" style="font-size: 72px; color: #123456">Title</h2>'
            f'<div data-style-id="card" data-style-baseline="{empty}" '
            'style="background-color: #ffffff; border-radius: 24px"></div>'
        )
        generated = (
            '<h2 data-edit-id="title">Title</h2>'
            '<div data-style-id="card"></div>'
        )
        merged, changed, unknown = module.merge(existing, generated)
        self.assertEqual(changed, [])
        self.assertEqual(unknown, [])
        self.assertIn('style="font-size: 72px; color: #123456"', merged)
        self.assertIn('style="background-color: #ffffff; border-radius: 24px"', merged)
        self.assertIn(f'data-edit-style-baseline="{empty}"', merged)
        self.assertIn(f'data-style-baseline="{empty}"', merged)

    def test_microdeck_preview_isolates_each_slide(self) -> None:
        path = SKILL / "scripts" / "make_preview_gallery.py"
        spec = importlib.util.spec_from_file_location("make_preview_gallery", path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        source = (SKILL / "assets" / "runtime" / "base-deck.html").read_text(encoding="utf-8")
        self.assertEqual(module.count_slides(source), 2)
        isolated = module.isolated_slide(source, 2)
        self.assertIn("presentation-studio-preview-isolation", isolated)
        self.assertIn(".deck-chrome,.deck-controls", isolated)
        self.assertIn(".deck-stage>.slide:nth-of-type(2)", isolated)
        self.assertIn('[data-present-step="required"]', isolated)
        self.assertIn("Opción ${option.code}-${slideIndex+1}", module.TEMPLATE)
        self.assertIn("requestAnimationFrame(()=>requestAnimationFrame", module.TEMPLATE)

    def test_brand_attribution_and_trademark_files(self) -> None:
        for root in (ROOT, PLUGIN, SKILL):
            self.assertTrue((root / "NOTICE").is_file())
            self.assertTrue((root / "TRADEMARKS.md").is_file())
            notice = (root / "NOTICE").read_text(encoding="utf-8")
            self.assertIn("Copyright 2026 intell labs", notice)
            self.assertIn("https://github.com/intell-labs/presentation-studio", notice)
        codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        expected_author = "intell labs"
        self.assertEqual(codex["author"]["name"], expected_author)
        self.assertEqual(codex["interface"]["developerName"], expected_author)
        self.assertEqual(claude["author"]["name"], expected_author)

    def test_visual_qa_contract_is_packaged(self) -> None:
        qa = SKILL / "scripts" / "qa_runtime.cjs"
        self.assertTrue(qa.is_file())
        source = qa.read_text(encoding="utf-8")
        for code in (
            "box-overlap",
            "safe-area-overlap",
            "line-through-text",
            "orphan-connector",
            "unfinished-sequence",
            "brand-name-repetition",
            "brand-mention-accent",
            "unannotated-major-block",
            "text-overlap",
            "surface-text-overlap",
            "text-line-height-tight",
            "text-spacing-tight",
            "connector-proportion",
            "connector-endpoint-gap",
            "brand-theme-color-shift",
            "theme-tone-polarity",
            "author-menu-discoverability",
            "menu-shortcut-label",
            "text-font-size-small",
            "text-font-size-large",
            "typography-editor-hidden",
            "typography-size-bounds",
        ):
            self.assertIn(code, source)
        gallery_qa = SKILL / "scripts" / "qa_gallery.cjs"
        self.assertTrue(gallery_qa.is_file())
        gallery_source = gallery_qa.read_text(encoding="utf-8")
        for code in ("preview-load", "embedded-empty-slide", "embedded-required-state-not-final", "embedded-scale", "responsive-columns", "preview-labels"):
            self.assertIn(code, gallery_source)
        fixture = ROOT / "tests" / "fixtures" / "visual-overlap.html"
        self.assertTrue(fixture.is_file())
        fixture_source = fixture.read_text(encoding="utf-8")
        self.assertIn('data-qa-box="a"', fixture_source)
        self.assertIn('data-brand-mark', fixture_source)

    def test_project_schema_requires_visual_and_brand_policy(self) -> None:
        schema = json.loads((SKILL / "references" / "project.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.4")
        brand_required = schema["properties"]["brand"]["required"]
        self.assertIn("usage_policy", brand_required)
        visual_required = schema["properties"]["visual_qa"]["required"]
        self.assertIn("all_states_rendered", visual_required)
        self.assertIn("harmony_review", visual_required)
        self.assertIn("typography_spacing_passed", visual_required)
        exploration_required = schema["properties"]["visual_exploration"]["required"]
        self.assertIn("gallery_qa", exploration_required)
        appearance_required = schema["properties"]["appearance"]["required"]
        self.assertIn("brand_palette", appearance_required)
        self.assertIn("theme_strategy", appearance_required)
        self.assertIn("typography", appearance_required)
        typography = schema["properties"]["appearance"]["properties"]["typography"]
        self.assertEqual(set(typography["properties"]["bounds"]["required"]), {"label", "body", "h3", "h2", "h1"})
        feature_required = schema["properties"]["features"]["required"]
        self.assertIn("author_menu_always_visible", feature_required)
        self.assertIn("brand_palette_lock", feature_required)
        self.assertIn("typography_editor", feature_required)
        self.assertIn("typography_bounds", feature_required)
        self.assertIn("contextual_editor_toolbar", feature_required)
        self.assertIn("per_element_text_style", feature_required)
        self.assertIn("visual_style_editor", feature_required)
        route_evaluation = schema["properties"]["delivery"]["properties"]["route_evaluation"]
        self.assertEqual(
            set(route_evaluation["properties"]["user_selected"]["items"]["enum"]),
            {"self-contained-html", "hosted-site", "native-presentation"},
        )
        starter_path = SKILL / "scripts" / "init_project.py"
        spec = importlib.util.spec_from_file_location("init_delivery_routing", starter_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        starter_routes = module.build_contract()["delivery"]["route_evaluation"]
        self.assertEqual(starter_routes["status"], "pending")
        self.assertEqual(starter_routes["user_selected"], ["self-contained-html"])

    def test_no_external_code_is_declared(self) -> None:
        lock = json.loads((ROOT / "release" / "vendor-lock.json").read_text(encoding="utf-8"))
        self.assertFalse(lock["bundled_external_code"])
        self.assertTrue(all(not item["included_paths"] for item in lock["references"]))

    def test_chat_skill_zip_shapes_when_built(self) -> None:
        manifest = json.loads((ROOT / "release" / "manifest.json").read_text(encoding="utf-8"))
        archives = [
            ROOT / "dist" / f"presentation-studio-{manifest['version']}-chatgpt.zip",
            ROOT / "dist" / f"presentation-studio-{manifest['version']}-claude.zip",
        ]
        if not all(archive.exists() for archive in archives):
            self.skipTest("Chat skill release archives have not been built yet.")
        for archive in archives:
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
            self.assertIn("presentation-studio/SKILL.md", names)
            self.assertTrue(all(name.startswith("presentation-studio/") for name in names))


if __name__ == "__main__":
    unittest.main()
