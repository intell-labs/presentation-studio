#!/usr/bin/env python3
"""Static checks for PPT Studio HTML outputs."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


CORE_RUNTIME_IDS = (
    "deck-stage",
    "deck-chrome",
    "prev",
    "next",
    "menu-trigger",
    "control-menu",
    "save-status",
    "save-label",
    "theme-dialog",
    "typography-dialog",
    "element-toolbar",
    "help-dialog",
    "about-dialog",
    "presentation-project-data",
    "ppt-studio-attribution",
)
CORE_RUNTIME_MARKERS = (
    "const DESIGN_W=1920,DESIGN_H=1080",
    "showSaveFilePicker",
    "showOpenFilePicker",
    "pushState",
    "data-present-step=\"required\"",
    "classList.toggle('is-active'",
    "toggleAttribute('inert'",
    "stampEditBaselines",
    "preserve_browser_edits",
    "data-view-mode=\"audience\"",
    "data-author-control",
    "author_menu_always_visible",
    "data-shortcut=\"E\"",
    "data-shortcut=\"Alt/⌥ Y\"",
    "typography_editor",
    "typography_bounds",
    "typography-target",
    "contextual_editor_toolbar",
    "per_element_text_style",
    "visual_style_editor",
    "element-style-target",
    "data-style-id",
    "--brand-primary",
    "--brand-secondary",
    "prefers-reduced-transparency",
    "prefers-contrast:more",
    "--content-safe-bottom",
    "--content-safe-right",
    "data-qa-box",
)
RUNTIME_VERSION = "base-deck-v2"


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.slide_ids: list[str] = []
        self.edit_ids: list[str] = []
        self.style_ids: list[str] = []
        self.references: list[tuple[str, str, str]] = []
        self.meta: dict[str, str] = {}
        self.has_project_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            self.ids.append(identifier)
        classes = set((values.get("class") or "").split())
        if tag == "section" and ("slide" in classes or identifier and identifier.startswith("hoja-")):
            self.slide_ids.append(identifier or "")
        if values.get("data-edit-id"):
            self.edit_ids.append(values["data-edit-id"] or "")
        if values.get("data-style-id"):
            self.style_ids.append(values["data-style-id"] or "")
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[values["name"] or ""] = values["content"] or ""
        if tag == "script" and identifier == "presentation-project-data":
            self.has_project_data = True
        for key in ("src", "href", "poster"):
            value = values.get(key)
            if value:
                self.references.append((tag, key, value))
        if values.get("srcset") and not (values["srcset"] or "").lstrip().startswith("data:"):
            for candidate in (values["srcset"] or "").split(","):
                value = candidate.strip().split(" ", 1)[0]
                if value:
                    self.references.append((tag, "srcset", value))


class TextCoverageParser(HTMLParser):
    """Find visible slide text that is not inside a stable editable node."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, bool, bool, bool]] = []
        self.uncovered: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        parent = self.stack[-1] if self.stack else ("", False, False, False)
        in_slide = parent[1] or "slide" in classes or (values.get("id") or "").startswith("hoja-")
        in_edit = parent[2] or bool(values.get("data-edit-id"))
        ignored = parent[3] or tag in {"script", "style", "svg", "title"} or bool(classes & {"notes", "sr-only"})
        if tag not in self.VOID:
            self.stack.append((tag, in_slide, in_edit, ignored))

    def handle_endtag(self, tag: str) -> None:
        wanted = tag.lower()
        index = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == wanted), None)
        if index is not None:
            del self.stack[index:]

    def handle_data(self, data: str) -> None:
        if not self.stack:
            return
        _tag, in_slide, in_edit, ignored = self.stack[-1]
        text = " ".join(data.split())
        if in_slide and not in_edit and not ignored and text:
            self.uncovered.append(text[:80])


