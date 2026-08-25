from __future__ import annotations

import os
from pathlib import Path


def _path_from_env(name: str, default: str) -> Path:
    return Path(os.getenv(name, default)).expanduser().resolve()


RUNTIME_ROOT = _path_from_env("AJC_RUNTIME_ROOT", "runtime")
REFERENCE_ROOT = _path_from_env("AJC_REFERENCE_ROOT", "examples/reference")
CV_ROOT = _path_from_env("AJC_CV_ROOT", "examples/cv")
SOURCE_EXPORT_ROOT = _path_from_env("AJC_SOURCE_EXPORT_ROOT", "examples/source_exports")

MAX_DOCUMENT_BYTES = int(os.getenv("AJC_MAX_DOCUMENT_BYTES", str(20 * 1024 * 1024)))
OCR_DPI = int(os.getenv("AJC_OCR_DPI", "300"))
OCR_LANGUAGE = os.getenv("AJC_OCR_LANGUAGE", "fra+eng")


def ensure_runtime_dirs() -> None:
    for path in (
        RUNTIME_ROOT,
        RUNTIME_ROOT / "text",
        RUNTIME_ROOT / "tokens",
        RUNTIME_ROOT / "results",
        RUNTIME_ROOT / "staging",
    ):
        path.mkdir(parents=True, exist_ok=True)
