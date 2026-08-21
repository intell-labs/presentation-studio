#!/usr/bin/env python3
"""Inline local stylesheets, scripts, and media references into one HTML file."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


REMOTE = ("http://", "https://", "//", "data:", "blob:", "#", "mailto:", "tel:", "javascript:")
MEDIA_TAG_RE = re.compile(r"<(?:img|source|video|audio|track|input)\b[^>]*>", re.I)
ATTRIBUTE_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.S)


def is_local(value: str) -> bool:
    return bool(value) and not value.startswith(REMOTE)


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def local_path(value: str, base: Path, root: Path, allow_outside_root: bool) -> Path:
    path_value = unquote(urlsplit(value).path)
    path = (base / path_value).resolve()
    if not allow_outside_root and path != root and root not in path.parents:
        raise ValueError(f"Asset escapes the project root: {value}")
    return path


def inline_css_urls(
    css: str,
    css_dir: Path,
    root: Path,
    unresolved: list[str],
    allow_outside_root: bool,
) -> str:
    def replace(match: re.Match[str]) -> str:
        quote, value = match.group(1), match.group(2).strip()
        if not is_local(value):
            return match.group(0)
        try:
            path = local_path(value, css_dir, root, allow_outside_root)
        except ValueError as error:
            unresolved.append(str(error))
            return match.group(0)
        if not path.is_file():
            unresolved.append(str(path))
            return match.group(0)
        return f"url({quote}{data_url(path)}{quote})"
    return re.sub(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", replace, css)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--allow-outside-root",
        action="store_true",
        help="Allow local assets outside the HTML file's directory.",
    )
    args = parser.parse_args()
    source_path = args.html.resolve()
    root = source_path.parent
    output_path = (args.output or source_path.with_name(source_path.stem + "-self-contained.html")).resolve()
    if output_path == source_path:
        parser.error("--output must differ from the source HTML path.")
    html = source_path.read_text(encoding="utf-8")
    unresolved: list[str] = []

    def stylesheet(match: re.Match[str]) -> str:
        tag = match.group(0)
        attrs = {name.lower(): value for name, _quote, value in ATTRIBUTE_RE.findall(tag)}
        href = attrs.get("href", "")
        rel = set(attrs.get("rel", "").lower().split())
        if "stylesheet" not in rel or not href:
            return tag
        if not is_local(href):
            return tag
        try:
            path = local_path(href, root, root, args.allow_outside_root)
        except ValueError as error:
            unresolved.append(str(error))
            return tag
        if not path.is_file():
            unresolved.append(str(path))
            return tag
        css = inline_css_urls(
            path.read_text(encoding="utf-8"), path.parent, root, unresolved, args.allow_outside_root
        )
        return f'<style data-bundled-from="{href}">\n{css}\n</style>'

    html = re.sub(r"<link\b[^>]*>", stylesheet, html, flags=re.I)

    def script(match: re.Match[str]) -> str:
        before, src, after = match.group(1), match.group(2), match.group(3)
        if not is_local(src):
            return match.group(0)
        try:
            path = local_path(src, root, root, args.allow_outside_root)
        except ValueError as error:
            unresolved.append(str(error))
            return match.group(0)
        if not path.is_file():
            unresolved.append(str(path))
            return match.group(0)
        return f'<script{before}{after} data-bundled-from="{src}">\n{path.read_text(encoding="utf-8")}\n</script>'

    html = re.sub(r'<script\b([^>]*?)src=["\']([^"\']+)["\']([^>]*)>\s*</script>', script, html, flags=re.I)

    def bundle_value(value: str) -> str:
        if not is_local(value):
            return value
        try:
            path = local_path(value, root, root, args.allow_outside_root)
        except ValueError as error:
            unresolved.append(str(error))
            return value
        if not path.is_file():
            unresolved.append(str(path))
            return value
        return data_url(path)

    def media_tag(match: re.Match[str]) -> str:
        tag = match.group(0)

        def attribute(attribute_match: re.Match[str]) -> str:
            name, quote, value = attribute_match.groups()
            lowered = name.lower()
            if lowered in {"src", "poster"}:
                return f"{name}={quote}{bundle_value(value)}{quote}"
            if lowered == "srcset":
                candidates = []
                for candidate in value.split(","):
                    parts = candidate.strip().split()
                    if not parts:
                        continue
                    parts[0] = bundle_value(parts[0])
                    candidates.append(" ".join(parts))
                return f"{name}={quote}{', '.join(candidates)}{quote}"
            return attribute_match.group(0)

        return ATTRIBUTE_RE.sub(attribute, tag)

    html = MEDIA_TAG_RE.sub(media_tag, html)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    for path in sorted(set(unresolved)):
        print(f"UNRESOLVED: {path}")
    if unresolved and args.strict:
        return 1
    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
