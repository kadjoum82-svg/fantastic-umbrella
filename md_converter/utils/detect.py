from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

WEB_SCHEMES = {"http", "https"}

PDF_EXTS = {".pdf"}
DOCX_EXTS = {".docx"}
DOC_EXTS = {".doc"}
EPUB_EXTS = {".epub"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
HTML_EXTS = {".html", ".htm"}
GENERIC_EXTS = {".pptx", ".xlsx", ".csv", ".json", ".xml", ".txt"}

SUPPORTED_EXTENSIONS = (
    PDF_EXTS | DOCX_EXTS | DOC_EXTS | EPUB_EXTS | IMAGE_EXTS | HTML_EXTS | GENERIC_EXTS
)


def is_url(source: str) -> bool:
    return urlparse(source).scheme in WEB_SCHEMES


def detect_kind(source: str) -> str:
    """Détermine le type de source (pdf, docx, doc, epub, image, web, generic)."""
    if is_url(source):
        return "web"

    ext = Path(source).suffix.lower()
    if ext in PDF_EXTS:
        return "pdf"
    if ext in DOCX_EXTS:
        return "docx"
    if ext in DOC_EXTS:
        return "doc"
    if ext in EPUB_EXTS:
        return "epub"
    if ext in IMAGE_EXTS:
        return "image"
    if ext in HTML_EXTS:
        return "web"
    return "generic"
