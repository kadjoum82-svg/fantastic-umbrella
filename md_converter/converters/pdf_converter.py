from __future__ import annotations

import io
import statistics

import fitz  # PyMuPDF

from ..exceptions import ConversionError
from .base import ConversionResult

MIN_CHARS_FOR_TEXT_PAGE = 20
FONT_SAMPLE_PAGES = 15
HEADING_RATIOS = ((1.45, 1), (1.25, 2), (1.1, 3))


def convert_pdf(path: str, *, ocr: bool = True, ocr_lang: str = "eng+fra") -> ConversionResult:
    """Convertit un PDF en Markdown, page par page, sans limite de pages.

    Chaque page est traitée indépendamment (streaming), ce qui permet de gérer des
    documents de plusieurs milliers de pages sans charger l'ensemble en mémoire ni
    imposer de plafond artificiel. Les pages sans texte natif (scans) basculent en
    OCR si activé.
    """
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise ConversionError(f"Impossible d'ouvrir le PDF '{path}': {exc}") from exc

    warnings: list[str] = []
    parts: list[str] = []

    try:
        body_size = _median_font_size(doc)

        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            page_md = _page_to_markdown(page, body_size)

            if len(page_md) < MIN_CHARS_FOR_TEXT_PAGE:
                if ocr:
                    ocr_text = _ocr_page(page, lang=ocr_lang)
                    if ocr_text:
                        page_md = ocr_text
                    else:
                        page_md = "*[Page vide ou illisible]*"
                        warnings.append(
                            f"Page {page_index + 1}: aucun texte détecté (ni natif ni OCR)."
                        )
                else:
                    page_md = "*[Page probablement scannée ; OCR désactivé]*"
                    warnings.append(f"Page {page_index + 1}: page probablement scannée, OCR désactivé.")

            parts.append(f"<!-- Page {page_index + 1}/{doc.page_count} -->\n\n{page_md}")
    finally:
        doc.close()

    markdown = "\n\n".join(parts).strip() + "\n"
    return ConversionResult(markdown=markdown, warnings=warnings)


def _median_font_size(doc: "fitz.Document") -> float | None:
    sizes: list[float] = []
    for page_index in range(min(FONT_SAMPLE_PAGES, doc.page_count)):
        page = doc.load_page(page_index)
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["text"].strip():
                        sizes.append(round(span["size"], 1))
    return statistics.median(sizes) if sizes else None


def _page_to_markdown(page: "fitz.Page", body_size: float | None) -> str:
    page_dict = page.get_text("dict")
    blocks_out: list[str] = []

    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:  # 0 = texte, on ignore les images
            continue

        line_texts: list[str] = []
        max_size = 0.0
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(span["text"] for span in spans).strip()
            if not text:
                continue
            line_texts.append(text)
            max_size = max(max_size, max((span["size"] for span in spans), default=0.0))

        if not line_texts:
            continue

        text = " ".join(line_texts)
        blocks_out.append(_apply_heading(text, max_size, body_size))

    return "\n\n".join(blocks_out).strip()


def _apply_heading(text: str, max_size: float, body_size: float | None) -> str:
    if not body_size:
        return text
    for ratio, level in HEADING_RATIOS:
        if max_size >= body_size * ratio:
            return f"{'#' * level} {text}"
    return text


def _ocr_page(page: "fitz.Page", *, lang: str, zoom: float = 2.0) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix)
    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
    try:
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception:
        return ""
