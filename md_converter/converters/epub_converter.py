from __future__ import annotations

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub
from markdownify import markdownify as html_to_md

from ..exceptions import ConversionError
from .base import ConversionResult


def convert_epub(path: str) -> ConversionResult:
    try:
        book = epub.read_epub(path)
    except Exception as exc:
        raise ConversionError(f"Impossible de lire l'EPUB '{path}': {exc}") from exc

    warnings: list[str] = []
    parts: list[str] = []

    title_meta = book.get_metadata("DC", "title")
    if title_meta:
        parts.append(f"# {title_meta[0][0]}")

    # Parcourt tous les documents du spine, sans limite de chapitres/pages.
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        chapter_md = html_to_md(str(soup), heading_style="ATX", bullets="-").strip()
        if chapter_md:
            parts.append(chapter_md)

    if len(parts) <= (1 if title_meta else 0):
        warnings.append("Aucun contenu textuel trouvé dans l'EPUB.")

    markdown = "\n\n".join(parts).strip() + "\n"
    return ConversionResult(markdown=markdown, warnings=warnings)
