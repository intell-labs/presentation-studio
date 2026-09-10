#!/usr/bin/env python3
"""Inventory existing deck assets and verify decisions against the actual HTML.

No network access or source mutation. Asset fingerprints survive file-to-data-URI
bundling; inline SVG fingerprints ignore attribute order and formatting whitespace.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, unquote_to_bytes, urlparse


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def contract_digest(project: dict) -> str:
    # QA metadata lives outside the design being approved; never embed a self-hash.
    def normalized(value):
        if isinstance(value, dict):
            return {k: normalized(v) for k, v in value.items()}
        if isinstance(value, list):
            return [normalized(v) for v in value]
        return int(value) if isinstance(value, float) and value.is_integer() else value
    return digest(json.dumps(normalized({k: v for k, v in project.items() if k != "visual_qa"}),
                             sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


class Node:
    def __init__(self, tag="root", attrs=None, parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs or []), parent
        self.children = []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def canonical(self):
        return [self.tag, sorted((k, v) for k, v in self.attrs.items()
                               if not k.startswith("data-") and k != "class"),
                [child.canonical() if isinstance(child, Node) else child.strip()
                 for child in self.children if isinstance(child, Node) or child.strip()]]

    def slide(self):
        node = self
        while node:
            if "slide" in (node.attrs.get("class") or "").split():
                return node.attrs.get("id", "")
            node = node.parent
        return ""


class Document(HTMLParser):
    VOID = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def asset_digest(node, base):
    if node.tag == "svg":
        return digest(json.dumps(node.canonical(), ensure_ascii=False).encode())
    ref = node.attrs.get("src", "")
    if ref.startswith("data:"):
        meta, value = ref.split(",", 1)
        return digest(base64.b64decode(value) if ";base64" in meta else unquote_to_bytes(value))
    if ref and not urlparse(ref).scheme and not ref.startswith("//"):
        file = base / unquote(ref.split("?", 1)[0].split("#", 1)[0])
        if file.is_file():
            return digest(file.read_bytes())
    return ""  # Never claim remote or unresolved assets were verified.


def inventory(html: Path):
    document = Document(html.read_text(encoding="utf-8"))
    result = []
    for node in document.root.walk():
        if node.tag not in {"img", "svg"} or not node.slide():
            continue
        fingerprint = asset_digest(node, html.parent)
        result.append({"id": node.attrs.get("data-asset-id", ""), "slide": node.slide(),
                       "kind": node.tag, "sha256": fingerprint,
                       "source": "embedded" if node.tag == "svg" or node.attrs.get("src", "").startswith("data:")
                       else node.attrs.get("src", ""), "alt": node.attrs.get("alt", "")})
    return {"html_sha256": digest(html.read_bytes()), "assets": result}


def design_errors(project):
    errors = []
    appearance = project.get("appearance", {})
    themes = appearance.get("available_themes", [])
    if not isinstance(themes, list) or not themes or any(t not in ("light", "dark", "custom") for t in themes) or len(themes) != len(set(themes)):
        errors.append("design.themes: available_themes must be a nonempty unique list of supported themes.")
    if appearance.get("default_theme") not in themes:
        errors.append("design.themes: default_theme is not enabled.")
    slides = project.get("slides", [])
    for slide in slides:
        if slide.get("role") not in {"cover", "section", "content", "data", "closing"}:
            errors.append(f"design.role: {slide.get('id')} needs an explicit slide role.")
        if slide.get("tone") not in {"anchor", "content"}:
            errors.append(f"design.tone: {slide.get('id')} needs an explicit tone.")
        if appearance.get("theme_strategy", {}).get("inverse_anchor_slides") and slide.get("role") in {"cover", "closing"} and slide.get("tone") != "anchor":
            errors.append(f"design.anchor: {slide.get('id')} must be an anchor for the approved inversion strategy.")
    design = project.get("design_contract")
    if not isinstance(design, dict):
        return errors + ["design.contract: missing design_contract; migrate using references/enhancement-contract.md."]
    assets = design.get("assets", [])
    ids = [a.get("id") for a in assets]
    if len(ids) != len(set(ids)) or any(not i for i in ids):
        errors.append("assets.ids: asset decision IDs must be unique and nonempty.")
    for a in assets:
        if a.get("decision") not in {"keep", "replace", "remove", "add"} or not a.get("reason"):
            errors.append(f"assets.decision: {a.get('id')} needs a decision and reason.")
        if a.get("decision") != "remove" and (not re.fullmatch(r"[a-f0-9]{64}", a.get("sha256", "")) or not a.get("slides")):
            errors.append(f"assets.fingerprint: {a.get('id')} needs a verified fingerprint and target slides.")
        if a.get("decision") == "keep" and a.get("baseline_sha256") != a.get("sha256"):
            errors.append(f"assets.changed: {a.get('id')} marked keep but differs from baseline.")
        if set(a.get("slides", [])) - {s.get("id") for s in slides}:
            errors.append(f"assets.slide: {a.get('id')} references an unknown slide.")
        if "themes" in a and (not a["themes"] or set(a["themes"]) - set(themes)):
            errors.append(f"assets.theme: {a.get('id')} references a disabled or empty theme list.")
    if project.get("workflow", {}).get("mode") == "enhance":
        if not re.fullmatch(r"[a-f0-9]{64}", design.get("baseline_sha256", "")):
            errors.append("assets.baseline: enhance requires the SHA-256 of the approved starting HTML.")
        baseline = set(design.get("baseline_asset_hashes", []))
        accounted = {a.get("baseline_sha256") for a in assets}
        if baseline - accounted:
            errors.append("assets.unaccounted: baseline assets lack keep/replace/remove decisions.")
    for case in design.get("cases", []):
        if not all(case.get(k) for k in ("id", "client", "project", "function", "confirmation")):
            errors.append("design.case: record client, project, function and confirmation independently.")
        if set(case.get("evidence_asset_ids", [])) - set(ids):
            errors.append(f"design.case: unknown evidence asset in {case.get('id')}.")
    return errors


def artifact_errors(html: Path, project):
    errors = design_errors(project)
    nodes = list(Document(html.read_text(encoding="utf-8")).root.walk())
    actual = {n.attrs.get("id"): n for n in nodes if "slide" in (n.attrs.get("class") or "").split()}
    planned = {s.get("id"): s for s in project.get("slides", [])}
    if set(actual) != set(planned):
        errors.append("design.slides: DOM slide IDs differ from the approved contract.")
    for identifier, slide in planned.items():
        if identifier in actual:
            attrs = actual[identifier].attrs
            if attrs.get("data-slide-role") != slide.get("role"):
                errors.append(f"design.role: {identifier} DOM role differs from the contract.")
            if attrs.get("data-tone", "content") != slide.get("tone"):
                errors.append(f"design.anchor: {identifier} DOM tone differs from the contract.")
    actual_assets = inventory(html)["assets"]
    for asset in project.get("design_contract", {}).get("assets", []):
        matches = [a for a in actual_assets if a["id"] == asset.get("id")]
        if asset.get("decision") == "remove":
            if matches:
                errors.append(f"assets.removed-present: {asset['id']} is still present.")
            continue
        for slide in asset.get("slides", []):
            selected = [a for a in matches if a["slide"] == slide]
            if len(selected) != 1:
                errors.append(f"assets.missing: {asset['id']} must appear exactly once on {slide}.")
            elif selected[0]["sha256"] != asset.get("sha256"):
                errors.append(f"assets.changed: {asset['id']} differs from the approved asset on {slide}.")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--project", type=Path, help="Check decisions instead of producing inventory")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = artifact_errors(args.html, json.loads(args.project.read_text())) if args.project else inventory(args.html)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.resolve() in {args.html.resolve(), args.project.resolve() if args.project else None}:
            parser.error("Output must not overwrite an input.")
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return int(bool(result)) if args.project else 0


if __name__ == "__main__":
    raise SystemExit(main())
