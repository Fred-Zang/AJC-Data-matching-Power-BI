from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import MAX_DOCUMENT_BYTES, OCR_DPI, OCR_LANGUAGE


class DocumentProcessingError(RuntimeError):
    pass


def _check_size(path: Path) -> None:
    if path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise DocumentProcessingError(f"Document too large: {path.name}")


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()


def _ocr_image(path: Path) -> str:
    import pytesseract
    from PIL import Image

    with Image.open(path) as image:
        return pytesseract.image_to_string(image, lang=OCR_LANGUAGE)


def _ocr_pdf(path: Path) -> str:
    import pytesseract
    from pdf2image import convert_from_path

    pages = convert_from_path(str(path), dpi=OCR_DPI)
    return "\n".join(pytesseract.image_to_string(page, lang=OCR_LANGUAGE) for page in pages)


def _convert_office_to_pdf(path: Path, output_dir: Path) -> Path:
    executable = shutil.which("libreoffice") or shutil.which("soffice")
    if not executable:
        raise DocumentProcessingError("LibreOffice is required for DOC/DOCX conversion")
    result = subprocess.run(
        [executable, "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(path)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise DocumentProcessingError("LibreOffice conversion failed")
    converted = output_dir / f"{path.stem}.pdf"
    if not converted.exists():
        raise DocumentProcessingError("LibreOffice did not produce the expected PDF")
    return converted


def extract_text(path: Path) -> str:
    """Extract text locally; no document is sent to an external AI service."""
    path = path.resolve()
    if not path.is_file():
        raise DocumentProcessingError(f"Document not found: {path}")
    _check_size(path)
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        return _read_text_file(path)
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        return _ocr_image(path)
    if suffix == ".pdf":
        text = _extract_pdf_text(path)
        return text if text.strip() else _ocr_pdf(path)
    if suffix in {".doc", ".docx", ".odt", ".rtf"}:
        with tempfile.TemporaryDirectory(prefix="ajc_cv_") as tmp:
            pdf = _convert_office_to_pdf(path, Path(tmp))
            text = _extract_pdf_text(pdf)
            return text if text.strip() else _ocr_pdf(pdf)

    raise DocumentProcessingError(f"Unsupported document type: {suffix}")
