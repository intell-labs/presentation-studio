#!/usr/bin/env python3
"""Merge browser-edited PPT Studio text and element styles into a regenerated deck.

Editable elements are matched by stable ``data-edit-id`` values. The runtime
stores ``data-edit-baseline`` hashes, which let this tool preserve only content
that changed in the browser while accepting intentional generator updates.
Per-element text styles and visual styles use independent style baselines.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html.parser
import os
import pathlib
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass


VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
BASELINE_RE = re.compile(
    r"(\sdata-edit-baseline\s*=\s*)([\"'])(.*?)(\2)", re.IGNORECASE | re.DOTALL
)
ATTRIBUTE_RE_TEMPLATE = r"(\s{attribute}\s*=\s*)([\"'])(.*?)(\2)"


@dataclass
class Editable:
    edit_id: str
    start_start: int
    start_end: int
    content_start: int
    content_end: int
    baseline: str | None
    style: str | None
    style_baseline: str | None

    def content(self, source: str) -> str:
        return source[self.content_start : self.content_end]


@dataclass
class Frame:
    tag: str
    edit_id: str | None
    start_start: int
    start_end: int
    content_start: int
    baseline: str | None
    style: str | None
    style_baseline: str | None


@dataclass
class Styleable:
    style_id: str
    start_start: int
    start_end: int
    style: str | None
    baseline: str | None


class EditableParser(html.parser.HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_offsets = [0]
        for match in re.finditer(r"\n", source):
            self.line_offsets.append(match.end())
        self.stack: list[Frame] = []
        self.editables: dict[str, Editable] = {}
        self.styleables: dict[str, Styleable] = {}

    def absolute_position(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        start = self.absolute_position()
        raw = self.get_starttag_text()
        end = start + len(raw)
        values = {name.lower(): value for name, value in attrs}
        edit_id = values.get("data-edit-id")
        baseline = values.get("data-edit-baseline")
        style = values.get("style")
        style_baseline = values.get("data-edit-style-baseline")
        style_id = values.get("data-style-id")
        if style_id:
            if style_id in self.styleables:
                raise ValueError(f"Duplicate data-style-id: {style_id}")
            self.styleables[style_id] = Styleable(
                style_id, start, end, style, values.get("data-style-baseline")
            )
        if tag.lower() in VOID_ELEMENTS:
            if edit_id:
                raise ValueError(f"Editable ID {edit_id!r} is attached to a void element.")
            return
        if edit_id and any(frame.edit_id for frame in self.stack):
            raise ValueError(f"Nested data-edit-id is not supported: {edit_id}")
        self.stack.append(Frame(tag.lower(), edit_id, start, end, end, baseline, style, style_baseline))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if any(name.lower() == "data-edit-id" for name, _value in attrs):
            raise ValueError("Editable IDs cannot be attached to self-closing elements.")

    def handle_endtag(self, tag: str) -> None:
        end = self.absolute_position()
        wanted = tag.lower()
        match_index = next(
            (index for index in range(len(self.stack) - 1, -1, -1) if self.stack[index].tag == wanted),
            None,
        )
        if match_index is None:
            return
        frame = self.stack[match_index]
        del self.stack[match_index:]
        if not frame.edit_id:
            return
        if frame.edit_id in self.editables:
            raise ValueError(f"Duplicate data-edit-id: {frame.edit_id}")
        self.editables[frame.edit_id] = Editable(
            frame.edit_id,
            frame.start_start,
            frame.start_end,
            frame.content_start,
            end,
            frame.baseline,
            frame.style,
            frame.style_baseline,
        )


def parse_editables(source: str) -> dict[str, Editable]:
    parser = EditableParser(source)
    parser.feed(source)
    parser.close()
    if parser.stack:
        editable_open = [frame.edit_id for frame in parser.stack if frame.edit_id]
        if editable_open:
            raise ValueError(f"Unclosed editable elements: {', '.join(editable_open)}")
    return parser.editables


def parse_document(source: str) -> EditableParser:
    parser = EditableParser(source)
    parser.feed(source)
    parser.close()
    return parser


def js_fnv1a(value: str) -> str:
    data = value.encode("utf-16-le", errors="surrogatepass")
    result = 0x811C9DC5
    for index in range(0, len(data), 2):
        code_unit = data[index] | (data[index + 1] << 8)
        result ^= code_unit
        result = (result * 0x01000193) & 0xFFFFFFFF
    return f"{result:08x}"


def with_baseline(start_tag: str, baseline: str) -> str:
    if BASELINE_RE.search(start_tag):
        return BASELINE_RE.sub(lambda match: f'{match.group(1)}"{baseline}"', start_tag, count=1)
    insertion = start_tag.rfind("/>")
    if insertion < 0:
        insertion = start_tag.rfind(">")
    if insertion < 0:
        raise ValueError("Malformed editable start tag.")
    return start_tag[:insertion] + f' data-edit-baseline="{baseline}"' + start_tag[insertion:]


def with_attribute(start_tag: str, attribute: str, value: str | None) -> str:
    pattern = re.compile(
        ATTRIBUTE_RE_TEMPLATE.format(attribute=re.escape(attribute)),
        re.IGNORECASE | re.DOTALL,
    )
    if value is None:
        return pattern.sub("", start_tag, count=1)
    encoded = html.escape(value, quote=True)
    if pattern.search(start_tag):
        return pattern.sub(lambda match: f'{match.group(1)}"{encoded}"', start_tag, count=1)
    insertion = start_tag.rfind("/>")
    if insertion < 0:
        insertion = start_tag.rfind(">")
    if insertion < 0:
        raise ValueError("Malformed start tag.")
    return start_tag[:insertion] + f' {attribute}="{encoded}"' + start_tag[insertion:]


def merge(existing_source: str, generated_source: str) -> tuple[str, list[str], list[str]]:
    existing_document = parse_document(existing_source)
    generated_document = parse_document(generated_source)
    existing = existing_document.editables
    generated = generated_document.editables
    changed: dict[str, Editable] = {}
    unknown_baseline: list[str] = []

    for edit_id, element in existing.items():
        content_hash = js_fnv1a(element.content(existing_source))
        if element.baseline is None:
            changed[edit_id] = element
            unknown_baseline.append(edit_id)
        elif content_hash != element.baseline.lower():
            changed[edit_id] = element

    dropped = sorted(set(changed) - set(generated))
    if dropped:
        raise ValueError(
            "Refusing to drop browser edits whose IDs are absent from the generated deck: "
            + ", ".join(dropped)
        )

    changed_text_styles = {
        edit_id: element
        for edit_id, element in existing.items()
        if element.style_baseline is not None
        and js_fnv1a(element.style or "") != element.style_baseline.lower()
    }
    changed_visual_styles = {
        style_id: element
        for style_id, element in existing_document.styleables.items()
        if element.baseline is not None
        and js_fnv1a(element.style or "") != element.baseline.lower()
    }
    dropped_text_styles = sorted(set(changed_text_styles) - set(generated))
    dropped_visual_styles = sorted(set(changed_visual_styles) - set(generated_document.styleables))
    if dropped_text_styles or dropped_visual_styles:
        missing = [*(f"text-style:{item}" for item in dropped_text_styles), *(f"visual-style:{item}" for item in dropped_visual_styles)]
        raise ValueError("Refusing to drop browser-edited styles whose IDs are absent from the generated deck: " + ", ".join(missing))

    replacements: list[tuple[int, int, str]] = []
    start_tags: dict[tuple[int, int], str] = {}
    for edit_id, target in generated.items():
        generated_content = target.content(generated_source)
        baseline = js_fnv1a(generated_content)
        key = (target.start_start, target.start_end)
        start_tag = start_tags.get(key, generated_source[target.start_start : target.start_end])
        start_tag = with_baseline(start_tag, baseline)
        start_tag = with_attribute(start_tag, "data-edit-style-baseline", js_fnv1a(target.style or ""))
        if edit_id in changed_text_styles:
            start_tag = with_attribute(start_tag, "style", changed_text_styles[edit_id].style)
        start_tags[key] = start_tag
        if edit_id in changed:
            replacements.append(
                (target.content_start, target.content_end, changed[edit_id].content(existing_source))
            )

    for style_id, target in generated_document.styleables.items():
        key = (target.start_start, target.start_end)
        start_tag = start_tags.get(key, generated_source[target.start_start : target.start_end])
        start_tag = with_attribute(start_tag, "data-style-baseline", js_fnv1a(target.style or ""))
        if style_id in changed_visual_styles:
            start_tag = with_attribute(start_tag, "style", changed_visual_styles[style_id].style)
        start_tags[key] = start_tag

    replacements.extend((start, end, tag) for (start, end), tag in start_tags.items())

    result = generated_source
    for start, end, replacement in sorted(replacements, reverse=True):
        result = result[:start] + replacement + result[end:]
    return result, sorted(changed), sorted(unknown_baseline)


def backup_file(path: pathlib.Path, backup_dir: pathlib.Path | None) -> pathlib.Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    directory = backup_dir or path.parent
    directory.mkdir(parents=True, exist_ok=True)
    candidate = directory / f"{path.stem}.backup-{timestamp}{path.suffix}"
    counter = 2
    while candidate.exists():
        candidate = directory / f"{path.stem}.backup-{timestamp}-{counter}{path.suffix}"
        counter += 1
    shutil.copy2(path, candidate)
    return candidate


def write_atomic(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preserve browser text edits while accepting a regenerated PPT Studio deck."
    )
    parser.add_argument("existing", type=pathlib.Path, help="Last saved browser-edited HTML")
    parser.add_argument("generated", type=pathlib.Path, help="Freshly generated HTML")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Merged output HTML")
    parser.add_argument("--backup-dir", type=pathlib.Path, help="Optional backup directory")
    parser.add_argument("--no-backup", action="store_true", help="Do not back up an existing output")
    args = parser.parse_args()

    try:
        existing_source = args.existing.read_text(encoding="utf-8")
        generated_source = args.generated.read_text(encoding="utf-8")
        merged, changed, unknown = merge(existing_source, generated_source)
        backup = None
        if args.output.exists() and not args.no_backup:
            backup = backup_file(args.output, args.backup_dir)
        write_atomic(args.output, merged)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Merged {len(changed)} browser-edited field(s) into {args.output}")
    if backup:
        print(f"Backup: {backup}")
    if unknown:
        print(
            "Warning: preserved fields without baselines: " + ", ".join(unknown),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
