#!/usr/bin/env python3
"""Extract audience-visible text from the final HTML for language QA."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
SKIP_CLASSES = {"notes", "speaker-notes", "control-menu", "deck-controls", "license-panel"}


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, str | None]] = []
        self.items: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        parent_skip = self.stack[-1][1] if self.stack else False
        hidden = (
            parent_skip
            or tag in SKIP_TAGS
            or bool(classes & SKIP_CLASSES)
            or "hidden" in values
            or values.get("aria-hidden") == "true"
            or values.get("data-navigation") == "speaker-only"
        )
        self.stack.append((tag, hidden, values.get("data-edit-id") or values.get("id")))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if self.stack and self.stack[-1][1]:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        marker = next((item[2] for item in reversed(self.stack) if item[2]), "")
        self.items.append({"id": marker or "", "text": text})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = args.html.read_text(encoding="utf-8")
    extractor = VisibleTextParser()
    extractor.feed(source)
    result = extractor.items
    rendered = json.dumps(result, ensure_ascii=False, indent=2) if args.json else "\n".join(item["text"] for item in result)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(args.output)
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