def runtime_contract_errors(source: str, deck: DeckParser) -> list[str]:
    errors: list[str] = []
    if deck.meta.get("ppt-studio-runtime") != RUNTIME_VERSION:
        errors.append(f"PPT Studio runtime metadata must be {RUNTIME_VERSION}.")
    if f'data-ppt-studio-runtime="{RUNTIME_VERSION}"' not in source:
        errors.append("PPT Studio runtime root marker is missing.")
    missing_ids = sorted(set(CORE_RUNTIME_IDS) - set(deck.ids))
    if missing_ids:
        errors.append("PPT Studio runtime controls are missing: " + ", ".join(missing_ids))
    missing_markers = [marker for marker in CORE_RUNTIME_MARKERS if marker not in source]
    if missing_markers:
        errors.append("PPT Studio runtime behavior is missing: " + ", ".join(missing_markers))
    chrome_match = re.search(r'<nav\b[^>]*id=["\']deck-chrome["\'][^>]*>(.*?)</nav>', source, re.I | re.S)
    if not chrome_match:
        errors.append("Unified deck-chrome navigation was not found.")
    else:
        chrome = chrome_match.group(1)
        positions = [chrome.find(f'id="{identifier}"') for identifier in ("prev", "page-count", "next", "menu-trigger")]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            errors.append("deck-chrome must order controls as previous, counter, next, menu.")
        if 'id="control-menu"' not in chrome:
            errors.append("The control menu must be anchored inside deck-chrome.")
    if ".deck-chrome .page-count,.deck-chrome .menu-trigger,.deck-chrome .control-menu{display:none" not in source:
        errors.append("Mobile controls must collapse to arrows only.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    source = args.html.read_text(encoding="utf-8")
    deck = DeckParser()
    deck.feed(source)
    coverage = TextCoverageParser()
    coverage.feed(source)
    errors: list[str] = []
    warnings: list[str] = []

    if not re.match(r"\s*<!doctype html>", source, re.I):
        errors.append("Missing HTML doctype.")
    if not deck.slide_ids:
        errors.append("No slides detected.")
    duplicate_ids = sorted({item for item in deck.ids if deck.ids.count(item) > 1})
    duplicate_edit_ids = sorted({item for item in deck.edit_ids if deck.edit_ids.count(item) > 1})
    duplicate_style_ids = sorted({item for item in deck.style_ids if deck.style_ids.count(item) > 1})
    errors.extend(runtime_contract_errors(source, deck))
    if duplicate_ids:
        errors.append("Duplicate DOM IDs: " + ", ".join(duplicate_ids))
    if duplicate_edit_ids:
        errors.append("Duplicate data-edit-id values: " + ", ".join(duplicate_edit_ids))
    if duplicate_style_ids:
        errors.append("Duplicate data-style-id values: " + ", ".join(duplicate_style_ids))
    for tag, attribute, ref in deck.references:
        if ref.startswith(("/Users/", "file://", "C:\\")):
            errors.append(f"Absolute local reference: {ref}")
        elif re.match(r"https?://", ref) and (attribute in {"src", "poster", "srcset"} or tag == "link"):
            errors.append(f"Remote asset prevents self-contained delivery: {ref}")
        elif not ref.startswith(("data:", "blob:", "#", "mailto:", "tel:", "javascript:")) and not re.match(r"https?://", ref):
            warnings.append(f"External local asset remains: {ref}")
    if "[TODO:" in source or "TODO:" in source:
        errors.append("TODO placeholder remains in HTML.")
    if "1920" not in source or "1080" not in source:
        warnings.append("Could not confirm a 1920 x 1080 fixed stage.")
    style_blocks = re.findall(r"<style\b[^>]*>(.*?)</style>", source, re.I | re.S)
    for style_source in style_blocks:
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", style_source, re.I | re.S):
            ref = match.group(2).strip()
            if ref.startswith(("data:", "blob:", "#")):
                continue
            if re.match(r"https?://|//", ref):
                errors.append(f"Remote CSS asset prevents self-contained delivery: {ref}")
            elif ref:
                warnings.append(f"External local CSS asset remains: {ref}")
        for match in re.finditer(r"@import\s+(?:url\()?\s*(['\"])(.*?)\1", style_source, re.I):
            ref = match.group(2).strip()
            if ref.startswith(("data:", "blob:")):
                continue
            if re.match(r"https?://|//", ref):
                errors.append(f"Remote CSS import prevents self-contained delivery: {ref}")
            else:
                warnings.append(f"External local CSS import remains: {ref}")
    if not deck.has_project_data:
        warnings.append("Embedded presentation-project-data was not found.")
    if not deck.edit_ids:
        warnings.append("No editable text IDs were found.")
    if coverage.uncovered:
        sample = " | ".join(coverage.uncovered[:5])
        warnings.append(f"Visible slide text is missing data-edit-id: {sample}")
    if "prefers-reduced-motion" not in source:
        warnings.append("Reduced-motion CSS was not found.")
    for theme in ("light", "dark", "custom"):
        if f'data-theme="{theme}"' not in source and f"data-theme='{theme}'" not in source:
            warnings.append(f"Theme contract was not found: {theme}.")
    for token in ("--slide-bg", "--surface", "--text", "--accent", "--accent-2", "--brand-primary", "--brand-secondary"):
        if token not in source:
            warnings.append(f"Theme token was not found: {token}.")
    if 'id="theme-dialog"' not in source:
        warnings.append("Custom theme dialog was not found.")
    if deck.meta.get("generator") != "PPT Studio by intellbits":
        warnings.append("PPT Studio generator attribution was not found.")
    if deck.meta.get("generator-url") != "https://intellbits.com":
        warnings.append("PPT Studio generator URL was not found.")
    if 'id="about-dialog"' not in source:
        warnings.append("PPT Studio About dialog was not found.")
    if "Apache-2.0" not in source or "intellbits.com" not in source:
        warnings.append("PPT Studio runtime attribution is incomplete.")
    project_match = re.search(
        r'<script\b[^>]*id=["\']presentation-project-data["\'][^>]*>\s*(.*?)\s*</script>',
        source,
        re.I | re.S,
    )
    if project_match:
        try:
            project_data = json.loads(project_match.group(1))
            if project_data.get("schema_version") != "1.4":
                errors.append("Embedded project data must use schema_version 1.4.")
            features = project_data.get("features", {})
            if features.get("default_view") != "audience":
                warnings.append("Audience view is not the default delivery mode.")
            required_features = {
                "author_mode", "editable_text", "preserve_browser_edits", "save_workflow",
                "author_menu_always_visible", "safe_file_binding", "deep_links", "unified_control_cluster", "isolated_previews",
                "mobile_light_controls",
                "visual_geometry_qa", "all_state_rendering", "brand_usage_policy", "brand_palette_lock",
                "typography_spacing_qa", "typography_editor", "typography_bounds",
                "contextual_editor_toolbar", "per_element_text_style", "visual_style_editor",
                "gallery_visual_qa",
            }
            missing_features = sorted(feature for feature in required_features if features.get(feature) is not True)
            if missing_features:
                errors.append("Embedded project data is missing required runtime features: " + ", ".join(missing_features))
            brand_policy = project_data.get("brand", {}).get("usage_policy", {})
            required_brand_policy = {
                "names", "max_visible_marks_per_slide", "max_text_mentions_when_mark_present",
                "footer", "text_mentions_use_neutral_color", "allow_logo_recolor", "exceptions",
            }
            missing_brand_policy = sorted(required_brand_policy - set(brand_policy))
            if missing_brand_policy:
                errors.append("Embedded project data is missing brand usage policy: " + ", ".join(missing_brand_policy))
            appearance = project_data.get("appearance", {})
            palette = appearance.get("brand_palette", {})
            strategy = appearance.get("theme_strategy", {})
            missing_palette = sorted({"locked", "primary", "secondary", "dark", "light"} - set(palette))
            if missing_palette:
                errors.append("Embedded project data is missing brand palette fields: " + ", ".join(missing_palette))
            if strategy.get("preserve_brand_colors") is not True or strategy.get("inverse_anchor_slides") is not True:
                errors.append("Embedded theme strategy must preserve brand colors and inverse anchor slides.")
            typography = appearance.get("typography", {})
            families = typography.get("families", [])
            if not families or any(
                not isinstance(item, dict) or not all(item.get(key) for key in ("id", "label", "stack"))
                for item in families
            ):
                errors.append("Embedded typography must define approved font families with id, label, and stack.")
            bounds = typography.get("bounds", {})
            for role in ("label", "body", "h3", "h2", "h1"):
                values = bounds.get(role, {})
                minimum, maximum = values.get("min"), values.get("max")
                if (
                    not isinstance(minimum, (int, float))
                    or not isinstance(maximum, (int, float))
                    or minimum < 10
                    or maximum > 220
                    or minimum >= maximum
                ):
                    errors.append(f"Embedded typography bounds are invalid for {role}.")
            custom_theme = appearance.get("custom_theme", {})
            if palette.get("locked") is True and (
                str(custom_theme.get("accent", "")).lower() != str(palette.get("primary", "")).lower()
                or str(custom_theme.get("accent_2", "")).lower() != str(palette.get("secondary", "")).lower()
            ):
                errors.append("Embedded locked brand palette differs from custom theme accents.")
            visual_qa = project_data.get("visual_qa", {})
            required_visual_qa = {
                "all_slides_rendered", "all_states_rendered", "safe_areas_passed",
                "typography_spacing_passed", "geometry_report", "overlap_exceptions", "harmony_review",
            }
            missing_visual_qa = sorted(required_visual_qa - set(visual_qa))
            if missing_visual_qa:
                errors.append("Embedded project data is missing visual QA fields: " + ", ".join(missing_visual_qa))
        except json.JSONDecodeError as error:
            errors.append(f"Embedded presentation-project-data is invalid JSON: {error}")

    for warning in sorted(set(warnings)):
        print(f"WARNING: {warning}")
    if args.strict and warnings:
        errors.extend(warnings)
    for error in sorted(set(errors)):
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"HTML passes static checks: {len(deck.slide_ids)} slides, {len(deck.edit_ids)} editable text nodes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
