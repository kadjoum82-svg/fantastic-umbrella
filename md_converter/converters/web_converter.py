from __future__ import annotations

from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md
from readability import Document as ReadabilityDocument

from ..exceptions import ConversionError
from ..utils.detect import is_url
from .base import ConversionResult

DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; md-converter/1.0)"}


def convert_web(source: str, *, timeout: int = 30) -> ConversionResult:
    warnings: list[str] = []

    if is_url(source):
        html = _fetch(source, timeout=timeout)
    else:
        try:
            html = Path(source).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise ConversionError(f"Impossible de lire le fichier HTML '{source}': {exc}") from exc

    title = None
    content_html = html
    try:
        readability_doc = ReadabilityDocument(html)
        title = readability_doc.short_title() or None
        content_html = readability_doc.summary(html_partial=True)
    except Exception:
        warnings.append("Extraction du contenu principal impossible ; conversion de la page entière.")

    soup = BeautifulSoup(content_html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    body_md = html_to_md(str(soup), heading_style="ATX", bullets="-").strip()

    parts = [f"# {title}"] if title else []
    parts.append(body_md)

    markdown = "\n\n".join(p for p in parts if p).strip() + "\n"
    return ConversionResult(markdown=markdown, warnings=warnings)


def _fetch(url: str, *, timeout: int) -> str:
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ConversionError(f"Impossible de récupérer la page web '{url}': {exc}") from exc
    return response.text
