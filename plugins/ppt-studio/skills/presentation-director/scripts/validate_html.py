#!/usr/bin/env python3
"""Static checks for PPT Studio HTML outputs."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.slide_ids: list[str] = []
        self.edit_ids: list[str] = []
        self.references: list[str] = []
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
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[values["name"] or ""] = values["content"] or ""
        if tag == "script" and identifier == "presentation-project-data":
            self.has_project_data = True
        for key in ("src", "href", "poster"):
            value = values.get(key)
            if value:
                self.references.append(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    source = args.html.read_text(encoding="utf-8")
    deck = DeckParser()
    deck.feed(source)
    errors: list[str] = []
    warnings: list[str] = []

    if not re.match(r"\s*<!doctype html>", source, re.I):
        errors.append("Missing HTML doctype.")
    if not deck.slide_ids:
        errors.append("No slides detected.")
    duplicate_ids = sorted({item for item in deck.ids if deck.ids.count(item) > 1})
    duplicate_edit_ids = sorted({item for item in deck.edit_ids if deck.edit_ids.count(item) > 1})
    if duplicate_ids:
        errors.append("Duplicate DOM IDs: " + ", ".join(duplicate_ids))
    if duplicate_edit_ids:
        errors.append("Duplicate data-edit-id values: " + ", ".join(duplicate_edit_ids))
    for ref in deck.references:
        if ref.startswith(("/Users/", "file://", "C:\\")):
            errors.append(f"Absolute local reference: {ref}")
        elif not ref.startswith(("data:", "blob:", "#", "mailto:", "tel:", "javascript:")) and not re.match(r"https?://", ref):
            warnings.append(f"External local asset remains: {ref}")
    if "[TODO:" in source or "TODO:" in source:
        errors.append("TODO placeholder remains in HTML.")
    if "1920" not in source or "1080" not in source:
        warnings.append("Could not confirm a 1920 x 1080 fixed stage.")
    if not deck.has_project_data:
        warnings.append("Embedded presentation-project-data was not found.")
    if not deck.edit_ids:
        warnings.append("No editable text IDs were found.")
    if "prefers-reduced-motion" not in source:
        warnings.append("Reduced-motion CSS was not found.")
    for theme in ("light", "dark", "custom"):
        if f'data-theme="{theme}"' not in source and f"data-theme='{theme}'" not in source:
            warnings.append(f"Theme contract was not found: {theme}.")
    for token in ("--slide-bg", "--surface", "--text", "--accent", "--accent-2"):
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
