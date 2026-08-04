#!/usr/bin/env python3
"""Inline local stylesheets, scripts, and media references into one HTML file."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote


REMOTE = ("http://", "https://", "//", "data:", "blob:", "#", "mailto:", "tel:", "javascript:")


def is_local(value: str) -> bool:
    return bool(value) and not value.startswith(REMOTE)


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inline_css_urls(css: str, css_dir: Path, unresolved: list[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        quote, value = match.group(1), match.group(2).strip()
        if not is_local(value):
            return match.group(0)
        path = (css_dir / unquote(value)).resolve()
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
    args = parser.parse_args()
    source_path = args.html.resolve()
    root = source_path.parent
    output_path = args.output or source_path.with_name(source_path.stem + "-self-contained.html")
    html = source_path.read_text(encoding="utf-8")
    unresolved: list[str] = []

    def stylesheet(match: re.Match[str]) -> str:
        attrs, href = match.group(1), match.group(2)
        if not is_local(href):
            return match.group(0)
        path = (root / unquote(href)).resolve()
        if not path.is_file():
            unresolved.append(str(path))
            return match.group(0)
        css = inline_css_urls(path.read_text(encoding="utf-8"), path.parent, unresolved)
        return f'<style data-bundled-from="{href}">\n{css}\n</style>'

    html = re.sub(r'<link\b([^>]*?rel=["\']stylesheet["\'][^>]*?)href=["\']([^"\']+)["\'][^>]*>', stylesheet, html, flags=re.I)

    def script(match: re.Match[str]) -> str:
        before, src, after = match.group(1), match.group(2), match.group(3)
        if not is_local(src):
            return match.group(0)
        path = (root / unquote(src)).resolve()
        if not path.is_file():
            unresolved.append(str(path))
            return match.group(0)
        return f'<script{before}{after} data-bundled-from="{src}">\n{path.read_text(encoding="utf-8")}\n</script>'

    html = re.sub(r'<script\b([^>]*?)src=["\']([^"\']+)["\']([^>]*)>\s*</script>', script, html, flags=re.I)

    def media(match: re.Match[str]) -> str:
        prefix, value, suffix = match.group(1), match.group(2), match.group(3)
        if not is_local(value):
            return match.group(0)
        path = (root / unquote(value)).resolve()
        if not path.is_file():
            unresolved.append(str(path))
            return match.group(0)
        return prefix + data_url(path) + suffix

    html = re.sub(r'((?:src|poster)=["\'])([^"\']+)(["\'])', media, html, flags=re.I)
    output_path.write_text(html, encoding="utf-8")
    for path in sorted(set(unresolved)):
        print(f"UNRESOLVED: {path}")
    if unresolved and args.strict:
        return 1
    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
