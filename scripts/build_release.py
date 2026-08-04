#!/usr/bin/env python3
"""Build deterministic PPT Studio plugin and Claude Chat release archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "release" / "manifest.json"
DIST = ROOT / "dist"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def files_under(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_NAMES for part in path.parts)
        and path.suffix not in IGNORED_SUFFIXES
    )


def add_file(archive: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o755 if path.suffix in {".py", ".sh"} else 0o644) << 16
    archive.writestr(info, path.read_bytes())


def build_archive(source: Path, output: Path, archive_root: str) -> None:
    with zipfile.ZipFile(output, "w") as archive:
        for path in files_under(source):
            relative = path.relative_to(source).as_posix()
            add_file(archive, path, f"{archive_root}/{relative}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Replace the dist directory before building.")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    version = manifest["version"]
    plugin_root = ROOT / manifest["plugin_path"]
    skill_name = manifest["skill"]
    skill_root = plugin_root / "skills" / skill_name
    if not plugin_root.is_dir() or not skill_root.is_dir():
        raise SystemExit("Plugin or skill directory is missing.")

    if args.clean and DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    plugin_zip = DIST / f"ppt-studio-{version}-plugin.zip"
    claude_zip = DIST / f"presentation-director-{version}-claude.zip"
    build_archive(plugin_root, plugin_zip, "ppt-studio")
    build_archive(skill_root, claude_zip, skill_name)

    archives = [plugin_zip, claude_zip]
    checksum_lines = [f"{sha256(path)}  {path.name}" for path in archives]
    (DIST / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    for path in archives:
        print(path)
    print(DIST / "SHA256SUMS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
