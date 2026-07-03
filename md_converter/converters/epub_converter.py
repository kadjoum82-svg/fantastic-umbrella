from __future__ import annotations

import posixpath
from urllib.parse import urlsplit

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
    assets: dict[str, bytes] = {}

    image_items = {
        item.get_name(): item for item in book.get_items() if (item.media_type or "").startswith("image/")
    }

    title_meta = book.get_metadata("DC", "title")
    if title_meta:
        parts.append(f"# {title_meta[0][0]}")

    # Parcourt tous les documents du spine, sans limite de chapitres/pages.
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        _extract_chapter_images(soup, item.get_name(), image_items, assets)

        chapter_md = html_to_md(str(soup), heading_style="ATX", bullets="-").strip()
        if chapter_md:
            parts.append(chapter_md)

    if len(parts) <= (1 if title_meta else 0):
        warnings.append("Aucun contenu textuel trouvé dans l'EPUB.")

    markdown = "\n\n".join(parts).strip() + "\n"
    return ConversionResult(markdown=markdown, warnings=warnings, assets=assets)


def _extract_chapter_images(
    soup: BeautifulSoup,
    chapter_name: str,
    image_items: dict[str, "epub.EpubItem"],
    assets: dict[str, bytes],
) -> None:
    """Résout les <img> du chapitre vers les images embarquées dans l'EPUB et
    les place dans `assets`, en réécrivant le src vers ce même chemin relatif
    afin que les liens du Markdown produit restent valides une fois écrits sur
    disque à côté du fichier .md."""
    base_dir = posixpath.dirname(chapter_name)
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue

        split_src = urlsplit(src)
        if split_src.scheme:  # URL absolue ou data: URI : rien à résoudre dans le paquet EPUB
            continue

        resolved = posixpath.normpath(posixpath.join(base_dir, split_src.path))
        item = image_items.get(resolved)
        if item is None:
            continue

        assets[resolved] = item.get_content()
        img["src"] = resolved
