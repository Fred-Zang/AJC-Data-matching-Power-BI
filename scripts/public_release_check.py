from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "runtime"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".csv", ".yml", ".yaml", ".toml", ".example", ".dockerignore", ".gitignore"}

PATTERNS = {
    "JWT/Bearer token": re.compile(r"Bearer\s+eyJ[A-Za-z0-9._-]{20,}", re.I),
    "private home path": re.compile(r"/home/[A-Z0-9._-]+(?:/|\\b)", re.I),
    "Windows production path": re.compile(
    r"(?<![A-Z0-9])[A-Z]:[/\\][^\r\n]*(?:projet|AJC)",
    re.I,
),
    "email address": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    "hard-coded credential": re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|bearer[_-]?token)\s*=\s*[\"'][^\"']{8,}[\"']"),
}


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in {".gitignore", ".dockerignore", ".env.example"} or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main() -> int:
    failures: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label}: {path.relative_to(ROOT)}")

    if failures:
        print("Public release check: FAILED")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Public release check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
